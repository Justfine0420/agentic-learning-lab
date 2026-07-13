# 第 5.7 课：FastAPI 接入 LangChain Agent

## 1. 本课目标

第 5.6 课已经让 CLI 调用结构化 LangChain Agent：

```text
CLI 菜单
-> run_structured_learning_agent()
-> LangChain Agent
-> StructuredLearningSuggestion
```

这一课把同一个 Agent 能力接入 FastAPI，新增：

```http
POST /chat
```

客户端提交问题后，API 负责校验输入、调用结构化 Agent，并返回统一的结构化学习建议：

```text
POST /chat
-> ChatRequest
-> run_structured_learning_agent(question)
-> Agent 读取本地只读工具
-> StructuredLearningSuggestion
-> AgentChatResponse
```

你会学到：

- 为什么 API 路由应调用已有的 Agent 入口，而不是重写 Agent 创建逻辑。
- 如何用 Pydantic 区分请求和响应契约。
- 为什么 `/chat` 与 Stage 4 的 `/ai/suggestion` 应该并存。
- 如何把 provider、网络和结构化结果错误转换成明确的 HTTP 响应。
- 如何用 `TestClient` 测试 API，而不真的调用模型 provider。
- 为什么当前接口返回一次性结构化结果，而不是 streaming 事件。

## 2. 你会新增什么项目能力

完成后，FastAPI 会增加：

```http
POST /chat
Content-Type: application/json

{
  "question": "我今天应该先练什么？"
}
```

成功响应：

```json
{
  "source": "agent",
  "suggestion": {
    "summary": "今天用 FastAPI 调用结构化 Agent。",
    "suggestions": [
      {
        "title": "调用只读工具",
        "description": "让 Agent 读取当前学习档案和笔记。",
        "estimated_minutes": 25
      }
    ],
    "next_checkpoint": "能区分 /chat 和 /ai/suggestion。"
  }
}
```

这个接口会把问题传给：

```python
run_structured_learning_agent(question)
```

Agent 再按需调用已有的只读工具：

```text
read_current_student_profile
read_recent_learning_notes
build_current_rule_based_suggestion
```

工具读取的是项目共享的：

```text
data/student.json
```

## 3. 前置知识

开始前需要理解：

- Stage 3 已经建立 FastAPI route、Pydantic 请求体和 `HTTPException` 错误响应。
- Stage 4.5 已有 `POST /ai/suggestion`，它直接调用普通 LLM 封装。
- Stage 5.5 已有 `run_structured_learning_agent(question)`，并返回 `StructuredLearningSuggestion`。
- Stage 5.6 已证明 CLI 可以复用这个结构化 Agent 入口。
- 当前 Agent 工具全部是只读工具，学习状态仍保存于 JSON 文件。

本课涉及的已有函数是：

```python
def run_structured_learning_agent(
    question: str = DEFAULT_AGENT_QUESTION,
    *,
    settings: LLMSettings | None = None,
    agent: Any | None = None,
) -> StructuredLearningSuggestion:
    ...
```

因此 FastAPI 不需要了解 `create_agent()`、`ToolStrategy` 或 `@tool` / middleware 的装配细节。它只接收 HTTP 请求并调用稳定的 Python 函数。

## 4. 核心概念

### FastAPI 是入口层，Agent 是业务能力层

`app/api.py` 的职责是：

```text
读取 JSON 请求
校验输入
调用业务函数
返回 HTTP 响应
```

`app/langchain_agent.py` 的职责是：

```text
创建 Agent
声明工具和 middleware
调用模型
提取 structured_response
返回 StructuredLearningSuggestion
```

如果 API 路由直接写 `create_structured_learning_agent()`、再自己调用 `.invoke()`，CLI 和 API 会出现两条 Agent 调用链。以后增加 RAG 工具、调整 prompt 或修改结构化响应时，两个入口容易失去一致性。

所以路由只调用：

```python
run_structured_learning_agent(question)
```

### `/chat` 和 `/ai/suggestion` 的边界

两个接口都会返回结构化学习建议，但它们不是同一条能力路径。

| 接口 | 调用层 | 是否接收问题 | 数据来源 | `source` |
| --- | --- | --- | --- | --- |
| `POST /ai/suggestion` | Stage 4 普通 LLM 封装 | 否 | API 直接读取当前学员资料并组装 prompt | `ai` |
| `POST /chat` | Stage 5 LangChain Agent | 是 | Agent 根据问题调用多个只读工具 | `agent` |

