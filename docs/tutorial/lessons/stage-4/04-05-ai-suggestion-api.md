# 第 4.5 课：AI 建议 API、CLI 入口与降级边界

## 1. 本课目标

第 4.3 课已经能调用真实模型生成普通文本建议。
第 4.4 课已经能把模型的业务内容校验成结构化学习建议。

但目前这些能力还停在：

```text
app/llm.py
app/llm_demo.py
app/structured_llm_demo.py
```

本课要把结构化 AI 建议接入 FastAPI 和 CLI：

```text
POST /ai/suggestion
CLI 选项 4：生成 AI 学习建议
```

你要学会：

- 为什么不直接改掉已有 `GET /suggestion`。
- 为什么 AI 接口应该和规则接口分开。
- 如何把结构化 LLM 调用接入 FastAPI route。
- 如何让 CLI 复用同一个 AI 建议核心函数。
- 为什么 CLI 不需要通过 HTTP 调用自己本地的 API。
- 如何把 provider 不可用、网络失败、模型输出错误转换成 API 错误。
- 为什么本课用 `503 Service Unavailable`。
- 为什么“降级”不等于在服务端偷偷返回规则建议。

本课完成后，项目会同时拥有两个 API 建议接口和一个 CLI AI 建议入口：

```text
GET  /suggestion     -> 规则建议，稳定、离线可用
POST /ai/suggestion  -> AI 建议，需要 provider 可用
CLI 5                -> AI 建议，直接复用 LLM 业务函数
```

## 2. 你会新增什么项目能力

本课会更新：

```text
app/models.py
app/api.py
app/cli.py
tests/test_api.py
tests/test_cli.py
```

新增响应模型：

```python
class AISuggestionResponse(BaseModel):
    source: str = "ai"
    suggestion: StructuredLearningSuggestion
```

新增 API：

```text
POST /ai/suggestion
```

新增 CLI 菜单：

```text
4. 生成 AI 学习建议
```

原来的菜单编号保持不变：

```text
3. 查看离线规则建议   -> 规则建议
4. 生成 AI 学习建议   -> AI 建议
5. 退出
```

成功时返回：

```json
{
  "source": "ai",
  "suggestion": {
    "summary": "今天先复习 FastAPI 和 Pydantic。",
    "suggestions": [
      {
        "title": "复习接口边界",
        "description": "区分规则建议接口和 AI 建议接口。",
        "estimated_minutes": 20
      }
    ],
    "next_checkpoint": "能说明 provider 不可用时为什么返回 503。"
  }
}
```

失败时返回：

```json
{
  "detail": "AI provider request failed."
}
```

或者：

```json
{
  "detail": "Missing required environment variable: DEEPSEEK_API_KEY."
}
```

## 3. 前置知识

开始前，你应该已经理解：

- `GET /suggestion` 是规则建议接口，不依赖模型。
- `generate_structured_learning_suggestion()` 会调用 provider 并返回 Pydantic 对象。
- FastAPI 可以用 `response_model` 定义响应结构。
- FastAPI 可以用 `HTTPException` 返回错误状态码。
- CLI 可以直接复用业务函数，不一定要通过 HTTP 请求本地 API。
- provider 调用可能失败，模型输出也可能不符合 schema。

本课会用到三个错误边界：

```python
RuntimeError
httpx.HTTPError
ValueError
```

含义：

| 错误 | 常见原因 | API 状态 |
| --- | --- | --- |
| `RuntimeError` | 缺少 API Key | `503` |
| `httpx.HTTPError` | 网络失败、provider 返回错误 | `503` |
| `ValueError` | 模型输出无法通过结构化校验 | `503` |

## 4. 核心概念

### 不要直接替换 `GET /suggestion`

当前已有接口：

```text
GET /suggestion
```

它的特点是：

- 不访问外网。
- 不需要 API Key。
- 不产生费用。
- 不受 provider 状态影响。
- 已经有测试覆盖。

如果直接把它改成 AI 调用，学习者只要没配 `.env` 或 Ollama 没启动，就会发现原本稳定的 API 突然不可用。

这不是升级，这是破坏兼容性。

所以本课新增：

```text
POST /ai/suggestion
```

而不是改掉：

