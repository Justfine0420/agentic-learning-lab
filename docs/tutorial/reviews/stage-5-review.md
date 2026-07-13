# 阶段 5 复盘：LangChain Agent、工具调用与双入口

## 1. 阶段目标

阶段 4 已经让项目能够直接调用模型，并得到经过 Pydantic 校验的学习建议。

阶段 5 的目标是在这层基础上引入 LangChain Agent，把“给模型一段完整资料并生成答案”的调用方式升级为：

```text
用户问题
-> Agent
-> 按需调用只读工具
-> 读取当前学习状态
-> 生成结构化学习建议
-> CLI 或 FastAPI 返回结果
```

完成这个阶段后，学习者需要能解释：

- LangChain 在项目中负责什么，LangGraph 和 Deep Agents 又分别解决什么问题。
- `create_agent()`、模型、注解式 middleware、messages 和 tools 如何组成 Agent harness。
- 为什么工具要按单一职责拆分，并保持只读。
- 为什么 Agent 最终结果使用 `StructuredLearningSuggestion`，而不是重新解析普通文本。
- 为什么 CLI 和 FastAPI 都复用 `run_structured_learning_agent()`。
- 为什么 provider、网络和结构化结果失败要明确暴露，不能伪装成成功的规则建议。

## 2. 已生成课程

| 小节 | 标题 | 文档 | 状态 |
| --- | --- | --- | --- |
| 5.1 | LangChain 定位 | `docs/tutorial/lessons/stage-5/05-01-langchain-positioning.md` | 已生成 / 已验证 |
| 5.2 | 创建第一个 LangChain Agent | `docs/tutorial/lessons/stage-5/05-02-first-langchain-agent.md` | 已生成 / 已验证 |
| 5.3 | Python 函数变成 LangChain 工具 | `docs/tutorial/lessons/stage-5/05-03-python-functions-as-tools.md` | 已生成 / 已验证 |
| 5.4 | 多工具调用 | `docs/tutorial/lessons/stage-5/05-04-multiple-tools.md` | 已生成 / 已验证 |
| 5.5 | 结构化 Agent 输出 | `docs/tutorial/lessons/stage-5/05-05-structured-agent-output.md` | 已生成 / 已验证 |
| 5.6 | CLI 接入 LangChain Agent | `docs/tutorial/lessons/stage-5/05-06-cli-agent-integration.md` | 已生成 / 已验证 |
| 5.7 | FastAPI 接入 LangChain Agent | `docs/tutorial/lessons/stage-5/05-07-fastapi-agent-integration.md` | 已生成 / 已验证 |

## 3. 当前项目能力

完成阶段 5 后，`AI 学习助教` 已经具备：

- 安装并固定 `langchain==1.3.12` 与 `langchain-openai==1.3.4`。
- 使用 `ChatOpenAI` 复用阶段 4 的 `LLMSettings`、API Key、base URL、model、超时和重试配置。
- 使用 `create_agent()` 创建 Agent，而不是在入口层手写工具调用循环。
- 使用 `@dynamic_prompt` 根据 Agent state 生成学习助教职责、工具使用和中文输出约束。
- 使用 `@wrap_tool_call` 把本地资料读取失败转换为安全的工具结果，避免编造资料。
- 使用 `read_current_student_profile` 读取当前学员档案。
- 使用 `read_recent_learning_notes` 读取受 1 到 10 条边界限制的最近笔记。
- 使用 `build_current_rule_based_suggestion` 读取已有离线规则建议。
- 让三个工具全部通过 `storage.load_student()` 读取同一份 `data/student.json`。
- 使用 `ToolStrategy(StructuredLearningSuggestion)` 获取结构化 Agent 输出。
- 从 Agent state 的 `structured_response` 提取并校验 `StructuredLearningSuggestion`。
- 对 Ark coding / Agent Plan 路径使用窄兼容包装层，避免发送不被端点接受的 `tool_choice="required"`。
- 在 CLI 菜单第 4 项调用结构化 Agent，并在调用前保存内存中的学员状态。
- 提供 `POST /chat`，把请求中的 `question` 传给结构化 Agent。
- 让 `/chat` 在请求体错误、空白问题与 Agent/provider 失败时分别表达 `422`、`400` 与 `503`。
- 通过 fake Agent、`TestClient` 和离线工具调用测试核心路径，不让单元测试依赖真实模型服务。

## 4. 当前架构与数据流

真实代码始终只有一份：

```text
ai-learning-assistant/
```

阶段 5 的核心代码位于：

```text
app/langchain_agent.py
```

结构化 Agent 调用链：

