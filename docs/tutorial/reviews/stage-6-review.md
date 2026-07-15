# 阶段 6 复盘：本地资料 RAG、向量检索与资料问答 API

## 1. 阶段目标

阶段 5 已经让项目具备结构化 LangChain Agent，并能通过 CLI 与 `POST /chat` 读取本地学员档案、学习笔记和规则建议。

阶段 6 的目标是新增一条更窄但更可追溯的资料问答链路：

```text
本地 Markdown 资料
-> Document + source
-> chunk
-> embedding
-> vector store
-> 相关资料片段
-> MaterialAnswer(answer, sources)
-> POST /ask-materials
```

完成这个阶段后，学习者需要能解释：

- RAG 为什么不是“把所有资料塞进 prompt”。
- `Document`、chunk、embedding、vector store、retriever 和 grounded answer 各自负责什么。
- 为什么 `source` 元数据必须从加载阶段保留到 API 响应阶段。
- 为什么聊天模型配置不能自动当成 embedding 模型配置。
- 为什么当前使用 `InMemoryVectorStore`，但不把它说成持久化向量数据库。
- 为什么自动测试使用 fake embedding 和 fake LLM client，而不依赖真实 API Key 或本地 Ollama 服务。
- 为什么 `POST /ask-materials` 的 400、422 和 503 要分开表达。

## 2. 已生成课程

| 小节 | 标题 | 文档 | 状态 |
| --- | --- | --- | --- |
| 6.1 | RAG 是什么 | `docs/tutorial/lessons/stage-6/06-01-rag-concepts.md` | 已生成 / 已验证 |
| 6.2 | 本地资料加载 | `docs/tutorial/lessons/stage-6/06-02-local-material-loading.md` | 已生成 / 已验证 |
| 6.3 | 文档切分 | `docs/tutorial/lessons/stage-6/06-03-document-splitting.md` | 已生成 / 已验证 |
| 6.4 | 向量检索 | `docs/tutorial/lessons/stage-6/06-04-vector-retrieval.md` | 已生成 / 已验证 |
| 6.5 | 基于资料回答 | `docs/tutorial/lessons/stage-6/06-05-grounded-material-answer.md` | 已生成 / 已验证 |
| 6.6 | RAG API | `docs/tutorial/lessons/stage-6/06-06-rag-api.md` | 已生成 / 已验证 |

## 3. 内容归位判断

阶段 6 结束时新增了：

```text
ai-learning-assistant/materials/stage-6.md
```

它应保留在 `materials/`，但定位必须清楚：这是给学习者回顾和给 RAG 检索使用的补充学习资料，不是阶段交付报告。

归位规则如下：

| 内容类型 | 应放位置 | 原因 |
| --- | --- | --- |
| RAG 概念、数据流、参数区别、常见误解、自测问题 | `ai-learning-assistant/materials/stage-6.md` | 这些内容适合被后续 `load_local_materials()` 加载、切分和检索 |
| 阶段目标、课程清单、验证命令、关键设计决策、阶段限制、下一阶段关系 | `docs/tutorial/reviews/stage-6-review.md` | 这些是阶段级复盘和归档证据，不应混入学习资料语料 |
| 逐课操作、代码片段、练习和验收标准 | `docs/tutorial/lessons/stage-6/*.md` | 这些是学习者按课推进的正文 |

因此，`stage-6.md` 不需要移入 `reviews/`，但不能承担复盘职责。本文件才是阶段 6 的归档复盘。

## 4. 当前项目能力

完成阶段 6 后，`AI 学习助教` 已经具备：

- 使用 `load_local_materials()` 读取顶层 `materials/*.md`。
- 将每份资料加载为 LangChain `Document`。
- 使用稳定相对路径保存 `Document.metadata["source"]`，例如 `materials/stage-5.md`。
- 忽略非 Markdown 文件，并按文件名稳定排序。
- 使用 `RecursiveCharacterTextSplitter` 切分资料。
- 默认 `chunk_size=800`、`chunk_overlap=120`。
- 切分后保留每个 chunk 的 `source` 元数据。
- 通过显式注入的 `Embeddings` 构建 `InMemoryVectorStore`。
- 通过独立 Ollama embedding 配置构造 `OllamaEmbeddings`。
- 使用 `retrieve_material_chunks(query, vector_store, k=3)` 取回相关 chunk。
- 使用 `MaterialAnswer(answer, sources)` 表达资料问答结果。
- 构造只包含检索 chunk 与允许引用 sources 的回答 prompt。
- 要求聊天模型返回 JSON object，并用 Pydantic 校验。
- 拒绝未知 source、缺少 source 的实质回答和缺失 source metadata 的资料。
- 无资料 chunk 时直接返回固定资料不足回答，不调用模型。
- 使用 `answer_question_from_local_materials()` 串联本地资料加载、切分、向量索引、检索和资料回答。
- 提供 `POST /ask-materials`。
- 通过自动化测试覆盖 RAG 资料加载、切分、检索、回答和 API 错误边界。

