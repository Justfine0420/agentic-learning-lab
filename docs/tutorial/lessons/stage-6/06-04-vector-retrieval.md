# 第 6.4 课：向量检索

## 1. 本课目标

第 6.3 课已经把本地资料切成带来源的 chunk。现在的问题是：用户问“Python 类型标注怎么写”时，系统不能按文件顺序把全部 chunk 交给模型，需要先找到最相关的少量片段。

这一课建立向量检索层：

```text
chunk Document
-> Embeddings
-> InMemoryVectorStore
-> query
-> 最相关的 chunk Document
```

完成后，应能解释：

- embedding 为什么能让问题和资料在同一个向量空间中比较。
- vector store 负责什么，为什么它不是模型也不是资料原文。
- `k` 是候选片段数量，不是 chunk size。
- 为什么检索函数仍返回 `Document`，而不是只返回字符串。
- 为什么本地 Ollama 的聊天模型配置不能自动充当 embedding 配置。

## 2. 你会新增什么项目能力

`app/rag.py` 新增两个函数：

```text
build_material_vector_store(documents, embeddings)
build_ollama_embeddings(settings=None)
retrieve_material_chunks(query, vector_store, k=3)
```

它们的职责是：

| 函数 | 输入 | 输出 |
| --- | --- | --- |
| `build_material_vector_store` | chunk `Document` 与 `Embeddings` | `InMemoryVectorStore` |
| `build_ollama_embeddings` | 可选 Ollama embedding 配置 | `OllamaEmbeddings` |
| `retrieve_material_chunks` | 非空 query、vector store、正整数 `k` | 最相近的 `Document` 列表 |

当前层保证：

- chunk 写入内存向量库时使用调用方提供的 embedding 实现。
- 可以通过本地 Ollama embedding 模型构造 LangChain `Embeddings`。
- 检索结果保留 `source` 等 metadata。
- 空向量库返回空列表。
- 空白问题和非正数 `k` 会得到明确的 `ValueError`。

仍未新增：

- 云端 embedding provider 配置。
- 持久化向量数据库。
- reranker、混合检索、分数阈值或多路召回。
- 基于检索片段的模型回答。
- RAG API、Agent RAG 工具、LangGraph 工作流。

## 3. 前置知识

开始前，应已理解：

- `Document` 如何保存 `page_content` 和 `metadata["source"]`。
- `split_material_documents()` 如何得到可检索 chunk。
- `chunk_size`、`chunk_overlap` 与检索条数是不同参数。
- `pytest` 如何使用 test double 验证外部接口协作，而不调用真实网络服务。
- 本地 Ollama 需要先启动服务并拉取可用于 embedding 的模型。

还不需要：

- 获取或填写任何云端 embedding API Key。
- 部署 Chroma、PGVector、Pinecone 或其他持久化数据库。
- 选择云端生产 embedding 模型或计费方案。
- 调用聊天模型生成自然语言回答。

## 4. 核心概念

### embedding 是文本的可比较表示

embedding 把文本转换为浮点数向量。查询和 chunk 使用同一套 embedding 方法后，vector store 才能按距离或相似度找回语义上更接近的片段。

```text
"Python 类型标注"
-> [0.12, -0.08, ...]

"函数参数可以写类型注解"
-> [0.10, -0.06, ...]
```

向量本身不适合给用户阅读，也不会取代原文。检索结果仍然是包含原文本和来源的 `Document`。

### vector store 是索引，不是持久化资料库

`InMemoryVectorStore` 将文档向量留在当前进程内存中。进程结束后，索引就消失，下一次需要重新从 Markdown 加载、切分和建立向量。

这很适合课程里的最小数据流和离线单元测试，但不是生产持久化方案。后续若需要重启恢复、增量更新或多用户隔离，应在有明确需求时选择持久化 vector store。

### `Embeddings` 必须显式注入

现有 `LLMSettings` 描述的是聊天模型的 provider、base URL 和 model。很多聊天端点不提供 embedding API，即使同一个厂商同时提供两种模型，它们的名称、权限和计费也可能不同。

因此项目函数接收 `Embeddings`：

```python
vector_store = build_material_vector_store(chunks, embeddings)
```

函数不会把当前 `ChatOpenAI` 或 `LLMSettings.model` 自动解释为 embedding 模型。测试使用确定性 `KeywordEmbeddings` double，只验证“向量库会按 embedding 结果返回正确来源”，不把它伪装成真实语义模型。

### Ollama embedding 使用独立配置

本地 Ollama 可以同时服务聊天模型和 embedding 模型，但它们不是同一个配置项：

