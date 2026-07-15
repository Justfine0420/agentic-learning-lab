# Stage 6 补充学习资料：基础 RAG 检索、回答与 API

定位：本文件是给学习者回顾和给 RAG 检索使用的补充学习资料，保留在 `ai-learning-assistant/materials/`。阶段目标、验证结果和设计取舍放在 `docs/tutorial/reviews/stage-6-review.md`，不要把本文件当作阶段复盘。

## 目录

- [1. Stage 6 当前完成了什么](#1-stage-6-当前完成了什么)
- [2. RAG 的最小数据流](#2-rag-的最小数据流)
- [3. Document 为什么要保留 source](#3-document-为什么要保留-source)
- [4. chunk_size、overlap 和 k 的区别](#4-chunk_sizeoverlap-和-k-的区别)
- [5. embedding 与 vector store](#5-embedding-与-vector-store)
- [6. 当前代码如何调用](#6-当前代码如何调用)
- [7. 当前边界](#7-当前边界)
- [8. 从基础 RAG 到进阶 RAG](#8-从基础-rag-到进阶-rag)
- [9. 自测问题](#9-自测问题)

## 1. Stage 6 当前完成了什么

Stage 5 的 Agent 可以读取学员档案、笔记和规则建议，但不能根据 `materials/` 下的课程资料回答问题。Stage 6 建立了基础 RAG 闭环。

当前项目已经可以：

- 将顶层 `materials/*.md` 加载为 LangChain `Document`。
- 用 `RecursiveCharacterTextSplitter` 将完整资料切成带 overlap 的 chunk。
- 使用显式传入的 `Embeddings` 将 chunk 写入 `InMemoryVectorStore`。
- 根据问题检索最相近的 chunk，并保留它的来源 metadata。
- 将“问题 + 检索 chunk”交给聊天模型，生成 `MaterialAnswer(answer, sources)`。
- 通过 `POST /ask-materials` 提供资料问答 API。

相关代码在：

```text
app/rag.py
app/config.py
tests/test_rag.py
```

## 2. RAG 的最小数据流

```text
materials/*.md
-> load_local_materials()
-> 完整 Document
-> split_material_documents()
-> chunk Document
-> build_material_vector_store()
-> InMemoryVectorStore
-> retrieve_material_chunks()
-> 相关 chunk Document
-> generate_material_answer()
-> MaterialAnswer(answer, sources)
-> POST /ask-materials
```

每一步职责不同：

| 概念 | 当前项目中的职责 |
| --- | --- |
| `Document` | 保存资料原文和来源 metadata。 |
| chunk | 将过长资料拆成适合检索的小片段。 |
| embedding | 将文本转换为可比较的浮点数向量。 |
| vector store | 保存 chunk 向量，并按相似度查询。 |
| retriever | 根据问题返回少量相关 chunk 的接口。 |
| grounded answer | 仅根据检索 chunk 生成回答，并返回可追溯来源。 |

不要把这些名称当成同一个东西。特别是 embedding 只负责表示文本，不会直接生成自然语言答案。

## 3. Document 为什么要保留 source

加载器读取 Markdown 时，会为每份资料创建：

```python
Document(
    page_content="资料的原始 Markdown 内容",
    metadata={"source": "materials/stage-5.md"},
)
```

`page_content` 是资料正文；`metadata["source"]` 是资料从哪里来的。切分后的每个 chunk 也会继承该 metadata。

```text
materials/stage-5.md
-> 完整 Document，source=materials/stage-5.md
-> 多个 chunk，每个都保留同一个 source
```

这样后续即使只检索到某一个 chunk，也能知道它来自哪份资料。来源路径使用相对路径，避免泄露机器上的绝对目录，也便于测试在不同机器上得到同样结果。

## 4. chunk_size、overlap 和 k 的区别

这三个参数作用在不同阶段：

```python
chunks = split_material_documents(
    documents,
    chunk_size=800,
    chunk_overlap=120,
)

results = retrieve_material_chunks(
    "Python 类型标注怎么写？",
    vector_store,
    k=3,
)
```

| 参数 | 含义 |
| --- | --- |
| `chunk_size=800` | 每个 chunk 的目标最大字符数。 |
| `chunk_overlap=120` | 相邻 chunk 重复保留的字符数，减少边界处上下文断裂。 |
| `k=3` | 本次问题从全部 chunk 中取回的候选数量。 |

因此，`chunk_size` 决定资料如何被切开，`k` 决定一次检索拿几块回来。两者不能互相替代。

## 5. embedding 与 vector store

embedding 会把问题和 chunk 映射为同一个向量空间中的数字列表：

```text
"Python 类型标注"
-> [0.12, -0.08, ...]

"函数参数可以写类型注解"
-> [0.10, -0.06, ...]
```

向量相近不等于文字相同，而是表示它们在 embedding 模型看来语义可能相关。

当前项目的 `build_material_vector_store()` 使用 `InMemoryVectorStore`。它把 chunk 和向量保存在当前 Python 进程内存中：

```text
程序启动
-> 建立内存向量库
-> 可以检索

程序结束
-> 向量索引消失
-> 下次需要重新加载、切分和建立索引
```

这不是持久化向量数据库。Ollama 下载的 embedding 模型文件也不是本项目资料的向量索引。

聊天模型和 embedding 模型使用不同配置：

```text
OLLAMA_MODEL=qwen3:8b
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
```

不能因为同一个 Ollama 服务能聊天，就把聊天模型配置自动当成 embedding 配置。

## 6. 当前代码如何调用

完整调用顺序如下：

```python
from app.rag import (
    build_material_vector_store,
    load_local_materials,
    retrieve_material_chunks,
    split_material_documents,
)

documents = load_local_materials()
chunks = split_material_documents(documents)
vector_store = build_material_vector_store(chunks, embeddings)
results = retrieve_material_chunks(
    "Python 类型标注怎么写？",
    vector_store,
    k=3,
)
```

`embeddings` 由调用方传入。生产环境可通过 `build_ollama_embeddings()` 创建本地 Ollama embedding 对象；测试则使用确定性的 fake embedding，避免依赖本地服务或网络。

`results` 是 `list[Document]`，每项仍包含：

```python
result.page_content
result.metadata["source"]
```

也就是说，当前可以根据问题找回资料片段和来源。

完整的资料问答入口会继续执行：

```python
answer = answer_question_from_local_materials(
    "Python 类型标注怎么写？",
    k=3,
)
```

它会加载资料、切分、建立内存索引、检索 chunk，再调用聊天模型生成：

```python
MaterialAnswer(
    answer="基于资料的中文回答",
    sources=["materials/stage-2.md"],
)
```

`POST /ask-materials` 调用的也是这条业务链路。模型被要求只能使用检索到的资料片段；资料不足时，回答会明确说明资料不足，而不是把模型自身知识伪装成资料结论。

## 7. 当前边界

当前 Stage 6.6 已完成基础 RAG 的“加载 -> 切分 -> 检索 -> 回答 -> API”闭环，但还没有：

- 云端 embedding provider 配置。
- 缓存、增量构建或持久化向量索引；当前每次 API 请求都会重建内存索引。
- reranker、混合检索、分数阈值或多路召回。
- Agent 自动调用 RAG 检索工具。
- 多轮资料问答、chat history、streaming 或 LangGraph 状态机。

所以需要区分：

```text
当前：能依据本地资料回答问题，并返回来源。
进阶：提高召回质量、性能、持久化能力和多步骤交互。
```

## 8. 从基础 RAG 到进阶 RAG

高级 RAG 不是替换当前代码，而是在基础闭环稳定后，针对明确问题逐层增加能力。推荐学习顺序如下：

| 顺序 | 要解决的问题 | 学习重点 |
| --- | --- | --- |
| 1. 评估基础检索 | 不知道检索结果是否真的相关 | 自建问题集、人工标注相关 chunk、`Recall@k`、`MRR`、错误样例分析。 |
| 2. 改善资料与切分 | 一个概念被切断，或 chunk 过大、过小 | 按标题、段落、代码块切分；补充 metadata；比较不同 `chunk_size` 与 overlap。 |
| 3. 持久化与增量索引 | 每次请求都重新 embedding，资料变大后变慢 | 了解 Chroma、Qdrant、PGVector 等持久化 vector store，以及资料变更后的增量更新策略。 |
| 4. 改善召回 | 纯向量 top-k 漏掉术语、代码名或精确关键词 | 关键词检索、向量检索、metadata filter、混合召回、分数阈值。 |
| 5. 重排候选 | 召回的候选很多，但前几条不够准确 | 先召回较多候选，再用 reranker 精排，最后把少量证据交给模型。 |
| 6. 多轮与 Agent | 不同问题需要不同资料范围或多步操作 | 将 retriever 封装为只读工具，再按需求引入 chat history、LangGraph 或人工确认。 |

学习时先从当前项目的 `tests/test_rag.py` 和 `app/rag.py` 开始：给已有资料写几个问题，观察 top-k 是否命中正确 `source`。没有评价样例就直接上 reranker，通常无法判断“效果变好”还是“只是换了更多组件”。

可继续阅读这些官方资料：

- LangChain Retrieval 概览：<https://docs.langchain.com/oss/python/langchain/retrieval>
- LangChain 文本切分器：<https://python.langchain.com/docs/concepts/text_splitters/>
- Ollama Embeddings：<https://docs.ollama.com/capabilities/embeddings>
- Qdrant Hybrid Queries：<https://qdrant.tech/documentation/concepts/hybrid-queries/>

其中，持久化数据库、混合检索和 reranker 都是解决“资料规模或检索质量已经成为问题”时的手段，不是基础 RAG 必须一次装齐的组件。

## 9. 自测问题

1. 为什么 `Document` 不能只保存 `page_content`，还要保存 `metadata["source"]`？
2. 为什么 `chunk_size=800` 和 `k=3` 不是同一个参数？
3. 为什么 `InMemoryVectorStore` 不能当作持久化数据库？
4. `embed_query("Python 类型标注")` 的结果为什么不是用户可读的知识问答答案？
5. 为什么 embedding 模型配置应与聊天模型配置分开？
6. 为什么没有评估问题集时，不应仅凭感觉加入 reranker？
7. 为什么持久化 vector store 解决的是性能与重启恢复，而不是自动提高回答正确性？