保留旧接口有两个原因：

- 前面课程的代码与测试继续有效。
- 学习者可以比较“直接模型调用”和“Agent 工具调用”的职责边界。

`/chat` 出错时不会代替调用 `/ai/suggestion`，也不会返回规则建议。调用方需要明确知道这一次 Agent 请求是否成功。

### 请求模型和响应模型分别描述契约

请求模型：

```python
class ChatRequest(BaseModel):
    question: str = Field(min_length=1, description="学员希望向学习助教提出的问题")
```

它告诉 FastAPI：客户端必须传入至少一个字符的 `question`。

响应模型：

```python
class AgentChatResponse(BaseModel):
    source: str = "agent"
    suggestion: StructuredLearningSuggestion
```

它让调用方能识别 Agent 路径，同时复用已经验证过的 `StructuredLearningSuggestion`，不重复定义摘要、行动建议和检查点字段。

### 422、400 和 503 不表示同一种失败

| 情况 | 处理位置 | 状态码 | 示例 |
| --- | --- | --- | --- |
| `question` 缺失或空字符串 | Pydantic 请求模型 | 422 | `{}` 或 `{"question": ""}` |
| `question` 只有空白 | 路由业务校验 | 400 | `{"question": "   "}` |
| API key、网络、provider 或 Agent 结构化结果失败 | Agent 调用边界 | 503 | provider 未配置、连接失败、缺少 `structured_response` |

`Field(min_length=1)` 可以拒绝空字符串，但三个空格仍有长度。路由用：

```python
question = chat.question.strip()
if question == "":
    raise HTTPException(status_code=400, detail="问题不能为空。")
```

阻止无意义请求继续消耗模型调用。

### 503 表示 Agent 能力当前不可用

下列异常都表示这次请求没有得到可靠的 Agent 结果：

```python
RuntimeError
httpx.HTTPError
OpenAIError
ValueError
```

对应关系：

| 异常 | 常见来源 | API 响应 |
| --- | --- | --- |
| `RuntimeError` | 缺少 provider API key | `503`，保留配置错误详情 |
| `httpx.HTTPError` | provider 网络或 HTTP 请求失败 | `503`，返回 provider 请求失败 |
| `OpenAIError` | `ChatOpenAI` / OpenAI SDK 调用失败 | `503`，返回 provider 请求失败 |
| `ValueError` | Agent 没有可靠的结构化响应 | `503`，保留结构化结果错误详情 |

这和“返回一个看起来正常的规则建议”完全不同。前者让客户端可以重试、修正配置或提示用户；后者会掩盖 Agent 失败。

### 非 streaming 响应适合当前结构化结果

`/chat` 现在等待 Agent 完成工具调用和结构化输出，再一次性返回 JSON。这个边界让 `response_model`、错误语义和 API 测试保持清晰。

Streaming 需要同时定义 token 事件、工具调用事件、结束事件和最终结构化结果的传输协议。它会在后续 LangGraph streaming 阶段作为独立能力处理。

## 5. 代码实现

### 第一步：新增请求与响应模型

打开：

```text
ai-learning-assistant/app/models.py
```

在 `AISuggestionResponse` 后新增：

```python
class ChatRequest(BaseModel):
    question: str = Field(min_length=1, description="学员希望向学习助教提出的问题")


class AgentChatResponse(BaseModel):
    source: str = "agent"
    suggestion: StructuredLearningSuggestion
```

`ChatRequest` 只负责 HTTP 输入。`AgentChatResponse` 把已有的领域对象包装成 API 响应，不把 LangChain 的内部 state 暴露给客户端。

### 第二步：导入 Agent 入口与异常类型

打开：

```text
ai-learning-assistant/app/api.py
```

补充导入：

```python
import httpx
from fastapi import FastAPI, HTTPException
from openai import OpenAIError

from app.langchain_agent import run_structured_learning_agent
from app.models import AgentChatResponse, ChatRequest
```

项目已经通过 `langchain-openai` 安装 OpenAI SDK，所以可以使用 `OpenAIError` 表示 SDK 层 provider 错误。

### 第三步：新增 `POST /chat`

在 `POST /ai/suggestion` 后新增：

