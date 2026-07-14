# 第 6.5 课：基于资料回答

## 1. 本课目标

第 6.4 课已经能从本地学习资料中检索最相关的 chunk。现在要把这些 chunk 交给聊天模型，生成一个可展示给学习者的回答，并带上引用来源。

这一课建立 RAG 回答层：

```text
query
-> retrieve_material_chunks()
-> context Document[]
-> chat model
-> MaterialAnswer(answer, sources)
```

完成后，应能解释：

- 为什么“检索到资料”不等于“可以随便回答”。
- 为什么回答结果必须是结构化对象，而不是一段裸字符串。
- 为什么 `sources` 必须来自检索到的 `Document.metadata["source"]`。
- 资料为空时为什么直接返回资料不足，而不是继续调用模型。
- 为什么当前还不新增 `POST /ask-materials`。

## 2. 你会新增什么项目能力

`app/models.py` 新增：

```text
MaterialAnswer
```

`app/rag.py` 新增回答生成函数：

```text
build_material_answer_messages(question, documents)
parse_material_answer(content, allowed_sources)
generate_material_answer(question, documents, settings=None, client=None)
answer_material_question(question, vector_store, settings=None, client=None, k=3)
```

它们的职责是：

| 函数 | 输入 | 输出 |
| --- | --- | --- |
| `build_material_answer_messages` | 用户问题、检索到的 `Document` | chat messages |
| `parse_material_answer` | 模型返回文本、允许引用的 source 列表 | `MaterialAnswer` |
| `generate_material_answer` | 用户问题、资料 chunk、可选模型配置和 client | 带来源的回答 |
| `answer_material_question` | 用户问题、vector store、可选模型配置和 client | 检索后回答 |

当前层保证：

- 空白问题会在调用模型前失败。
- 无资料 chunk 时返回固定的资料不足回答，不调用模型。
- prompt 只包含检索到的资料片段和允许引用的 sources。
- 模型必须返回 JSON object，并按 `MaterialAnswer` 校验。
- 模型引用了未检索到的 source 时会失败。
- 有资料且模型给出实质回答时，必须至少引用一个允许的 source。

仍未新增：

- `POST /ask-materials` API。
- CLI 资料问答菜单。
- chat history、多轮 RAG、streaming。
- reranker、分数阈值或持久化向量库。
- 把 RAG 检索注册成 LangChain Agent 工具。
- LangGraph 工作流。

## 3. 前置知识

开始前，应已理解：

- `Document.page_content` 保存 chunk 文本。
- `Document.metadata["source"]` 保存稳定来源路径。
- `retrieve_material_chunks(query, vector_store, k=3)` 返回相关 chunk。
- `call_chat_completion()` 是项目已有的 OpenAI-compatible 聊天模型调用封装。
- Pydantic 模型可以把模型返回的 JSON 校验成业务对象。

还不需要：

- 设计公开 RAG API。
- 处理前端引用展示。
- 持久化向量索引。
- 让 Agent 自动决定是否调用 RAG。

## 4. 核心概念

### RAG 回答要先承认证据边界

RAG 的关键不是“让模型更会说”，而是限制模型只能依据给定资料说。检索结果就是回答层的证据边界：

```text
允许回答的内容 = 检索到的 chunk
允许引用的 sources = 检索到的 Document.metadata["source"]
```

如果资料里没有足够依据，系统应返回：

```text
当前资料中没有找到足够依据回答这个问题。
```

这比编一个看似合理的答案更可靠。课程项目宁可说不知道，也不把资料外知识伪装成学习资料结论。

### `answer + sources` 是业务契约

裸字符串回答无法稳定展示引用，也无法判断模型有没有越界。项目新增 `MaterialAnswer`：

```python
class MaterialAnswer(BaseModel):
    answer: str = Field(min_length=1, description="基于学习资料生成的回答")
    sources: list[str] = Field(default_factory=list, description="回答引用的资料来源路径")
```

回答层只接受这类结构：

```json
{
  "answer": "类型标注写在函数参数和返回值上。",
  "sources": ["materials/stage-2.md"]
}
```

后续 API 和前端展示可以直接复用这个契约。

### prompt 不是安全边界，解析校验才是最后一道门

prompt 会告诉模型：

- 只能基于资料片段回答。
- 只能引用允许的 sources。
- 资料不足时 sources 必须为空数组。
- 只返回 JSON 对象。