## 5. 当前架构与数据流

真实项目仍然只有一份：

```text
ai-learning-assistant/
```

阶段 6 的核心代码位于：

```text
app/rag.py
app/models.py
app/api.py
tests/test_rag.py
tests/test_api.py
```

本地资料加载与切分：

```text
materials/*.md
-> load_local_materials()
-> list[Document]
-> split_material_documents()
-> chunk Document[]
```

向量检索：

```text
chunk Document[]
-> build_material_vector_store(chunks, embeddings)
-> InMemoryVectorStore
-> retrieve_material_chunks(question, vector_store, k)
-> relevant Document[]
```

资料回答：

```text
question + relevant Document[]
-> build_material_answer_messages()
-> call_chat_completion(..., response_format={"type": "json_object"})
-> parse_material_answer()
-> MaterialAnswer(answer, sources)
```

HTTP 入口：

```text
POST /ask-materials
-> AskMaterialsRequest(question, k)
-> answer_question_from_local_materials()
-> MaterialAnswer
```

## 6. 当前入口

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

检查资料加载：

```powershell
py -3.13 -c "from app.rag import load_local_materials; print([document.metadata['source'] for document in load_local_materials()])"
```

检查默认 chunk 数量：

```powershell
py -3.13 -c "from app.rag import load_local_materials, split_material_documents; print(len(split_material_documents(load_local_materials())))"
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

资料问答接口：

```text
POST /ask-materials
```

请求示例：

```json
{
  "question": "Python 类型标注有什么用？",
  "k": 3
}
```

成功响应形状：

```json
{
  "answer": "基于资料的中文回答",
  "sources": ["materials/stage-2.md"]
}
```

真实调用需要本地 Ollama embedding 模型可用，并且聊天模型 provider 可用。自动化测试不要求这些外部服务存在。

## 7. 验证命令与结果

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest tests/test_api.py tests/test_rag.py
```

阶段 6 复盘归档前结果：

```text
61 passed
```

完整测试：

```powershell
py -3.13 -m pytest
```

阶段 6 复盘归档前结果：

