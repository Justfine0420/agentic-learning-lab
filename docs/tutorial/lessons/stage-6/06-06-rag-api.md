# 第 6.6 课：RAG API

## 1. 本课目标

第 6.5 课已经能在函数层完成资料问答：

```text
question + vector store -> MaterialAnswer(answer, sources)
```

现在要把这条链路暴露成 FastAPI 接口，让外部调用方可以通过 HTTP 请求基于本地学习资料提问。

本课建立的接口是：

```text
POST /ask-materials
```

完成后，应能解释：

- 请求体为什么需要 `question` 和可选 `k`。
- 为什么响应模型直接使用 `MaterialAnswer`。
- 422、400 和 503 分别表示什么。
- 为什么 API 层不直接拼 prompt，也不直接操作 `Document`。
- 为什么当前仍不做 CLI 菜单、Agent 工具化、streaming 或 LangGraph。

## 2. 你会新增什么项目能力

`app/models.py` 新增请求模型：

```text
AskMaterialsRequest
```

`app/rag.py` 新增组合函数：

```text
answer_question_from_local_materials(question, k=3, ...)
```

`app/api.py` 新增接口：

```text
POST /ask-materials
```

接口数据流：

```text
HTTP request
-> AskMaterialsRequest
-> answer_question_from_local_materials()
-> load_local_materials()
-> split_material_documents()
-> build_ollama_embeddings()
-> build_material_vector_store()
-> answer_material_question()
-> MaterialAnswer
-> HTTP response
```

当前层保证：

- 缺少 `question` 或空字符串 `question` 返回 422。
- 纯空白 `question` 返回 400。
- 非法 `k` 返回 422。
- provider、embedding、模型输出或 RAG 结构化回答不可用时返回 503。
- 成功响应返回 `answer` 和 `sources`。
- 自动测试不会访问真实 Ollama 或云端 provider。

仍未新增：

- CLI 资料问答菜单。
- 缓存或持久化 vector store。
- 云端 embedding provider。
- Agent 自动调用 RAG 工具。
- chat history、多轮资料问答、streaming。
- LangGraph 状态机。

## 3. 前置知识

开始前，应已理解：

- FastAPI 如何用 Pydantic 模型描述请求体。
- `response_model` 如何定义响应结构。
- `HTTPException` 如何返回业务错误状态码。
- `MaterialAnswer` 为什么必须包含 `answer` 和 `sources`。
- 本地 Ollama embedding 配置与聊天模型 provider 配置是两套配置。

还不需要：

- 前端展示引用。
- 缓存向量索引。
- 将 RAG 问答纳入 Agent 规划。
- 设计 LangGraph node。

## 4. 核心概念

### API 层只负责 HTTP 契约

`POST /ask-materials` 不应该自己拼 prompt，也不应该自己遍历 Markdown 文件。API 层只做三件事：

```text
1. 校验 HTTP 请求
2. 调用 RAG 组合函数
3. 把业务异常转换成 HTTP 状态码
```

资料加载、切分、embedding、vector store 和回答生成继续留在 `app/rag.py`。这样后续 CLI、Agent 工具或 LangGraph node 也可以复用同一条 RAG 函数链路。

### 请求体需要保留 `k`

`k` 控制送入回答层的候选 chunk 数量：

```json
{
  "question": "Python 类型标注有什么用？",
  "k": 3
}
```

`k` 的默认值是 3，并限制在 1 到 10 之间。太小可能漏掉上下文，太大可能把无关内容塞进 prompt。当前限制是课程项目的安全边界，不是生产调参结论。

### 422、400 和 503 不是一回事

| 状态码 | 含义 | 示例 |
| --- | --- | --- |
| 422 | 请求体结构不符合 Pydantic 模型 | 缺少 `question`、`question=""`、`k=0` |
| 400 | 请求体结构合法，但业务上无效 | `question="   "` |
| 503 | RAG 能力当前不可用 | provider 未配置、Ollama 不可用、模型输出无效 |