但模型可能仍然返回坏结果。因此代码还会做确定性校验：

- 不是 JSON：拒绝。
- 不符合 `MaterialAnswer`：拒绝。
- 引用了未知 source：拒绝。
- 有资料、有实质回答、却没有 source：拒绝。

这些规则应该写在代码和测试里，而不是寄希望于模型听话。

### 无资料时不调用模型

当检索结果为空时，模型没有证据上下文。继续调用模型只会增加幻觉风险和网络成本。

所以 `generate_material_answer()` 会直接返回：

```python
MaterialAnswer(
    answer="当前资料中没有找到足够依据回答这个问题。",
    sources=[],
)
```

测试会验证 fake client 没有收到请求。

### 6.5 不是 API 课

当前代码已经可以从函数层完成：

```text
question + vector_store -> MaterialAnswer
```

但是 HTTP 请求体、错误码、OpenAPI 响应模型、provider 不可用处理和端到端 API 测试，属于第 6.6 课。现在提前做 API，只会把阶段边界搅乱。

## 5. 代码实现

`app/models.py` 增加结构化回答模型：

```python
class MaterialAnswer(BaseModel):
    answer: str = Field(min_length=1, description="基于学习资料生成的回答")
    sources: list[str] = Field(default_factory=list, description="回答引用的资料来源路径")
```

`app/rag.py` 定义固定的资料不足回答：

```python
MATERIAL_ANSWER_UNAVAILABLE = "当前资料中没有找到足够依据回答这个问题。"
```

从 `Document` 中提取来源：

```python
def get_material_source(document: Document) -> str:
    source = document.metadata.get("source")
    if not isinstance(source, str) or source.strip() == "":
        raise ValueError("Material document is missing source metadata.")
    return source.strip()
```

构造发送给聊天模型的消息：

```python
def build_material_answer_messages(
    question: str,
    documents: list[Document],
) -> list[dict[str, str]]:
    if question.strip() == "":
        raise ValueError("question must not be empty")

    schema = json.dumps(MaterialAnswer.model_json_schema(), ensure_ascii=False, indent=2)
    sources = extract_material_sources(documents)
    source_lines = "\n".join(f"- {source}" for source in sources) or "- 无"
```

这里会把资料片段、允许引用的 source 列表、问题和 JSON schema 放进 user message。system message 只负责角色和回答边界。

解析模型返回时做白名单校验：

```python
def parse_material_answer(content: str, allowed_sources: list[str]) -> MaterialAnswer:
    try:
        result = MaterialAnswer.model_validate_json(content)
    except ValueError as error:
        raise ValueError("LLM response was not a valid material answer.") from error

    allowed_source_set = set(allowed_sources)
    deduped_sources: list[str] = []
    seen: set[str] = set()
    for source in result.sources:
        if source not in allowed_source_set:
            raise ValueError("Material answer cited an unknown source.")
        if source not in seen:
            deduped_sources.append(source)
            seen.add(source)
```

生成回答：

```python
def generate_material_answer(
    question: str,
    documents: list[Document],
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
) -> MaterialAnswer:
    if question.strip() == "":
        raise ValueError("question must not be empty")
    if not documents:
        return MaterialAnswer(answer=MATERIAL_ANSWER_UNAVAILABLE, sources=[])

    messages = build_material_answer_messages(question, documents)
    content = call_chat_completion(
        messages,
        settings=settings,
        client=client,
        response_format={"type": "json_object"},
    )
    return parse_material_answer(content, allowed_sources=extract_material_sources(documents))
```

检索并回答：

```python
def answer_material_question(
    question: str,
    vector_store: InMemoryVectorStore,
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
    k: int = 3,
) -> MaterialAnswer:
    chunks = retrieve_material_chunks(question, vector_store, k=k)
    return generate_material_answer(question, chunks, settings=settings, client=client)
```

测试继续使用 deterministic test double：

- `KeywordEmbeddings` 控制检索命中。
- `FakeLLMClient` 控制聊天模型返回。
- 不访问真实 API Key。
- 不访问真实 Ollama 服务。

这样可以稳定验证 RAG 回答层的业务边界，而不是把单元测试变成网络集成测试。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行 RAG 和 LLM 相关单元测试：

```powershell
py -3.13 -m pytest tests/test_rag.py tests/test_llm.py
```

运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

如果你要手动跑真实 RAG 回答，需要同时满足：