```text
question
-> run_structured_learning_agent(question)
-> create_structured_learning_agent()
-> create_agent(model, tools, middleware, response_format)
-> agent.invoke({"messages": ...})
-> result["structured_response"]
-> StructuredLearningSuggestion
```

两个用户入口复用同一条业务调用链：

```text
CLI 选项 4
-> save_student(student)
-> run_structured_learning_agent()
-> Agent 工具读取 data/student.json
-> 格式化为命令行文本

POST /chat
-> ChatRequest.question
-> run_structured_learning_agent(question)
-> Agent 工具读取 data/student.json
-> AgentChatResponse
```

CLI 需要先保存 `student`，因为 CLI 中的内存字典和 Agent 工具读取的 JSON 文件是两份不同的状态视图。FastAPI 的资料与笔记 API 已经直接写入 JSON，因此 `/chat` 可以让工具读取持久化后的当前状态。

三个工具的职责如下：

| 工具 | 输入 | 输出 | 写入行为 |
| --- | --- | --- | --- |
| `read_current_student_profile` | 是否包含笔记 | 当前档案文本 | 无 |
| `read_recent_learning_notes` | `limit` | 最近笔记文本 | 无 |
| `build_current_rule_based_suggestion` | 无 | 规则建议文本 | 无 |

工具保持只读是当前阶段的刻意约束。这样 Agent 可以查询资料，但不能修改学员档案、笔记或文件系统。

## 5. 当前入口

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行 CLI：

```powershell
py -3.13 -m app.main
```

相关菜单：

```text
3. 查看离线规则建议
4. 生成 Agent 学习建议
5. 退出
```

运行普通 Agent demo：

```powershell
py -3.13 -m app.langchain_agent_demo
```

运行结构化 Agent demo：

```powershell
py -3.13 -m app.langchain_structured_agent_demo
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

建议相关接口：

```text
GET  /suggestion
POST /ai/suggestion
POST /chat
```

`GET /suggestion` 保持为离线规则建议。`POST /ai/suggestion` 保留为阶段 4 的直接 LLM 路径。`POST /chat` 是阶段 5 的结构化工具型 Agent 路径。

## 6. 验证命令与结果

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest tests/test_langchain_agent.py tests/test_cli.py tests/test_api.py
```

这组测试覆盖 Agent 模型初始化、Ark 兼容包装、`@tool`、`@dynamic_prompt`、`@wrap_tool_call`、结构化结果、CLI 路由和 `/chat` 错误边界。

完整测试：

```powershell
py -3.13 -m pytest
```

阶段 5 复盘归档前结果：

