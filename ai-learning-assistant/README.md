# AI 学习助教

`AI 学习助教` 是本课程的贯穿代码项目。

它从一个普通 Python CLI 程序开始，逐步升级为具备 FastAPI、LLM 调用、LangChain 工具调用、RAG、LangGraph 和 Deep Agents 能力的 AI 应用。

当前阶段：阶段 7，LangGraph 基础，进行中。

当前进度：CLI 和 FastAPI 都可以调用结构化 LangChain Agent 生成学习建议；阶段 6 已通过 `POST /ask-materials` 暴露基于本地资料的 RAG 问答接口；第 7.2 课已新增 `LearningState`、`LearningStateUpdate` 和初始状态构造函数。当前还没有 `StateGraph`、node、edge 或学习流程 API。

## 1. 当前功能

### CLI

- 收集学员姓名、学习目标和 Python 水平。
- 添加学习笔记。
- 查看学员资料和笔记。
- 生成离线规则学习建议。
- 在 provider 配置可用时，通过 LangChain Agent 生成结构化学习建议。

运行入口：

```powershell
py -3.13 -m app.main
```

### FastAPI

当前 API 覆盖：

```text
GET  /health
GET  /profile
POST /profile
GET  /notes
GET  /notes/{note_index}
POST /notes
GET  /suggestion
POST /ai/suggestion
POST /chat
POST /ask-materials
```

启动服务：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### 本地存储

当前仍使用 JSON 文件保存学习状态：

```text
data/student.json
```

已覆盖的存储能力：

- 文件不存在时返回默认学员资料。
- JSON 损坏时备份异常文件并恢复默认数据。
- 字段缺失或旧数据格式不完整时做基础归一化。
- CLI、API 和 LangChain 工具共用同一份本地学习状态。

数据库迁移会在后续课程中再引入。

### LLM 调用

当前已支持 OpenAI 兼容的 `chat/completions` 调用方式，并通过环境变量切换 provider。

支持的 provider 配置包括：

```text
LLM_PROVIDER=volcengine_agent_plan
LLM_PROVIDER=deepseek
LLM_PROVIDER=ollama
```

相关模块：

```text
app/config.py
app/llm.py
app/llm_demo.py
app/structured_llm_demo.py
```

真实密钥写入本地 `.env`，不要写入 `.env.example` 或代码。

### LangChain

当前 LangChain 能力：

- 使用 `create_agent` 创建最小 Agent。
- 注册多个只读工具：`read_current_student_profile`、`read_recent_learning_notes`、`build_current_rule_based_suggestion`。
- 工具可以读取 `data/student.json` 中的学员档案、最近学习笔记，并复用离线规则建议。
- 使用 `ToolStrategy(StructuredLearningSuggestion)` 生成结构化 Agent 结果。
- 对火山引擎 Ark coding / Agent Plan 路径放宽 LangChain 强制工具选择参数，兼容不支持 `tool_choice="required"` 的 OpenAI-compatible 端点。
- CLI 第 4 项会调用 `run_structured_learning_agent()`，并把结果格式化为命令行文本。
- `POST /chat` 接收学员问题后调用 `run_structured_learning_agent(question)`，返回结构化 Agent 建议。
- 提供手动 demo 入口验证 Agent 调用。

相关模块：

```text
app/langchain_agent.py
app/langchain_agent_demo.py
app/langchain_structured_agent_demo.py
```

手动运行：

```powershell
py -3.13 -m app.langchain_agent_demo
```

这条命令需要 `.env` 中的 provider 配置可用，或者本地 Ollama 已启动。

### RAG 基础

当前 RAG 已完成资料加载、文档切分、向量检索和基于资料回答：

- `load_local_materials()` 读取顶层 `materials/*.md`。
- 每份资料返回一个 LangChain `Document`。
- `Document.metadata["source"]` 使用稳定的相对路径，例如 `materials/stage-5.md`。
- 文件按名称排序；非 Markdown 文件不会进入资料集合。
- `split_material_documents()` 使用 `RecursiveCharacterTextSplitter` 将资料拆成可检索 chunk，并保留每个 chunk 的元数据。
- 默认 `chunk_size=800`、`chunk_overlap=120`；非法大小组合会在切分前失败。
- `build_material_vector_store()` 使用注入的 `Embeddings` 建立 `InMemoryVectorStore`。
- `build_ollama_embeddings()` 使用本地 Ollama embedding 模型构造 `OllamaEmbeddings`。
- `retrieve_material_chunks()` 按问题返回最相近的 chunk，并保留 `source` 元数据。
- `MaterialAnswer` 定义资料回答结构，包含 `answer` 和 `sources`。
- `generate_material_answer()` 将检索 chunk 交给聊天模型，并校验返回 JSON 与引用来源。
- `answer_material_question()` 串联向量检索和资料回答生成。
- `answer_question_from_local_materials()` 组合本地资料加载、切分、向量索引和资料回答。
- `POST /ask-materials` 接收资料问题并返回 `answer + sources`。
- `numpy` 用于内存向量库的相似度计算。

当前还没有云端 embedding provider 配置、RAG CLI 入口、持久化向量索引或 Agent RAG 工具。

可以在不配置 provider 的情况下手动检查加载结果：

```powershell
py -3.13 -c "from app.rag import load_local_materials; print([document.metadata['source'] for document in load_local_materials()])"
```

查看默认 chunk 数量：