```text
GET /suggestion
```

### 降级边界

“降级”不是服务端偷偷做决定。

一种糟糕实现是：

```text
POST /ai/suggestion
-> AI 失败
-> 服务端偷偷返回规则建议
-> HTTP 200
```

这会让调用方以为拿到了 AI 结果。
但实际只是规则结果。

本课的设计是：

```text
POST /ai/suggestion
-> AI 失败
-> HTTP 503
-> detail 说明原因
```

调用方如果想降级，可以自己调用：

```text
GET /suggestion
```

这样边界清楚：

| 接口 | 责任 |
| --- | --- |
| `GET /suggestion` | 稳定规则建议 |
| `POST /ai/suggestion` | AI 结构化建议 |
| 客户端或后续业务层 | 决定是否从 AI 降级到规则 |

### API 和 CLI 复用同一个业务函数

`POST /ai/suggestion` 是 HTTP 入口。
CLI 菜单是命令行入口。

这两个入口不应该各写一套模型调用逻辑。

本课的共用核心是：

```text
generate_structured_learning_suggestion(student)
```

所以最终结构是：

```text
FastAPI route
-> load_student()
-> generate_structured_learning_suggestion(student)
-> AISuggestionResponse

CLI 选项 4
-> 当前 student
-> generate_structured_learning_suggestion(student)
-> 打印结构化建议
```

注意，CLI 不需要这样做：

```text
CLI
-> HTTP POST http://127.0.0.1:8000/ai/suggestion
```

否则每次使用 CLI AI 建议前，都必须先启动 `uvicorn`。
这会把命令行工具变成 API 服务的客户端，反而增加学习者的运行负担。

### 为什么是 503

AI provider 不可用不是请求体错。
本课的 `POST /ai/suggestion` 没有请求体。

这些问题都属于服务端依赖暂不可用：

- API Key 没配置。
- provider 网络请求失败。
- provider 返回错误。
- 模型返回内容无法被当前 schema 接受。

所以用：

```text
503 Service Unavailable
```

比 `400` 更合适。

### API 响应模型

本课新增：

```python
class AISuggestionResponse(BaseModel):
    source: str = "ai"
    suggestion: StructuredLearningSuggestion
```

`source` 的作用是让调用方知道：

```text
这是 AI 建议。
```

如果后续要做统一接口，也可以返回：

```json
{"source": "rule", "...": "..."}
```

但本课不做统一接口。
先把两个接口边界讲清楚。

## 5. 代码实现

### 第一步：新增响应模型

打开：

```text
ai-learning-assistant/app/models.py
```

在 `StructuredLearningSuggestion` 后面新增：

```python
class AISuggestionResponse(BaseModel):
    source: str = "ai"
    suggestion: StructuredLearningSuggestion
```

注意，它复用了第 4.4 课的业务输出模型。

它不是 provider 响应外壳。
它是我们自己的 API 响应结构。

### 第二步：导入 LLM 函数和错误类型

打开：

```text
ai-learning-assistant/app/api.py
```

新增导入：

```python
import httpx
from fastapi import FastAPI, HTTPException

from app.llm import generate_structured_learning_suggestion
```

同时从 `app.models` 导入：

```python
AISuggestionResponse
```

`httpx.HTTPError` 是 HTTPX 的通用错误父类。
网络错误和 HTTP 状态错误都可以归到这一层处理。

### 第三步：新增 `POST /ai/suggestion`

在 `GET /suggestion` 后面新增：

```python
@app.post("/ai/suggestion", response_model=AISuggestionResponse)
def generate_ai_suggestion() -> AISuggestionResponse:
    student = load_student()

    try:
        suggestion = generate_structured_learning_suggestion(student)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=503, detail="AI provider request failed.") from error
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return AISuggestionResponse(suggestion=suggestion)
```

它的流程是：

```text
load_student()
-> generate_structured_learning_suggestion(student)
-> AISuggestionResponse(source="ai", suggestion=...)
```

如果失败：

```text
RuntimeError / httpx.HTTPError / ValueError
-> HTTPException(503)
```

### 第四步：补充成功测试

打开：

```text
ai-learning-assistant/tests/test_api.py
```

新增测试：

