# Stage 5 补充学习资料：LangChain Agent、工具调用与双入口

## 目录

- [1. Stage 5 在项目中新增了什么](#1-stage-5-在项目中新增了什么)
- [2. Stage 5 要解决的核心问题](#2-stage-5-要解决的核心问题)
- [3. Agent 和直接 LLM 调用有什么区别](#3-agent-和直接-llm-调用有什么区别)
- [4. `create_agent()` 组装了什么](#4-create_agent-组装了什么)
- [5. `@dynamic_prompt` 和本次用户问题如何分工](#5-dynamic_prompt-和本次用户问题如何分工)
- [6. 为什么把 Python 函数包装成工具](#6-为什么把-python-函数包装成工具)
- [7. `@wrap_tool_call` 为什么不写进工具函数](#7-wrap_tool_call-为什么不写进工具函数)
- [8. 多工具和只读边界](#8-多工具和只读边界)
- [9. `agent.invoke()` 之后发生了什么](#9-agentinvoke-之后发生了什么)
- [10. 结构化输出为什么使用 `ToolStrategy`](#10-结构化输出为什么使用-toolstrategy)
- [11. `structured_response` 为什么还要校验](#11-structured_response-为什么还要校验)
- [12. Provider 兼容性为什么放在模型适配层](#12-provider-兼容性为什么放在模型适配层)
- [13. 为什么 CLI 和 FastAPI 复用同一入口](#13-为什么-cli-和-fastapi-复用同一入口)
- [14. `/ai/suggestion` 和 `/chat` 的边界](#14-aisuggestion-和-chat-的边界)
- [15. 错误语义与测试隔离](#15-错误语义与测试隔离)
- [16. 当前数据流](#16-当前数据流)
- [17. Stage 5 的已知限制](#17-stage-5-的已知限制)
- [18. 常见误解与排查](#18-常见误解与排查)
- [19. LangChain v1 阅读要点](#19-langchain-v1-阅读要点)
- [20. 自测问题](#20-自测问题)
- [21. 验证命令](#21-验证命令)

## 1. Stage 5 在项目中新增了什么

Stage 4 已经能把学员资料拼进 prompt，直接调用模型并解析结构化结果。Stage 5 再增加一层 Agent：模型不必每次都收到全部资料，而是根据问题选择是否调用工具。

```text
用户问题
-> LangChain Agent
-> 按需调用只读工具
-> 读取当前学习状态
-> 生成 StructuredLearningSuggestion
-> CLI 或 FastAPI 返回结果
```

当前项目的核心能力如下：

- `create_agent()` 负责组装模型、工具、middleware 和输出策略。
- `read_current_student_profile`、`read_recent_learning_notes`、`build_current_rule_based_suggestion` 都是只读工具。
- `run_structured_learning_agent()` 是 CLI 和 `POST /chat` 共用的业务入口。
- `ToolStrategy(StructuredLearningSuggestion)` 让最终结果具备固定字段。
- provider、网络和结构化结果失败会明确返回失败，而不会伪装成成功建议。

相关代码：

```text
app/langchain_agent.py
app/cli.py
app/api.py
tests/test_langchain_agent.py
```

## 2. Stage 5 要解决的核心问题

Stage 5 不是“换一个库调用模型”。它解决的是直接 LLM 调用在资料、能力和入口增加后会遇到的边界问题。

| 问题 | 处理方式 | 结果 |
| --- | --- | --- |
| 每次都把档案和全部笔记拼进 prompt | 将资料读取拆成工具 | Agent 可按问题决定读取什么 |
| 一个函数同时查询档案、笔记和规则 | 按查询职责拆成三个工具 | 参数、描述和返回值更清楚 |
| 普通文本难以供 CLI、API 和测试稳定复用 | 使用 `StructuredLearningSuggestion` | 入口共享同一输出契约 |
| CLI 和 API 各自创建、调用 Agent | 复用 `run_structured_learning_agent()` | 调用链和错误语义不分叉 |
| 部分 OpenAI-compatible provider 不接受强制工具选择 | 在模型适配层放宽该参数 | 兼容逻辑不污染业务入口 |
| 真模型调用不稳定且有成本 | 测试使用 fake Agent / fake model | 单元测试可重复、无网络依赖 |

## 3. Agent 和直接 LLM 调用有什么区别

直接 LLM 调用的流程是应用先准备完整上下文，再要求模型回答：

```text
load_student()
-> build_structured_learning_suggestion_messages(student)
-> 模型
-> StructuredLearningSuggestion
```

Agent 的流程是应用只给出任务和可用能力。模型可以在执行中请求工具，再依据工具结果继续生成：

```text
question
-> Agent 看到动态 prompt 与工具定义
-> 模型决定是否调用工具
-> 工具读取数据并返回结果
-> Agent 生成最终结构化结果
```

两者都合理，适用条件不同。只有固定输入、固定上下文的任务，直接调用更简单；需要按问题选择外部能力时，Agent 才有意义。

## 4. `create_agent()` 组装了什么

当前结构化 Agent 的创建方式可以概括为：

```python
create_agent(
    model=current_model,
    tools=current_tools,
    middleware=LEARNING_AGENT_MIDDLEWARE,
    response_format=ToolStrategy(StructuredLearningSuggestion),
)
```

每个部分的职责不同：

| 部分 | 作用 |
| --- | --- |
| `model` | 负责理解问题、选择工具并生成结果 |
| `tools` | 定义模型允许调用的外部能力 |
| `middleware` | 用 `@dynamic_prompt` 生成 prompt，并用 `@wrap_tool_call` 保护工具调用边界 |
| `response_format` | 约束最终结果为可验证的学习建议结构 |

`create_agent()` 创建的是已配置好的 Agent。调用时不需要在 API 或 CLI 中重新声明工具、重写工具循环或重复拼 prompt。

## 5. `@dynamic_prompt` 和本次用户问题如何分工

`@dynamic_prompt` 在每次模型调用前执行，描述长期规则，并可以根据 Agent state 补充动态约束：

```text
你是谁
可以调用什么工具
什么时候应该读取档案或笔记
工具只能读取，不能修改数据
回答必须使用中文
```

`invoke()` 时只传本次动态问题：

```python
agent.invoke(
    {"messages": [{"role": "user", "content": f"用户问题：{question}"}]}
)
```

因此，下列信息不应该混在同一个位置：

| 内容 | 放置位置 |
| --- | --- |
| 助教的稳定职责和基于会话的动态约束 | `@dynamic_prompt` |
| 当前用户想问什么 | user message |
| 学员档案、笔记、离线建议 | 工具调用结果 |

这也是为什么 `POST /chat` 先接收 HTTP 请求，再让 Agent 按需读取学员数据。API 是入口层；读取哪些数据属于 Agent 的工具决策。

## 6. 为什么把 Python 函数包装成工具

Stage 5 中的查询工具直接在定义处用装饰器声明：

```python
@tool
def read_current_student_profile(include_notes: bool = True) -> str:
    """读取本地 JSON 中的当前学员档案；可按需包含学习笔记，且不会修改任何文件。"""
    student = load_student()
    return format_student_profile_for_tool(student, include_notes=include_notes)
```

`@tool` 从函数名、类型标注和 docstring 生成名称、参数 schema 与说明；不再额外手写包装和注册代码。

工具名称、说明、参数和返回值共同构成模型选择工具时看到的契约。函数能被 Python 调用，不代表模型知道何时该调用它；描述不清楚会导致模型误用、漏用或传错参数。

## 7. `@wrap_tool_call` 为什么不写进工具函数

工具函数负责读取数据；失败策略属于 Agent 调用边界。项目将两者分开：

```python
@wrap_tool_call
def recover_from_learning_tool_error(request, handler) -> ToolMessage:
    try:
        return handler(request)
    except (OSError, ValueError):
        return ToolMessage(
            content="读取本地学习资料失败，无法据此给出可靠建议。请告知用户稍后重试。",
            tool_call_id=request.tool_call["id"],
        )
```

这样每个 `@tool` 仍只表达业务能力，而 middleware 统一把本地读取失败转换为与当前 tool call 关联的安全结果。它不能代替权限校验，也不应该吞掉模型、provider 或结构化输出错误。

## 8. 多工具和只读边界

项目把工具拆成：

| 工具 | 用途 | 写入行为 |
| --- | --- | --- |
| `read_current_student_profile` | 查询姓名、目标、Python 水平，可选携带笔记 | 无 |
| `read_recent_learning_notes` | 查询最近 1 到 10 条笔记 | 无 |
| `build_current_rule_based_suggestion` | 读取当前水平对应的离线建议 | 无 |

这里的重点不是“工具越多越好”，而是职责清晰。把所有查询塞进一个大工具会让输入、输出和描述失去边界，模型也难以判断真正需要什么。

当前阶段全部只读是刻意的安全限制。写入型工具需要额外处理确认、幂等、权限、审计和失败恢复；这些尚未进入 Stage 5。

## 9. `agent.invoke()` 之后发生了什么

```python
current_agent = agent or create_structured_learning_agent(settings=settings)
result = current_agent.invoke({"messages": build_learning_agent_messages(question)})
```

这里的 `agent` 参数可用于测试注入 fake Agent。正常运行时没有传入 `agent`，才会创建真实 Agent。

`invoke()` 的结果不是只有一段最终文本。对于结构化 Agent，项目会从结果状态中取出：

```python
result["structured_response"]
```

随后由 `extract_structured_agent_response()` 统一处理，避免 CLI 和 API 各自猜测模型返回内容。

## 10. 结构化输出为什么使用 `ToolStrategy`

自由文本适合人阅读，但程序还要继续处理时不可靠。例如 CLI 需要格式化行动项，API 需要稳定 JSON，测试需要构造可比较的预期结果。

项目的目标结构是：

```python
class StructuredLearningSuggestion(BaseModel):
    summary: str
    suggestions: list[LearningSuggestionItem]
    next_checkpoint: str
```

`ToolStrategy(StructuredLearningSuggestion)` 告诉 LangChain：最终需要符合这个 schema 的结构化响应。对于没有原生结构化输出能力、但支持工具调用的模型，这种策略会通过工具调用实现结构化输出。

不要把它理解成“模型永远不会出错”。schema 仍然是契约，代码仍要检查最终 state 是否包含合格的 `structured_response`。

## 11. `structured_response` 为什么还要校验

项目处理结果时区分两种合法情况：

```python
if isinstance(structured_response, StructuredLearningSuggestion):
    return structured_response

if isinstance(structured_response, Mapping):
    return StructuredLearningSuggestion.model_validate(structured_response)
```

这层校验解决了两个问题：

- LangChain 已经返回 Pydantic 实例时直接复用。
- LangChain 返回字典时，重新用项目的 Pydantic 模型确认字段和业务约束。

如果结果不存在或不符合模型，抛出 `ValueError`。`POST /chat` 会把它转换为 `503`，而不是编造一个看似成功的规则建议。

## 12. Provider 兼容性为什么放在模型适配层

LangChain 对结构化输出可能传递 `tool_choice="required"` 或 `"any"`，意思是要求模型调用工具。部分 Ark coding 兼容端点会拒绝这些值。

项目通过 `VolcengineCompatibleChatOpenAI` 覆盖 `bind_tools()`：

```python
if isinstance(tool_choice, str) and tool_choice in {"any", "required"}:
    tool_choice = None

return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)
```

`None` 不是“required 不可被赋值”，而是省略这项 provider 参数，让端点使用默认工具选择方式。代价是失去强制工具调用的保证；收益是请求不会因不兼容参数直接失败。

把这个处理留在模型适配层，能保证 API、CLI 和工具函数仍然使用同一业务逻辑，且不影响支持该参数的 provider。

## 13. 为什么 CLI 和 FastAPI 复用同一入口

项目复用的是：

```python
run_structured_learning_agent(question)
```

而不是让两处入口各自写：

```text
创建模型
用注解声明工具和 middleware
创建 Agent
invoke
解析结构化结果
```

统一入口的收益：

- 新增工具或修改 `@dynamic_prompt` 时，只改一处。
- CLI 和 API 得到同一份 `StructuredLearningSuggestion` 契约。
- provider、网络和结果解析的异常可以统一映射。
- 测试可以直接给入口注入 fake Agent。

CLI 有一个额外步骤：调用前先 `save_student(student)`。因为 CLI 内存字典和工具读取的 `data/student.json` 是两份状态视图；不先保存，工具可能读到旧数据。

## 14. `/ai/suggestion` 和 `/chat` 的边界

这两个接口都会生成学习建议，但不是同一条能力路径：

| 接口 | 调用方式 | 资料读取方式 | `source` |
| --- | --- | --- | --- |
| `POST /ai/suggestion` | Stage 4 直接 LLM 调用 | API 先读取完整学员资料并组装 prompt | `ai` |
| `POST /chat` | Stage 5 LangChain Agent | Agent 根据问题调用多个只读工具 | `agent` |

保留两条路径是为了保留已经验证的 Stage 4 能力，并让学习者清楚比较“应用预先提供上下文”和“模型按需调用工具”的差别。

## 15. 错误语义与测试隔离

`POST /chat` 的错误边界如下：

| 场景 | 状态码 | 处理位置 |
| --- | --- | --- |
| 缺少 `question` 或空字符串 | `422` | FastAPI / Pydantic 请求模型 |
| `question` 只有空白 | `400` | 路由业务校验 |
| API Key、网络、provider 或结构化结果失败 | `503` | Agent 调用边界 |

`responses={400: ..., 503: ...}` 负责声明 OpenAPI 文档；`raise HTTPException(status_code=...)` 才是在运行时真正返回错误。

测试不请求真实 provider。它们用 `monkeypatch.setattr()` 把 API 模块中的 `run_structured_learning_agent` 临时替换成 fake 函数，验证问题传递、响应模型、错误映射，以及工具和 middleware 装配。测试结束后 pytest 会自动还原替换。

## 16. 当前数据流

### CLI 入口

```text
CLI 选项 4
-> save_student(student)
-> run_structured_learning_agent()
-> Agent 按需调用只读工具
-> data/student.json
-> StructuredLearningSuggestion
-> format_agent_suggestion()
```

### FastAPI 入口

```text
POST /chat {"question": "我今天应该先练什么？"}
-> ChatRequest 校验
-> run_structured_learning_agent(question)
-> Agent 按需调用只读工具
-> data/student.json
-> AgentChatResponse
```

注意：示例响应里的 `summary`、行动建议和检查点在真实运行时由模型生成；它们不是 API 写死的文案。`source="agent"` 和响应字段结构才是代码固定的接口契约。

## 17. Stage 5 的已知限制

当前阶段没有：

- RAG：Agent 不读取 `materials/`，也不做文档切分、embedding 或检索。
- 对话记忆：`POST /chat` 是单轮请求，不保存聊天历史。
- 写工具：Agent 不会改学员档案、笔记或文件。
- streaming：API 等 Agent 完成后一次性返回最终 JSON。
- LangGraph：没有显式 State、节点、条件分支或 checkpoint。
- Deep Agents：没有规划、文件系统任务、子 Agent 或长任务管理。

这些不是遗漏，而是课程分阶段控制的边界。先把模型、工具、结构化结果和错误语义稳定下来，后续再增加检索、状态图和长任务能力。

## 18. 常见误解与排查

### 以为 `/chat` 会先在 API 中读取学员数据

不是。`/chat` 只接收并校验 `question`，再调用统一 Agent 入口。学员档案和笔记由 Agent 工具在执行过程中按需读取。

### 以为成功响应示例中的文案是写死的

不是。示例 JSON 说明的是响应 shape；真实的 `summary`、建议内容和时间由模型生成，并受结构化 schema 校验。

### 以为 `ToolStrategy` 等于无需校验

不对。它帮助模型按 schema 返回结果，但调用方仍应验证 `structured_response` 是否存在且符合项目模型。

### 以为 `responses` 会自动返回 400 或 503

不对。`responses` 用于 OpenAPI 文档声明；路由仍要显式抛出 `HTTPException`。

### 以为 Agent 失败时应该静默返回规则建议

不对。规则建议和 Agent 建议是不同能力。`/chat` 失败返回 `503`，调用方可以显式决定是否改请求 `GET /suggestion`。

### 以为工具越多、工具越大越好

不对。工具应按清晰职责设计。当前三个工具覆盖档案、近期笔记和规则建议，已经足以说明多工具选择；没有必要过早加入写入、RAG 或外部系统操作。

## 19. LangChain v1 阅读要点

以下要点与当前项目直接对应：

1. Agent 由模型和工具组成；`create_agent()` 用统一入口创建可调用 Agent，适合把工具调用循环留在框架层。
2. 工具的名称、说明、参数和返回值是模型的可用能力说明，设计时应保证职责清晰、输入输出可预测。
3. `response_format` 可以要求结构化最终结果。模型支持 provider 原生结构化输出时，框架可采用 provider strategy；不支持时，可通过 `ToolStrategy` 利用工具调用完成结构化输出。
4. 结构化输出会出现在 Agent 结果的 `structured_response` 中，应用仍需要把它转换或校验为自己的领域模型。
5. 工具调用与结构化输出的失败要有显式处理策略；当前项目把无法获得可靠 Agent 结果的情况暴露为 `503`。
6. LangChain 解决模型、消息和工具编排；RAG、长期记忆、复杂流程状态和长任务规划要按需要引入相应能力，不能因为 Agent 已能调用工具就混为一谈。

阅读来源：

- 中文参考（按本项目材料保留）：<https://langchain-doc.cn/v1/python/langchain>
- 中文页面的 Agent 说明：<https://langchain-doc.cn/v1/python/langchain/agents.html>
- 中文页面的结构化输出说明：<https://langchain-doc.cn/v1/python/langchain/structured-output.html>
- 官方 Agent 文档：<https://docs.langchain.com/oss/python/langchain/agents>
- 官方结构化输出文档：<https://docs.langchain.com/oss/python/langchain/structured-output>

中文参考站与官方文档可能在版本和示例上不同。项目代码以锁定的 `langchain==1.3.12`、本仓库测试和官方文档中的稳定概念为准。

## 20. 自测问题

1. 为什么 Stage 5 不把完整学员档案继续直接拼进每一次 user message？
2. `@dynamic_prompt`、user message 和工具结果各自应该承载什么信息？
3. 为什么当前三个工具全部是只读工具？
4. `ToolStrategy(StructuredLearningSuggestion)` 和 `structured_response` 分别解决什么问题？
5. 为什么 `structured_response` 是字典时还要调用 `model_validate()`？
6. 为什么 `POST /chat` 和 `POST /ai/suggestion` 应并存？
7. 为什么 Ark 的 `tool_choice` 兼容处理不应散落在 API 或工具函数中？
8. 为什么自动化测试要使用 fake Agent，而不是调用真实 provider？

## 21. 验证命令

在 `ai-learning-assistant/` 目录中运行：

```powershell
py -3.13 -m pytest tests/test_langchain_agent.py tests/test_cli.py tests/test_api.py
py -3.13 -m pytest
py -3.13 -c "from app.langchain_agent import build_learning_agent_tools; print([item.name for item in build_learning_agent_tools()])"
py -3.13 -c "from app.api import app; print(sorted(app.openapi()['paths']['/chat']['post']['responses']))"
```

真实 Agent demo 还需要可用的 `.env` provider 配置：

```powershell
py -3.13 -m app.langchain_structured_agent_demo
```

没有配置 provider 时，不应把 demo 失败误判为单元测试失败。