- 本地 Ollama 已启动。
- 已拉取 embedding 模型，例如 `mxbai-embed-large`。
- `.env` 中聊天模型 provider 可用。

示例：

```powershell
py -3.13 -c "from app.rag import load_local_materials, split_material_documents, build_ollama_embeddings, build_material_vector_store, answer_material_question; docs=split_material_documents(load_local_materials()); store=build_material_vector_store(docs, build_ollama_embeddings()); print(answer_material_question('Python 类型标注有什么用？', store).model_dump())"
```

自动测试不会运行这条真实模型命令。

## 7. 常见错误

### 让模型自己决定 sources

`sources` 只能来自检索到的 `Document.metadata["source"]`。模型返回任何其他路径，都必须视为幻觉来源。

### 没有资料也调用模型

没有资料上下文时，模型无法给出 grounded answer。直接返回资料不足，比让模型自由发挥更符合 RAG 的目的。

### 只在 prompt 里写“不要编造”

prompt 是软约束。白名单校验、JSON schema 校验和无 source 拒绝，才是可测试的硬边界。

### 把回答层接进 API

接口层需要请求模型、错误码、响应模型、provider 失败处理和 OpenAPI 测试。那是第 6.6 课的目标。

### 把所有资料一次性塞给模型

这样绕过了向量检索，也会增加无关上下文。回答层应该只接收检索出来的少量 chunk。

### 把资料回答写成 Agent 工具

Agent 是否调用 RAG 是后续设计。当前阶段先把 RAG 基础链路做稳，再考虑工具化。

## 8. 练习

练习 1：解释为什么 `MaterialAnswer.sources` 不能允许任意字符串。

练习 2：如果模型返回了正确答案但 `sources=[]`，项目为什么要拒绝？

练习 3：写一个 fake LLM 响应，让 `parse_material_answer()` 因未知 source 失败。

练习 4：把 `k=1` 改成 `k=3`，思考 prompt 中的上下文数量如何变化。

练习 5：为什么 `answer_material_question()` 仍不应该自己创建 embedding 或 vector store？

## 9. 验收标准

完成后，应能做到：

- 定义 `MaterialAnswer(answer, sources)` 作为资料回答契约。
- 将检索到的 `Document` 格式化成带来源的 prompt 上下文。
- 要求聊天模型返回 JSON object。
- 用 Pydantic 校验模型返回。
- 拒绝未知 source、无 source 的实质回答和缺失 source metadata 的资料。
- 在无资料 chunk 时返回资料不足且不调用模型。
- 通过 fake embedding 和 fake LLM client 稳定测试回答层。
- 说明当前仍没有 RAG API、CLI 问答入口或 LangGraph 流程。
- 运行 `py -3.13 -m pytest tests/test_rag.py tests/test_llm.py` 和完整测试集通过。
- 运行 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| `MaterialAnswer` | 6.6：作为 `POST /ask-materials` 的响应模型基础 |
| `answer_material_question()` | 6.6：接入 HTTP API |
| `sources` 白名单 | 6.6：转换成用户可见引用 |
| 无资料短路 | 6.6：转换成稳定 API 响应 |
| RAG 函数层 | 后续可以注册为 LangChain Agent 的只读工具 |
| 资料问答步骤 | Stage 7：可放入 LangGraph 学习流程 node |
| 引用和资料证据 | Stage 8/9：支持可追踪、可恢复的长期任务 |

项目仍然只有一条真实代码主线：

```text
ai-learning-assistant/
```

没有创建代码副本。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-6/06-05-grounded-material-answer.md`

修改文件：

- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/rag.py`
- `ai-learning-assistant/tests/test_rag.py`
- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- 新增 `MaterialAnswer` 业务模型。
- 新增资料来源提取、上下文格式化、RAG 回答 prompt 构造、模型返回解析和 answer wrapper。
- `answer_material_question()` 串联向量检索与回答生成。
- 增加 unknown source、无资料短路、空问题、缺失 source metadata 和检索后回答的回归测试。

新增依赖：

- 无。

环境变量变更：

- 无。

官方文档核对：

- [LangChain ChatOpenAI integration](https://docs.langchain.com/oss/python/integrations/chat/openai)
- [LangChain Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [LangChain vector store integrations](https://docs.langchain.com/oss/python/integrations/vectorstores)

下一步：第 6.6 课，将资料回答接入 `POST /ask-materials`。