```text
138 passed
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

RAG API OpenAPI smoke check：

```powershell
py -3.13 -c "from app.api import app; print(sorted(app.openapi()['paths']['/ask-materials']['post']['responses']))"
```

期望包含：

```text
['200', '400', '422', '503']
```

## 8. 关键设计决策

### 先做 2-step RAG，不做 Agentic RAG

当前项目的资料问答是固定顺序：

```text
先检索
再回答
```

这适合课程阶段 6：数据流清楚、延迟可预测、测试可隔离。让 Agent 自行决定何时检索属于 Agentic RAG，需要额外设计工具描述、调用策略、失败恢复和多步推理边界，后续再做。

### `source` 是从加载到回答的硬契约

回答层不能让模型自由填写来源。允许引用的来源只能来自检索到的 `Document.metadata["source"]`。模型引用未知路径时，代码直接拒绝。

这让资料问答具备可追溯性，也能让测试明确区分“模型回答了”与“模型引用了有效证据”。

### embedding 必须独立配置

聊天 provider 和 embedding provider 不是同一件事。当前通过：

```text
OLLAMA_EMBEDDING_BASE_URL
OLLAMA_EMBEDDING_MODEL
```

配置本地 Ollama embedding。`OLLAMA_MODEL` 仍然表示聊天模型。生产函数接收 `Embeddings` 注入，避免把聊天端点误当向量端点。

### 使用内存向量库是课程边界

`InMemoryVectorStore` 适合最小闭环和离线测试。它不会跨进程持久化，也不会解决增量更新、缓存、并发或多用户隔离问题。

这不是遗漏。持久化向量数据库应在资料规模、性能和部署需求明确后再引入。

### API 层不拼 prompt

`POST /ask-materials` 只负责：

```text
校验请求
调用 RAG 组合函数
映射 HTTP 错误
返回响应模型
```

资料加载、切分、建库、检索、prompt 构造和模型返回校验都留在 `app/rag.py`。这样后续 CLI、Agent 工具或 LangGraph node 可以复用同一条业务链路。

## 9. 已知限制

- 当前没有 RAG CLI 菜单入口。
- 当前没有把 RAG 检索封装成 LangChain Agent 工具。
- 当前没有 chat history、多轮资料问答或 streaming。
- 当前没有缓存、增量构建或持久化向量索引。
- 当前没有云端 embedding provider 配置。
- 当前没有 reranker、混合检索、metadata filter 或分数阈值。
- 当前每次 `POST /ask-materials` 都会重新加载资料、切分并构建内存向量索引。
- 当前仍是单用户本地 JSON 学习状态，不包含数据库、多用户隔离或生产级并发控制。
- 真实 RAG 调用依赖本地 Ollama embedding 服务和聊天模型 provider；自动测试覆盖调用边界，不覆盖真实 provider 的在线质量。

这些限制是阶段边界。下一阶段先进入 LangGraph 状态机，不应偷偷把 Stage 8/9/10 的能力塞进 Stage 6。

## 10. 阶段自测

完成阶段 6 后，应该能够回答：

1. 为什么 `load_local_materials()` 返回 `Document`，而不是 `str`？
2. 为什么 `metadata["source"]` 应使用相对路径？
3. `chunk_size`、`chunk_overlap` 和 `k` 分别作用在哪个阶段？
4. 为什么 `retrieve_material_chunks()` 仍返回 `Document`？
5. 为什么 `InMemoryVectorStore` 不是持久化向量数据库？
6. 为什么 `OLLAMA_MODEL` 和 `OLLAMA_EMBEDDING_MODEL` 必须分开？
7. 为什么无资料 chunk 时不调用聊天模型？
8. 为什么有资料且模型给出实质回答时必须引用至少一个允许的 source？
9. 为什么 `question=""` 是 422，而 `question="   "` 是 400？
10. 为什么 provider、Ollama 或结构化回答失败应返回 503？

## 11. 后续升级关系

| 阶段 6 内容 | 后续升级 |
| --- | --- |
| `MaterialAnswer(answer, sources)` | 前端引用展示、Deep Agents 证据写入 |
| `answer_question_from_local_materials()` | LangChain 只读 RAG tool 或 LangGraph node |
| `POST /ask-materials` | 外部调用方可直接做资料问答 |
| `source` 白名单校验 | 后续可扩展为引用质量检查 |
| 内存向量库 | 后续按性能需求升级为缓存或持久化 vector store |
| 固定 2-step RAG | 后续可演进到 Agentic RAG 或 Hybrid RAG |

阶段 7 的第一课是 `7.1 LangGraph 核心模型`。它会先解释 State、node、edge 与图结构，不会直接把 RAG 改成状态图。

## 12. 阶段变更清单

新增或扩展的核心代码：

- `ai-learning-assistant/app/rag.py`
- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/app/config.py`
- `ai-learning-assistant/tests/test_rag.py`
- `ai-learning-assistant/tests/test_api.py`
- `ai-learning-assistant/tests/test_config.py`

新增依赖：

```text
numpy==2.3.5
langchain-ollama==1.1.0
langchain-text-splitters==1.1.2
```

新增环境变量示例：

```text
OLLAMA_EMBEDDING_BASE_URL
OLLAMA_EMBEDDING_MODEL
```

新增用户能力：

```text
本地 Markdown 资料加载
Document source 元数据
文档切分
本地 Ollama embedding 配置
InMemoryVectorStore 向量检索
MaterialAnswer(answer, sources)
POST /ask-materials
```

新增补充资料：

- `ai-learning-assistant/materials/stage-6.md`

官方文档：

- [LangChain Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [LangChain vector store integrations](https://docs.langchain.com/oss/python/integrations/vectorstores)
- [LangChain Ollama embeddings](https://docs.langchain.com/oss/python/integrations/embeddings/ollama)
- [FastAPI request body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI response model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)

下一步：

- 进入第 7.1 课：LangGraph 核心模型。