```text
OLLAMA_MODEL=qwen3:8b                      # 聊天模型
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large   # 向量模型
```

`OLLAMA_BASE_URL` 用于 OpenAI 兼容聊天接口，通常带 `/v1`；`OllamaEmbeddings` 使用 Ollama 原生地址，默认是 `http://localhost:11434`。项目会读取：

```text
OLLAMA_EMBEDDING_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
```

如果你的本机拉取的是其他 embedding 模型，例如 `qwen3-embedding:latest` 或 `all-minilm`，只需要改 `OLLAMA_EMBEDDING_MODEL`。前提是该模型支持 embedding；普通聊天模型不一定支持 `/api/embed`。

可以用下面命令查看本机已启用模型：

```powershell
ollama list
```

若列表里只有 completion / chat 模型，先拉取一个 embedding 模型，或把 `OLLAMA_EMBEDDING_MODEL` 改成本机已确认支持 embedding 的模型。

### `k` 控制候选数量

```text
k=1 -> 只返回最相近的一个 chunk
k=3 -> 返回前三个候选 chunk
```

`k` 与 `chunk_size` 无关：前者控制“取几块”，后者控制“每块有多大”。返回太多候选会把无关资料送入后续回答层；返回太少可能漏掉需要组合的上下文。当前默认 `k=3` 是起点，不是固定真理。

### 检索到资料不等于回答正确

检索层只做“找候选证据”。它不判断答案是否完整，也不会生成自然语言。Stage 6.5 将定义回答与来源的契约，并处理资料不足时不能编造结论的边界。

### 向量检索不是 LangGraph

向量检索是一次数据查询。LangGraph 负责有状态、多步骤、可恢复的工作流编排；当前函数没有状态图、node、edge、checkpoint 或 streaming。

## 5. 代码实现

`InMemoryVectorStore` 和 `Embeddings` 已随现有 LangChain 依赖安装。本课新增相似度计算和 Ollama 集成依赖：

```text
numpy==2.3.5
langchain-ollama==1.1.0
```

`numpy` 用于 `InMemoryVectorStore` 的相似度计算。没有它，索引能创建，但查询时会在 cosine similarity 阶段失败。

基础导入：

```python
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
```

`app/config.py` 新增 Ollama embedding 配置：

```python
@dataclass(frozen=True)
class OllamaEmbeddingSettings:
    base_url: str
    model: str
```

在 `app/rag.py` 增加向量库构建和 Ollama embedding 构造函数：

```python
def build_material_vector_store(
    documents: list[Document],
    embeddings: Embeddings,
) -> InMemoryVectorStore:
    vector_store = InMemoryVectorStore(embedding=embeddings)
    if documents:
        vector_store.add_documents(documents)
    return vector_store


def build_ollama_embeddings(
    settings: OllamaEmbeddingSettings | None = None,
) -> OllamaEmbeddings:
    current_settings = settings or get_ollama_embedding_settings()
    if current_settings.model.strip() == "":
        raise ValueError("OLLAMA_EMBEDDING_MODEL must not be empty")

    return OllamaEmbeddings(
        model=current_settings.model,
        base_url=current_settings.base_url,
    )


def retrieve_material_chunks(
    query: str,
    vector_store: InMemoryVectorStore,
    *,
    k: int = 3,
) -> list[Document]:
    if query.strip() == "":
        raise ValueError("query must not be empty")
    if k < 1:
        raise ValueError("k must be greater than 0")

    return vector_store.similarity_search(query, k=k)
```

测试定义一个只用于离线验证的 embedding double：

```python
class KeywordEmbeddings(Embeddings):
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)
```

它让 Python 类型标注问题与 `materials/python.md` 匹配，从而验证向量库调用、排序和来源传递。它不是生产 embedding 模型，也不用于项目运行时。

本次不修改：

```text
app/api.py
app/langchain_agent.py
app/models.py
app/cli.py
```

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行 RAG 单元测试：

```powershell
py -3.13 -m pytest tests/test_rag.py
```

运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

自动测试不会访问真实 Ollama 服务。若要手动验证本地 embedding 模型，先启动 Ollama 并拉取模型：

```powershell
ollama pull mxbai-embed-large
```

然后执行：

```powershell
py -3.13 -c "from app.rag import build_ollama_embeddings; print(len(build_ollama_embeddings().embed_query('Python 类型标注')))"
```

如果你使用其他本地 embedding 模型，先在 `.env` 中设置 `OLLAMA_EMBEDDING_MODEL`。

## 7. 常见错误

### 把聊天模型自动当成 embedding 模型

聊天与 embedding 是不同 API 能力。当前聊天 provider 可以生成建议，不代表同一 base URL、model 和 API Key 能生成向量。