```python
@app.post(
    "/chat",
    response_model=AgentChatResponse,
    responses={
        400: {"description": "问题不能为空。"},
        503: {"description": "Agent provider 或结构化结果不可用。"},
    },
)
def chat_with_learning_agent(chat: ChatRequest) -> AgentChatResponse:
    question = chat.question.strip()
    if question == "":
        raise HTTPException(status_code=400, detail="问题不能为空。")

    try:
        suggestion = run_structured_learning_agent(question)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (httpx.HTTPError, OpenAIError) as error:
        raise HTTPException(status_code=503, detail="AI provider request failed.") from error
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return AgentChatResponse(suggestion=suggestion)
```

调用链保持很短：

```text
chat_with_learning_agent()
-> run_structured_learning_agent(question)
-> Agent tools + model
-> StructuredLearningSuggestion
```

路由没有直接读取 `data/student.json`。这是 Agent 工具的职责，确保 CLI 和 FastAPI 调用的是同一套工具路径。

`responses` 会把 `400` 和 `503` 登记到 OpenAPI 文档中。运行时错误和 Swagger 展示的契约需要一致，不能只让调用过测试的人知道失败语义。

### 第四步：为成功路径添加 API 测试

打开：

```text
ai-learning-assistant/tests/test_api.py
```

测试不调用真实 provider，而是替换 API 模块里导入的函数：

```python
def fake_run_structured_learning_agent(question: str) -> StructuredLearningSuggestion:
    assert question == "我今天应该先练什么？"
    return suggestion


monkeypatch.setattr(
    api,
    "run_structured_learning_agent",
    fake_run_structured_learning_agent,
)

response = client.post("/chat", json={"question": "我今天应该先练什么？"})

assert response.status_code == 200
assert response.json()["source"] == "agent"
assert response.json()["suggestion"]["summary"] == "今天用 FastAPI 调用结构化 Agent。"
```

这个测试验证的是 HTTP 请求、问题传递、响应模型和 JSON 结构，不是 provider 的联网情况。

### 第五步：测试输入边界

继续增加：

```python
empty_response = client.post("/chat", json={"question": ""})
blank_response = client.post("/chat", json={"question": "   "})

assert empty_response.status_code == 422
assert blank_response.status_code == 400
assert blank_response.json() == {"detail": "问题不能为空。"}
```

还要替换 `run_structured_learning_agent` 为会抛出 `AssertionError` 的函数。这样能证明无效输入在 API 边界被拦住，没有执行 Agent。

### 第六步：测试 Agent 失败

使用参数化测试覆盖四种失败：

```python
@pytest.mark.parametrize(
    ("agent_error", "expected_detail"),
    [
        (RuntimeError("Missing required environment variable: DEEPSEEK_API_KEY."), "Missing required environment variable: DEEPSEEK_API_KEY."),
        (httpx.ConnectError("network failed"), "AI provider request failed."),
        (OpenAIError("provider failed"), "AI provider request failed."),
        (ValueError("LangChain agent result did not contain structured_response."), "LangChain agent result did not contain structured_response."),
    ],
)
def test_post_chat_returns_503_for_agent_errors(monkeypatch, agent_error, expected_detail) -> None:
    ...
```

这组测试确保 Agent 出错时 API 不会返回 `200`，也不会偷偷改走规则建议。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

先运行 API 定向测试：

```powershell
py -3.13 -m pytest tests/test_api.py
```

再运行全量测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

启动服务：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

另开一个 PowerShell 窗口，发送请求：

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/chat `
  -ContentType 'application/json' `
  -Body '{"question":"我今天应该先练什么？"}'