这三类错误要分开。否则调用方无法判断是用户输入该修，还是服务端 AI 能力暂时不可用。

### 响应模型直接复用 `MaterialAnswer`

成功响应：

```json
{
  "answer": "类型标注能说明函数参数和返回值。",
  "sources": ["materials/stage-2.md"]
}
```

这里不额外包一层 `source="materials"`。RAG 问答的核心业务契约就是 `answer + sources`，保持接口直接，有利于后续前端和测试复用。

### 这个接口会临时重建内存索引

当前 `answer_question_from_local_materials()` 每次调用都会：

```text
读取 Markdown
-> 切分 chunk
-> 调用 embedding
-> 构建 InMemoryVectorStore
-> 检索并回答
```

这对课程里的小资料集足够清晰，也容易测试。生产系统如果资料变大，才需要缓存、增量索引或持久化 vector store。别在最小闭环还没跑稳时急着上数据库。

## 5. 代码实现

`app/models.py` 增加请求模型：

```python
class AskMaterialsRequest(BaseModel):
    question: str = Field(min_length=1, description="学员希望基于本地学习资料提出的问题")
    k: int = Field(default=3, ge=1, le=10, description="用于回答的候选资料片段数量")
```

`app/rag.py` 增加本地资料问答组合函数：

```python
def answer_question_from_local_materials(
    question: str,
    *,
    k: int = 3,
    materials_dir: Path = MATERIALS_DIR,
    embeddings: Embeddings | None = None,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
) -> MaterialAnswer:
    if question.strip() == "":
        raise ValueError("question must not be empty")
    if k < 1:
        raise ValueError("k must be greater than 0")

    documents = load_local_materials(materials_dir)
    chunks = split_material_documents(documents)
    if not chunks:
        return generate_material_answer(question, [], settings=settings, client=client)

    current_embeddings = embeddings or build_ollama_embeddings()
    vector_store = build_material_vector_store(chunks, current_embeddings)
    return answer_material_question(
        question,
        vector_store,
        settings=settings,
        client=client,
        k=k,
    )
```

这里保留了 `materials_dir`、`embeddings`、`settings` 和 `client` 参数，是为了测试和后续复用。API 默认不传这些参数，使用项目真实资料、本地 Ollama embedding 配置和当前聊天 provider 配置。

`app/api.py` 新增接口：

```python
@app.post(
    "/ask-materials",
    response_model=MaterialAnswer,
    responses={
        400: {"description": "问题不能为空。"},
        503: {"description": "RAG provider、向量检索或结构化资料回答不可用。"},
    },
)
def ask_materials(request: AskMaterialsRequest) -> MaterialAnswer:
    question = request.question.strip()
    if question == "":
        raise HTTPException(status_code=400, detail="问题不能为空。")

    try:
        return answer_question_from_local_materials(question, k=request.k)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (httpx.HTTPError, OpenAIError, OllamaRequestError, OllamaResponseError) as error:
        raise HTTPException(status_code=503, detail="AI provider request failed.") from error
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
```

测试策略：

- API 测试 monkeypatch `answer_question_from_local_materials()`，不触发真实 provider。
- RAG 测试用 `KeywordEmbeddings` 和 `FakeLLMClient` 验证组合函数。
- OpenAPI 测试确认 `200`、`400`、`422` 和 `503` 都被声明。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行 API 和 RAG 测试：

```powershell
py -3.13 -m pytest tests/test_api.py tests/test_rag.py
```

运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

请求示例：

```powershell
$body = @{
  question = "Python 类型标注有什么用？"
  k = 3
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/ask-materials" -ContentType "application/json" -Body $body
```

真实调用需要：

- 本地 Ollama 已启动。
- 已拉取可用于 embedding 的模型，例如 `mxbai-embed-large`。
- `.env` 中聊天模型 provider 可用。

自动测试不会运行真实 provider 调用。

## 7. 常见错误