```python
def test_post_ai_suggestion_returns_structured_result(...):
    ...
```

测试用 `monkeypatch` 替换：

```python
api.generate_structured_learning_suggestion
```

这样测试不会访问真实 provider。

测试要确认：

- `POST /ai/suggestion` 返回 200。
- 响应里有 `source: "ai"`。
- 响应里有结构化 `summary`、`suggestions` 和 `next_checkpoint`。
- API 没有修改 `data/student.json`。

### 第五步：补充失败测试

本课至少测两个失败场景：

```text
缺少 provider 配置 -> 503
模型输出不符合 schema -> 503
```

对应测试：

```python
def test_post_ai_suggestion_returns_503_when_provider_config_missing(...):
    ...
```

以及：

```python
def test_post_ai_suggestion_returns_503_when_model_output_is_invalid(...):
    ...
```

这些测试的重点不是 provider 本身。
重点是 API 边界：

```text
AI 失败时，不伪装成成功。
```

### 第六步：给 CLI 新增 AI 建议入口

打开：

```text
ai-learning-assistant/app/cli.py
```

新增导入：

```python
import httpx

from app.llm import generate_structured_learning_suggestion
from app.models import StructuredLearningSuggestion
```

新增格式化函数：

```python
def format_ai_suggestion(suggestion: StructuredLearningSuggestion) -> list[str]:
    lines = [
        "=== AI 学习建议 ===",
        f"摘要：{suggestion.summary}",
        "",
        "行动建议：",
    ]

    for index, item in enumerate(suggestion.suggestions, start=1):
        lines.append(f"{index}. {item.title}（约 {item.estimated_minutes} 分钟）")
        lines.append(f"   {item.description}")

    lines.extend(["", f"下一检查点：{suggestion.next_checkpoint}"])
    return lines
```

再新增 CLI AI 建议函数：

```python
def suggest_with_ai() -> None:
    print()

    try:
        suggestion = generate_structured_learning_suggestion(student)
    except RuntimeError as error:
        print("AI 建议暂不可用。")
        print(f"原因：{error}")
        print("你可以先使用选项 3 获取离线规则建议。")
    except httpx.HTTPError:
        print("AI 建议暂不可用。")
        print("原因：AI provider 请求失败。")
        print("你可以先使用选项 3 获取离线规则建议。")
    except ValueError as error:
        print("AI 建议暂不可用。")
        print(f"原因：{error}")
        print("你可以先使用选项 3 获取离线规则建议。")
    else:
        for line in format_ai_suggestion(suggestion):
            print(line)
```

最后在菜单中保留旧编号，并追加新选项：

```python
print("3. 查看离线规则建议")
print("4. 生成 AI 学习建议")
print("5. 退出")
```

对应分支：

```python
elif choice == "5":
    suggest_with_ai()
```

这样做有两个好处：

- 旧课程里输入 `3` 和 `4` 的脚本仍然可用。
- CLI 和 API 共享模型调用能力，但不要求 CLI 依赖本地 API 服务。

### 第七步：补充 CLI 测试

新建：

```text
ai-learning-assistant/tests/test_cli.py
```

测试重点：

- `format_ai_suggestion()` 能把结构化模型转成人能读的 CLI 文本。
- `suggest_with_ai()` 成功时会打印摘要、行动建议和下一检查点。
- provider 请求失败时，CLI 会明确提示 AI 不可用，并提醒可以使用规则建议。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

运行测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py
```

如果你要检查 CLI 菜单：

```powershell
py -3.13 -m app.main
```

菜单中会出现：

```text
4. 生成 AI 学习建议
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

规则建议：

```text
GET http://127.0.0.1:8000/suggestion
```

AI 建议：

```text
POST http://127.0.0.1:8000/ai/suggestion
```

如果 provider 配置不可用，`POST /ai/suggestion` 会返回 `503`。
这时你仍然可以调用 `GET /suggestion` 获取规则建议。
CLI 中也一样：如果 AI 建议不可用，可以先使用选项 `3` 获取离线规则建议。

## 7. 常见错误

### 把 AI 失败包装成 200

不要这样做：

```text
AI 失败 -> 返回规则建议 -> HTTP 200
```

这会隐藏真实问题。