```powershell
py -3.13 -c "from app.rag import load_local_materials, split_material_documents; print(len(split_material_documents(load_local_materials())))"
```

实际检索需要调用方传入与资料语料兼容的 `Embeddings` 实例；项目支持通过本地 Ollama 构造 embedding，但不会把现有聊天 provider 自动当成 embedding provider。

### LangGraph 基础

当前 LangGraph 阶段已经开始，但还没有运行时图：

- `LearningState` 定义学习流程的共享状态字段。
- `LearningStateUpdate` 表达后续 node 可以返回的局部状态更新。
- `create_initial_learning_state()` 可以从现有 `Student` 字典创建初始学习状态。
- `completed_steps` 使用 `Annotated[list[str], add]` 标注累加语义，为后续 LangGraph reducer 做准备。

相关模块：

```text
app/graph.py
tests/test_graph.py
```

当前还没有 `StateGraph`、node、edge、checkpoint、streaming 或学习流程 API。后续课程会从第一个 node 开始逐步接入。

## 2. 安装依赖

建议使用 Python 3.13。

在本目录下执行：

```powershell
py -3.13 -m pip install -r requirements.txt
```

## 3. 环境变量

复制 `.env.example` 为本地 `.env`，并按你的 provider 填写配置。

示例：

```text
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

本地 Ollama 示例：

```text
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_EMBEDDING_BASE_URL=http://127.0.0.1:11434
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
```

聊天模型与向量模型分开配置。若本机启用的是其他 embedding 模型，例如 `qwen3-embedding:latest`，修改 `OLLAMA_EMBEDDING_MODEL`。

如果 provider 不可用：

- CLI 的离线规则建议仍然可用。
- CLI 的 Agent 学习建议会提示不可用，并提示使用离线规则建议。
- `GET /suggestion` 仍然可用。
- `POST /ai/suggestion` 会返回 `503`。
- `POST /chat` 会返回 `503`，不会静默改用规则建议。
- `POST /ask-materials` 会返回 `503`，不会静默改用资料外答案。
- 需要真实模型的 demo 会提示配置或连接问题。

## 4. 运行项目

运行 CLI：

```powershell
py -3.13 -m app.main
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

普通文本模型调用 demo：

```powershell
py -3.13 -m app.llm_demo
```

结构化模型调用 demo：

```powershell
py -3.13 -m app.structured_llm_demo
```

LangChain Agent demo：

```powershell
py -3.13 -m app.langchain_agent_demo
```

结构化 LangChain Agent demo：

```powershell
py -3.13 -m app.langchain_structured_agent_demo
```

## 5. 运行测试

```powershell
py -3.13 -m pytest
```

当前测试覆盖：

- 存储读写和异常恢复。
- CLI 输出和交互入口。
- FastAPI 路由、请求体校验和错误响应。
- provider 配置读取。
- LLM 请求封装和结构化输出解析。
- LangChain Agent、注解式工具与 middleware。
- RAG 资料加载、切分、向量检索、基于资料回答和资料问答 API。
- LangGraph 学习流程状态 schema 和初始状态构造。

## 6. 目录说明

```text
app/
├── api.py                       FastAPI 应用
├── cli.py                       CLI 交互
├── config.py                    LLM provider 配置
├── graph.py                     LangGraph 学习流程状态 schema
├── langchain_agent.py           LangChain Agent 和工具
├── langchain_agent_demo.py      LangChain 手动 demo
├── langchain_structured_agent_demo.py 结构化 LangChain 手动 demo
├── llm.py                       LLM 调用封装
├── llm_demo.py                  普通文本模型调用 demo
├── main.py                      CLI 入口
├── models.py                    TypedDict / Pydantic 模型
├── rag.py                       本地 Markdown 资料加载、检索和资料回答
├── storage.py                   JSON 存储
├── structured_llm_demo.py       结构化输出 demo
├── student_state.py             初始学习状态
└── suggestions.py               离线规则学习建议

data/                            本地学习数据，真实数据不提交
materials/                       阶段补充学习资料
outputs/                         后续生成的学习计划和总结
tests/                           测试代码
```

## 7. 学习资料

- `materials/stage-2.md`：Python 工程化、模块导入、JSON 文件读写、异常处理和 pytest。
- `materials/stage-3.md`：FastAPI、Pydantic、状态码、`TestClient` 和 API 数据流。
- `materials/stage-4.md`：LLM provider 配置、模型调用、结构化输出、CLI/API AI 建议入口。
- `materials/stage-5.md`：LangChain Agent、工具调用、结构化 Agent 输出、CLI/API 双入口与错误边界。
- `materials/stage-6.md`：基础 RAG 检索、Document source、chunk、embedding、资料回答与 `POST /ask-materials`。

这些 Markdown 在 Stage 6.2 已能加载为带 `source` 元数据的 `Document`，在 Stage 6.3 切分为保留来源的 chunk，在 Stage 6.4 通过注入的 embedding 建立内存向量检索，在 Stage 6.5 生成带 `sources` 的资料回答，并在 Stage 6.6 通过 `POST /ask-materials` 暴露为 HTTP 接口。

## 8. 与课程的关系

这个目录只维护一份真实项目代码。

每一课都会在这份代码上继续迭代，不创建 `lesson-xx-code/` 或 `stage-xx-code/` 这类副本。

课程入口见：

```text
../docs/tutorial/README.md
```