### 在 API 里直接写 RAG 流水线细节

路由里散落加载、切分、建库和回答逻辑，会让后续 CLI、Agent 和 LangGraph 无法复用。组合函数应该留在 `app/rag.py`。

### 把空白问题当作 422

`question="   "` 在结构上是字符串，Pydantic 会通过。业务层要返回 400，告诉调用方问题内容为空。

### 把 provider 失败返回 500

provider 配置缺失、网络失败、Ollama 不可用或模型输出无效，都是“能力暂时不可用”，不是未处理的服务器崩溃。当前接口统一返回 503。

### 自动测试访问真实 Ollama

单元测试应验证接口契约和 RAG 组合边界，不应要求每台机器都已拉取 embedding 模型。真实模型调用放在手动验收里。

### 误以为 `InMemoryVectorStore` 已经持久化

当前接口每次请求重建内存索引。重启服务不会保留任何向量索引。需要性能优化时，再设计缓存或持久化。

### 继续把聊天模型当 embedding 模型

`OLLAMA_MODEL` 仍然是聊天模型配置，`OLLAMA_EMBEDDING_MODEL` 才是向量模型配置。API 接入没有改变这条边界。

## 8. 练习

练习 1：分别构造 `{}`、`{"question": ""}`、`{"question": "   "}`，解释为什么前两个是 422，最后一个是 400。

练习 2：把 `k` 改成 1 和 5，思考它会影响哪个 RAG 步骤。

练习 3：在测试中让 `answer_question_from_local_materials()` 抛出 `RuntimeError`，确认接口返回 503。

练习 4：说明为什么 `POST /ask-materials` 不应该直接调用 `build_ollama_embeddings()` 和 `build_material_vector_store()`。

练习 5：手动启动 API 后请求 `/docs`，检查 `POST /ask-materials` 的请求体、响应模型和错误状态码是否出现在 OpenAPI 页面。

## 9. 验收标准

完成后，应能做到：

- 定义 `AskMaterialsRequest(question, k)`。
- 新增 `answer_question_from_local_materials()` 组合本地 RAG 流水线。
- 新增 `POST /ask-materials`，成功时返回 `MaterialAnswer`。
- 缺失字段、空字符串、空白字符串和非法 `k` 有清晰错误状态码。
- provider、Ollama、网络或结构化回答失败时返回 503。
- OpenAPI 文档声明 `200`、`400`、`422` 和 `503`。
- API 自动测试不访问真实 provider。
- 运行 `py -3.13 -m pytest tests/test_api.py tests/test_rag.py` 和完整测试集通过。
- 运行 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| `POST /ask-materials` | 前端或外部调用方可以基于资料问答 |
| `answer_question_from_local_materials()` | 后续可以封装成 LangChain 只读工具 |
| 503 错误边界 | LangGraph 可以把失败变成重试、降级或人工确认分支 |
| `MaterialAnswer.sources` | 后续前端可以展示引用，Deep Agents 可以写入总结证据 |
| 每次请求重建索引 | 后续可演进为缓存、持久化向量库或增量更新 |

项目仍然只有一条真实代码主线：

```text
ai-learning-assistant/
```

没有创建代码副本。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-6/06-06-rag-api.md`

修改文件：

- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/rag.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_rag.py`
- `ai-learning-assistant/tests/test_api.py`
- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- 新增 `AskMaterialsRequest`。
- 新增 `answer_question_from_local_materials()`，组合本地资料加载、切分、向量索引和资料回答。
- 新增 `POST /ask-materials`。
- 新增 API 成功、请求校验、OpenAPI 和 503 错误映射测试。
- 新增本地 RAG 组合函数测试。

新增依赖：

- 无。

环境变量变更：

- 无。

官方文档核对：

- [FastAPI request body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI response model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)

下一步：阶段 6 复盘，检查 RAG 主线从概念、资料加载、切分、向量检索、资料回答到 API 是否闭环。