### 在单元测试里访问真实 provider

API 测试里必须用 `monkeypatch`。

真实 provider 适合手动验收：

```powershell
py -3.13 -m app.structured_llm_demo
```

或启动 API 后手动请求：

```text
POST /ai/suggestion
```

### 把所有错误都写成 500

`500` 表示服务端内部错误。

provider 不可用、网络失败、模型输出不合 schema，更像外部依赖暂不可用。
本课统一用 `503`。

后续如果做更细粒度错误模型，可以再扩展。

### 修改已有 `GET /suggestion`

不要破坏已经稳定的接口。

本课只新增 API：

```text
POST /ai/suggestion
```

同时新增 CLI 入口：

```text
4. 生成 AI 学习建议
```

### 让 CLI 通过 HTTP 调本地 API

不要在 CLI 里直接写：

```python
requests.post("http://127.0.0.1:8000/ai/suggestion")
```

这会要求学习者先启动 API 服务，CLI 才能生成 AI 建议。

本课采用的做法是：

```text
CLI 和 API 共享 generate_structured_learning_suggestion()
```

HTTP route 只是对外服务边界，不是项目内部唯一调用方式。

## 8. 练习

练习 1：解释为什么 `GET /suggestion` 不应该直接改成 AI 调用。

练习 2：解释 `POST /ai/suggestion` 为什么使用 `POST`，而不是 `GET`。

练习 3：把 `generate_structured_learning_suggestion()` 的 monkeypatch 改成抛出 `RuntimeError`，观察 API 为什么返回 `503`。

练习 4：解释“服务端偷偷降级成规则建议”有什么问题。

练习 5：启动 API，在 provider 可用时手动请求 `POST /ai/suggestion`。

练习 6：运行 CLI，选择 `4`，观察 provider 可用和不可用时分别会打印什么。

## 9. 验收标准

完成本课后，你应该能做到：

- 解释规则建议接口和 AI 建议接口的区别。
- 解释为什么 `POST /ai/suggestion` 不破坏 `GET /suggestion`。
- 解释为什么 CLI AI 建议不需要 HTTP 调本地 API。
- 解释为什么 provider 不可用时返回 `503`。
- 看懂 `AISuggestionResponse`。
- 看懂 `generate_ai_suggestion()` 的错误处理。
- 看懂 `suggest_with_ai()` 的错误处理。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。
- 知道真实 provider 调用仍然需要 `.env` 或 Ollama 环境。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课是 Stage 4 到 Stage 5 的过渡。

| 本课内容 | 后续升级 |
| --- | --- |
| `POST /ai/suggestion` | LangChain Agent API |
| CLI AI 建议入口 | 终端版 Agent 交互入口 |
| `AISuggestionResponse` | Agent 结构化响应 |
| `503` provider 边界 | Agent 错误和降级策略 |
| 规则接口与 AI 接口分离 | 多 Agent / 多能力路由 |

Stage 5 进入 LangChain 后，模型调用会从手写 `llm.py` 逐步升级为 LangChain model 和 agent。

但 API 边界不会消失。
无论底层是手写 HTTP、LangChain、LangGraph 还是 Deep Agents，外部接口都必须清楚表达：

```text
成功返回什么
失败返回什么
调用方如何降级
```

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-4/04-05-ai-suggestion-api.md`

修改文件：

- `README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/tests/test_api.py`
- `ai-learning-assistant/tests/test_cli.py`
- `docs/tutorial/README.md`

代码变更：

- 新增 `AISuggestionResponse`。
- 新增 `POST /ai/suggestion`。
- 新增 CLI 选项 `4. 生成 AI 学习建议`。
- 新增 AI 建议 API 成功测试。
- 新增 provider 配置缺失时的 `503` 测试。
- 新增 provider 请求失败时的 `503` 测试。
- 新增模型输出无效时的 `503` 测试。
- 新增 CLI AI 建议格式化测试和 provider 失败提示测试。

新增依赖：

- 无。

环境变量变更：

- 无。继续复用第 4.2 课的 provider 配置。

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py
```

下一步：

- 生成阶段 4 复盘，总结 LLM 基础、provider 配置、模型调用、结构化输出和 AI API 边界。
