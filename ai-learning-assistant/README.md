# AI 学习助教

`AI 学习助教` 是本课程的贯穿代码项目。

它从一个普通 Python CLI 程序开始，逐步升级为具备 FastAPI、LLM 调用、LangChain 工具调用、RAG、LangGraph 和 Deep Agents 能力的 AI 应用。

当前阶段：阶段 5，LangChain。

当前进度：已完成第 5.7 课，CLI 和 FastAPI 都可以调用结构化 LangChain Agent 生成学习建议。

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
```

如果 provider 不可用：

- CLI 的离线规则建议仍然可用。
- CLI 的 Agent 学习建议会提示不可用，并提示使用离线规则建议。
- `GET /suggestion` 仍然可用。
- `POST /ai/suggestion` 会返回 `503`。
- `POST /chat` 会返回 `503`，不会静默改用规则建议。
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
- LangChain Agent 和工具注册。

## 6. 目录说明

```text
app/
├── api.py                       FastAPI 应用
├── cli.py                       CLI 交互
├── config.py                    LLM provider 配置
├── langchain_agent.py           LangChain Agent 和工具
├── langchain_agent_demo.py      LangChain 手动 demo
├── langchain_structured_agent_demo.py 结构化 LangChain 手动 demo
├── llm.py                       LLM 调用封装
├── llm_demo.py                  普通文本模型调用 demo
├── main.py                      CLI 入口
├── models.py                    TypedDict / Pydantic 模型
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

## 8. 与课程的关系

这个目录只维护一份真实项目代码。

每一课都会在这份代码上继续迭代，不创建 `lesson-xx-code/` 或 `stage-xx-code/` 这类副本。

课程入口见：

```text
../docs/tutorial/README.md
```