```

这条人工调用需要本地 `.env` 中的 provider 配置有效，并且模型支持当前 Agent 工具调用和结构化输出。

也可以打开：

```text
http://127.0.0.1:8000/docs
```

在 Swagger UI 中找到 `POST /chat`。

## 7. 常见错误

### API 路由重新创建 Agent

错误方向：

```python
agent = create_structured_learning_agent()
result = agent.invoke(...)
```

这样会绕开 `run_structured_learning_agent()`，把 Agent 调用逻辑复制到入口层。

正确方向：

```python
suggestion = run_structured_learning_agent(question)
```

### 把 `/chat` 写成普通 LLM 调用

错误方向：

```python
generate_structured_learning_suggestion(student)
```

这个函数属于 Stage 4 的直接模型调用路径。它不会让 Agent 决定是否读取档案、笔记和离线规则建议。

### 只校验 `min_length=1`

下面的请求长度大于 0：

```json
{
  "question": "   "
}
```

所以还需要：

```python
if chat.question.strip() == "":
```

### 把错误 JSON 当作成功响应

错误方向：

```python
return {"error": "AI provider request failed."}
```

如果不显式设置状态码，调用方可能收到 `200`。

正确方向：

```python
raise HTTPException(status_code=503, detail="AI provider request failed.")
```

### Agent 失败时自动返回规则建议

规则建议是一个独立能力，不是 Agent 失败时的隐藏替身。

`POST /chat` 返回 `503` 后，调用方可以决定提示用户、稍后重试，或者显式请求 `GET /suggestion`。

### 期待 `/chat` 输出过程事件

当前响应只在 Agent 完成后返回最终 JSON。不会发送 token、工具调用过程或中间消息。

## 8. 练习

练习 1：把 `question` 改成 `message`，同步修改 `ChatRequest`、路由、测试和接口调用，观察 Swagger 文档如何变化。

练习 2：为缺失 `question` 的请求补充一条断言，确认 FastAPI 返回 `422`。

练习 3：在测试里让 `run_structured_learning_agent()` 抛出 `OpenAIError`，解释为什么 API 返回 `503` 而不是 `500`。

练习 4：比较：

```http
POST /ai/suggestion
POST /chat
```

列出两者的请求体、调用函数、数据读取方式和 `source` 字段差异。

练习 5：运行 `POST /chat` 前先调用 `POST /notes` 添加一条笔记。思考 Agent 为什么能在工具调用时看到这条笔记。

## 9. 验收标准

完成后，应满足：

- 存在 `ChatRequest` 和 `AgentChatResponse`。
- 存在 `POST /chat`。
- `/chat` 把问题传给 `run_structured_learning_agent(question)`。
- 成功响应的 `source` 是 `agent`。
- 成功响应的 `suggestion` 符合 `StructuredLearningSuggestion`。
- 空字符串请求返回 `422`。
- 只有空白的请求返回 `400`，且不会调用 Agent。
- provider 配置、网络、OpenAI SDK 与结构化响应错误都返回 `503`。
- OpenAPI 文档声明 `200`、`400`、`422` 和 `503`。
- `/chat` 不静默改用规则建议或 `/ai/suggestion`。
- 既有 `POST /ai/suggestion`、`GET /suggestion` 和 CLI Agent 路径不退化。
- `py -3.13 -m pytest tests/test_api.py` 通过。
- `py -3.13 -m pytest` 通过。
- 语法检查通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

现在 CLI 和 FastAPI 都复用：

```python
run_structured_learning_agent(question)
```

后续能力会在这条稳定入口附近扩展：

| 当前内容 | 后续升级 |
| --- | --- |
| `/chat` 传入学习问题 | RAG 阶段增加资料检索工具，回答可引用本地资料 |
| 只读 JSON 工具 | 数据库阶段可替换为 Repository 或持久化存储 |
| 一次性结构化响应 | LangGraph streaming 阶段定义过程事件与状态传输 |
| `503` 表示 Agent 不可用 | LangGraph 可为失败、重试和人工确认定义分支 |
| 单次 Agent 调用 | Deep Agents 可把复杂学习任务拆成计划、研究和总结步骤 |

`/chat` 现在是单次 Agent 请求，不保存聊天历史，也不包含 RAG、写工具或 streaming。这些边界让 Stage 5 的重点保持在“通过 HTTP 调用结构化工具型 Agent”。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-5/05-07-fastapi-agent-integration.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_api.py`

新增 API：

```http
POST /chat
```

新增模型：

```python
ChatRequest
AgentChatResponse
```

新增错误响应：

```text
422 请求体缺失或 question 为空
400 question 只有空白
503 Agent provider 或结构化结果不可用
```

依赖变更：

- 无。

环境变量变更：

- 无，继续使用 Stage 4 已配置的 provider 环境变量。

官方文档：

- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [LangChain Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output)

下一步：

- 生成阶段 5 复盘，整理 LangChain Agent、只读工具、结构化输出、CLI 与 FastAPI 两个入口的能力边界。
- 阶段 6 将开始 RAG：先解释文档、chunk、embedding 与 retriever 的关系。