### 把 `OLLAMA_MODEL` 复用为向量模型

`OLLAMA_MODEL` 当前用于聊天端点，示例值可能是 `qwen3:8b`。向量检索应使用 `OLLAMA_EMBEDDING_MODEL`，并确保该模型支持 embedding。否则错误会在真实调用本地 Ollama 时才暴露，定位成本很高。

### 把 `InMemoryVectorStore` 当成持久化数据库

它随进程结束而清空。当前只用于建立可理解、可测试的检索最小闭环。

### 忘记把 chunk 写入 vector store

只创建 `InMemoryVectorStore` 不会自动索引任何资料。必须通过 `add_documents()` 写入 chunk，检索才会有结果。

### 返回字符串而不是 `Document`

字符串会丢失来源元数据。后续回答层需要根据 `source` 生成引用，因此检索函数继续返回 `Document`。

### 允许空问题或 `k=0`

空问题没有检索语义，非正数候选数没有有效结果。项目函数在调用底层库前明确拒绝。

### 把检索结果直接当成最终答案

检索只提供证据候选。它不负责组合资料、说明不确定性或组织用户可读答案。

## 8. 练习

练习 1：解释下面三层的职责：

```text
Embeddings
InMemoryVectorStore
retrieve_material_chunks()
```

练习 2：为什么 `k=3` 和 `chunk_size=800` 不能互换？

练习 3：如果进程重启后检索结果为空，说明哪个组件的生命周期需要重新思考？

练习 4：为 Python、FastAPI 和 LangChain 三类资料设计一个 test double 的关键词向量，验证不同问题命中不同来源。

练习 5：把 `OLLAMA_EMBEDDING_MODEL` 改成本机已拉取的 embedding 模型，手动调用 `embed_query()`，观察返回向量长度。

## 9. 验收标准

完成后，应能做到：

- 使用 `Embeddings` 和 `InMemoryVectorStore` 建立 chunk 的向量索引。
- 按 query 和正整数 `k` 返回最相近的 `Document`。
- 证明检索结果保留 `source` 与其他 metadata。
- 区分 embedding、vector store、retriever 函数和最终回答。
- 说明内存向量库在进程结束后需要重建。
- 能构造本地 Ollama `OllamaEmbeddings`，并说明它与聊天模型配置分离。
- 说明当前项目没有云端 embedding provider 配置，也没有 RAG 回答或 API。
- 运行 `py -3.13 -m pytest tests/test_rag.py` 和完整测试集通过。
- 运行 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| chunk `Document` | 6.4：向量索引和相似度检索 |
| 检索到的 `Document` | 6.5：生成 answer + sources |
| `source` metadata | 6.5：形成可展示的引用 |
| 空 query / 非法 `k` | 6.6：转换为明确 API 请求错误 |
| retriever 函数 | 后续可以注册为 LangChain Agent 的只读工具 |
| 多步骤学习流程 | Stage 7：LangGraph State、node 和 edge |
| 持久执行与人工协作 | Stage 8：LangGraph 进阶 |
| 长任务规划与文件产物 | Stage 9：Deep Agents |

项目仍然只有一条真实代码主线：

```text
ai-learning-assistant/
```

没有创建代码副本。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-6/06-04-vector-retrieval.md`

修改文件：

- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`
- `ai-learning-assistant/app/config.py`
- `ai-learning-assistant/app/rag.py`
- `ai-learning-assistant/tests/test_config.py`
- `ai-learning-assistant/tests/test_rag.py`
- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- 新增向量库构建和相似度检索函数。
- 新增本地 Ollama embedding 配置和 `build_ollama_embeddings()`。
- 使用独立 `OLLAMA_EMBEDDING_MODEL` 避免把聊天 provider 误当作 embedding provider。
- 新增最相近来源、空索引、空 query 和非法 `k` 的回归测试。
- 新增 Ollama embedding 配置读取和构造测试；自动测试不访问真实 Ollama 服务。

新增依赖：

- `numpy==2.3.5`
- `langchain-ollama==1.1.0`

环境变量变更：

- `OLLAMA_EMBEDDING_BASE_URL`
- `OLLAMA_EMBEDDING_MODEL`

官方文档核对：

- [LangChain vector store integrations](https://docs.langchain.com/oss/python/integrations/vectorstores)
- [LangChain Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [LangChain Ollama embeddings](https://docs.langchain.com/oss/python/integrations/embeddings/ollama)
- [Ollama embeddings](https://ollama.com/blog/embedding-models)

下一步：第 6.5 课，基于检索片段生成回答并返回来源。