```text
93 passed
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

无需 provider 的工具 smoke check：

```powershell
py -3.13 -c "from app.langchain_agent import build_learning_agent_tools; print([item.name for item in build_learning_agent_tools()])"
```

`POST /chat` 的 OpenAPI 契约 smoke check：

```powershell
py -3.13 -c "from app.api import app; print(sorted(app.openapi()['paths']['/chat']['post']['responses']))"
```

真实 provider 调用需要本地 `.env` 与可用模型服务。自动化测试刻意不使用真实 API Key，也不将网络连通性视为阶段完成条件。

## 7. 关键设计决策

### 保留阶段 4 的直接 LLM 路径

阶段 5 没有删除：

```text
app/llm.py
POST /ai/suggestion
```

它们仍然用于说明直接模型调用、OpenAI-compatible HTTP 协议和结构化输出校验。Agent 路径不是“用新库替换旧代码”，而是增加一个可以调用工具的业务层。

| 入口 | 路径 | 适用场景 |
| --- | --- | --- |
| `GET /suggestion` | 本地规则 | 无 provider 时的稳定建议 |
| `POST /ai/suggestion` | 直接 LLM | 对比阶段 4 的模型调用 |
| CLI 选项 4 | 结构化 Agent | 命令行 Agent 交互 |
| `POST /chat` | 结构化 Agent | API Agent 交互 |

Agent 失败时，`/chat` 返回明确的 `503`；它不会把规则建议伪装成 Agent 成功结果。

### 工具按查询职责拆分，且全部只读

把档案、笔记和规则建议塞进一个大工具，会让输入参数、描述和返回值失去边界。当前工具分别对应不同问题，Agent 可以自行决定是否需要调用。

只读约束避免模型调用直接改变学习数据。写工具需要额外的确认、审计、幂等性和失败恢复设计，留给后续有明确业务需求的阶段。

### 结构化输出是入口复用的契约

`StructuredLearningSuggestion` 已经定义了摘要、1 到 3 条行动建议和下一检查点。CLI 用它格式化文本，API 用它作为响应模型，测试也直接构造它。

稳定的结构比“解析最后一条普通文本”可靠。缺少 `structured_response` 时，代码抛出 `ValueError`，API 把它转换为 `503`，而不是继续猜测结果内容。

### Ark 兼容只放在模型适配层

部分 OpenAI-compatible 端点不接受 LangChain 为结构化输出设置的强制工具选择参数。`VolcengineCompatibleChatOpenAI` 只在 `volcengine_agent_plan` 与兼容别名 `volcengine_coding` 下去掉 `tool_choice="required"` 或 `"any"`，保留工具列表和业务 schema。

这比在 CLI、API 或每个工具上散落 provider 判断更容易测试，也不会改变 DeepSeek 和 Ollama 的默认路径。

### streaming、RAG 和状态图继续后置

当前 Agent 先完成最终结构化结果与入口复用。Streaming 需要定义 token、工具调用、工具结果和完成事件的协议；RAG 需要引入资料加载、切分、embedding、检索和来源；LangGraph 需要显式 State 与节点分支。

这些能力都会建立在阶段 5 已经稳定的模型、工具、结构化结果与错误边界之上。

## 8. 已知限制

- Agent 只读取本地 JSON 档案、笔记和离线规则建议，不读取 `materials/`，没有 RAG。
- `POST /chat` 是单轮请求，不保存聊天历史，也没有 memory。
- 没有写工具，Agent 不会修改档案、笔记、文件或外部系统。
- 没有 streaming；API 只在 Agent 完成后返回最终 JSON。
- 没有 LangGraph State、checkpoint、条件分支、重试图或 human-in-the-loop。
- 没有 Deep Agents 的计划、文件系统任务、子 Agent 或长任务管理。
- 当前仍是单用户本地 JSON 存储，不能替代数据库、多用户隔离或生产级并发控制。
- 真实模型调用依赖 provider 配置、网络和模型工具调用兼容性；自动化测试覆盖调用边界，不覆盖真实 provider 的在线行为。

这些限制是当前阶段边界，不应通过临时功能堆叠绕过。

## 9. 阶段自测

完成阶段 5 后，应该能够回答：

1. `create_agent()` 为什么需要 model、tools、middleware 和 messages？
2. `read_current_student_profile` 为什么适合作为只读 tool，而不是把所有资料直接拼进每条 message？
3. CLI 调 Agent 前为什么先执行 `save_student(student)`？
4. `ToolStrategy(StructuredLearningSuggestion)` 和 `structured_response` 分别解决什么问题？
5. `/ai/suggestion` 与 `/chat` 的调用链、请求体和 `source` 有什么差异？
6. 为什么 Agent/provider 失败应返回 `503`，而不是返回规则建议并使用 `200`？
7. 为什么 Ark 兼容逻辑应放在 Chat 模型适配层？
8. RAG、streaming 与 LangGraph 为什么没有被提前放进阶段 5？

## 10. 后续升级关系

| 阶段 5 内容 | 阶段 6 到 9 的升级 |
| --- | --- |
| 三个本地只读工具 | RAG 阶段新增资料检索工具 |
| `StructuredLearningSuggestion` | RAG 结果、Graph State 与长期任务结果的结构化契约 |
| `run_structured_learning_agent()` | RAG 能力接入后仍可作为 Agent 业务入口 |
| 单轮 `/chat` | 后续可由 LangGraph 管理多步状态和 streaming 事件 |
| JSON 文件状态 | checkpoint、Repository 与数据库迁移的前置约束 |
| provider 兼容适配 | 后续模型与工具策略的边界层 |

阶段 6 的第一课是 `6.1 RAG 是什么`。它先建立文档、chunk、embedding、retriever 与来源引用的概念边界，再开始让 Agent 基于本地资料回答问题。

## 11. 阶段变更清单

新增或扩展的核心代码：

- `ai-learning-assistant/app/langchain_agent.py`
- `ai-learning-assistant/app/langchain_agent_demo.py`
- `ai-learning-assistant/app/langchain_structured_agent_demo.py`
- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/tests/test_langchain_agent.py`
- `ai-learning-assistant/tests/test_cli.py`
- `ai-learning-assistant/tests/test_api.py`

新增依赖：

```text
langchain==1.3.12
langchain-openai==1.3.4
```

新增用户能力：

```text
LangChain Agent
三个只读工具
结构化 Agent 建议
CLI Agent 菜单入口
POST /chat
Ark 工具调用兼容适配
```

官方文档：

- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output)

下一步：

- 进入第 6.1 课：RAG 是什么。
