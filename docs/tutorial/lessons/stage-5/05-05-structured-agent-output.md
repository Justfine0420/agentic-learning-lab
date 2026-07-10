# 第 5.5 课：结构化 Agent 输出

## 1. 本课目标

第 5.4 课已经把 LangChain Agent 从单工具扩展到多工具：

```text
read_current_student_profile
read_recent_learning_notes
build_current_rule_based_suggestion
```

但 Agent 最终回答仍然是普通文本。普通文本适合人阅读，却不适合后续 CLI、FastAPI、RAG、LangGraph 或 Deep Agents 继续处理。

这一节要把 LangChain Agent 的最终结果升级为结构化对象：

```text
StructuredLearningSuggestion
```

你会学到：

- 为什么 Agent 最终输出不能长期停留在普通字符串。
- LangChain `response_format` 和 `structured_response` 的关系。
- 为什么这里选择 `ToolStrategy`，而不是直接依赖 provider-native 结构化输出。
- 如何复用 Stage 4 已有的 Pydantic 模型。
- 如何从 Agent 返回 state 中提取结构化结果。
- 如何为结构化 Agent 加离线测试和手动 demo。
- 为什么 streaming 继续后置处理。

## 2. 你会新增什么项目能力

完成后，项目会多一条结构化 Agent 路径：

```text
用户问题
-> LangChain Agent
-> 调用只读工具
-> 生成 StructuredLearningSuggestion
```

结构化结果包含：

```text
summary
suggestions[]
next_checkpoint
```

也就是说，后续 CLI 不必从一段自然语言里猜“摘要在哪里、行动建议有几条、下一步是什么”。它可以直接读取字段。

当前保留两条 Agent 路径：

| 路径 | 返回值 | 用途 |
| --- | --- | --- |
| `run_learning_agent()` | `str` | 文本 demo 和调试 |
| `run_structured_learning_agent()` | `StructuredLearningSuggestion` | 后续 CLI / API 接入基础 |

## 3. 前置知识

开始前需要理解：

- Stage 4.4 已经定义了 `StructuredLearningSuggestion`。
- Stage 4.5 已经让普通 LLM 调用返回结构化 AI 建议。
- Stage 5.4 已经给 Agent 注册了多个只读工具。
- `create_agent()` 可以接收 `tools` 和 `system_prompt`。
- LangChain Agent 最终返回的是一个 state，而不是单纯字符串。

Stage 4 的结构化输出是直接调用模型：

```text
应用代码 -> 模型 -> JSON -> Pydantic
```

Stage 5 的结构化 Agent 输出多了一层 Agent：

```text
应用代码 -> Agent -> 工具调用 -> 模型 -> structured_response -> Pydantic
```

## 4. 核心概念

### 普通文本的问题

普通文本看起来简单：

```text
建议你今天先复习函数，然后做一个小练习。
```

但程序很难稳定处理它。比如 CLI 想展示成固定格式：

```text
摘要：
1. 行动建议
下一检查点：
```

如果只拿到一段自然语言，就只能靠字符串切分或正则猜结构。这个做法很脆，模型稍微换一种说法就会坏。

结构化输出把返回格式变成契约：

```python
class StructuredLearningSuggestion(BaseModel):
    summary: str
    suggestions: list[LearningSuggestionItem]
    next_checkpoint: str
```

这才适合继续接 CLI、API 和后续流程。

### `response_format` 是什么

LangChain 的 `create_agent()` 支持 `response_format` 参数。

它的作用是告诉 Agent：

```text
最终结果要按指定 schema 返回。
```

当 Agent 成功生成结构化结果时，最终 state 中会出现：

```python
result["structured_response"]
```

这一节只从 `structured_response` 读取最终结果，不解析中间消息。

### 为什么使用 `ToolStrategy`

LangChain 有不同的结构化输出策略。当前项目接入的是 OpenAI-compatible provider：

```text
DeepSeek
火山引擎 Ark Agent Plan
Ollama OpenAI compatible endpoint
```

这些 provider 的原生结构化输出能力、工具调用兼容度和错误形态可能不完全一致。

这里使用：

```python
ToolStrategy(StructuredLearningSuggestion)
```

含义是：让结构化输出通过工具调用策略完成，尽量减少对 provider-native JSON 能力的依赖。

这样更符合当前课程阶段：先让 Agent 输出结构稳定，再逐步处理不同 provider 的能力差异。

注意：`ToolStrategy` 会要求模型调用结构化输出工具。部分 OpenAI-compatible provider 不接受
`tool_choice="required"` 这类强制工具选择参数。当前项目对火山引擎 Ark coding / Agent Plan 路径使用
`VolcengineCompatibleChatOpenAI` 包装层，去掉这个强制参数，保留工具列表，让模型自行选择工具。

### Streaming 继续后置

结构化输出解决的是“最终结果是什么”。

Streaming 解决的是“过程如何实时输出”。

这两个问题不要混在一起处理。当前顺序是：

```text
5.5：稳定最终结构化结果。
5.6：CLI 使用非 streaming 响应接入结构化 Agent。
5.7：FastAPI 使用非 streaming 响应接入结构化 Agent。
8.2：进入 LangGraph streaming。
```

后续做 streaming 时，需要同时处理 token、工具调用事件、工具结果事件和 API 事件格式。等最终结构稳定后再做，测试和课程节奏都会更稳。

## 5. 代码实现

### 第一步：导入结构化输出策略和 Pydantic 模型

打开：

```text
ai-learning-assistant/app/langchain_agent.py
```

新增导入：

```python
from langchain.agents.structured_output import ToolStrategy
from app.models import StructuredLearningSuggestion, Student
```

`StructuredLearningSuggestion` 来自 Stage 4。

它已经被普通 LLM 调用和 `POST /ai/suggestion` 使用过，这里继续复用，不再发明第二套结构。

### 第二步：新增结构化 Agent prompt

新增：

```python
STRUCTURED_LEARNING_AGENT_SYSTEM_PROMPT = (
    LEARNING_AGENT_SYSTEM_PROMPT
    + "最终结果必须形成结构化学习建议，包括摘要、1 到 3 条行动建议和下一检查点。"
)
```

这里不是替换原来的 prompt，而是为结构化路径追加约束。

旧的 `LEARNING_AGENT_SYSTEM_PROMPT` 仍然服务普通文本 demo。

### 第三步：定义结构化响应格式

新增：

```python
STRUCTURED_RESPONSE_TOOL_MESSAGE = "已生成结构化学习建议。"


def build_learning_agent_response_format() -> Any:
    return ToolStrategy(
        StructuredLearningSuggestion,
        tool_message_content=STRUCTURED_RESPONSE_TOOL_MESSAGE,
    )
```

这段代码做了两件事：

- 指定最终 schema 是 `StructuredLearningSuggestion`。
- 指定结构化输出工具调用完成后的工具消息内容。

`tool_message_content` 不是最终给用户看的学习建议，它是 LangChain 内部结构化输出工具消息的简短说明。

### 第四步：创建结构化 Agent

新增：

```python
def create_structured_learning_agent(
    *,
    settings: LLMSettings | None = None,
    model: Any | None = None,
    tools: list[Any] | None = None,
    response_format: Any | None = None,
) -> Any:
    current_model = model or build_langchain_chat_model(settings)
    current_tools = tools if tools is not None else build_learning_agent_tools()
    current_response_format = (
        response_format if response_format is not None else build_learning_agent_response_format()
    )

    return create_agent(
        model=current_model,
        tools=current_tools,
        system_prompt=STRUCTURED_LEARNING_AGENT_SYSTEM_PROMPT,
        response_format=current_response_format,
    )
```

注意这个函数没有删除 `create_learning_agent()`。

原因是两条路径的用途不同：

- 普通 Agent 用来观察文本回答。
- 结构化 Agent 用来承接后续 CLI / API。

### 第五步：提取 `structured_response`

新增：

```python
def extract_structured_agent_response(agent_result: Mapping[str, Any]) -> StructuredLearningSuggestion:
    structured_response = agent_result.get("structured_response")

    if isinstance(structured_response, StructuredLearningSuggestion):
        return structured_response

    if isinstance(structured_response, Mapping):
        return StructuredLearningSuggestion.model_validate(structured_response)

    raise ValueError("LangChain agent result did not contain structured_response.")
```

这里允许两种情况：

- LangChain 已经返回 Pydantic 实例。
- 测试或兼容路径返回普通 dict。

如果没有 `structured_response`，直接报错。不要悄悄退回普通文本，否则后续 CLI / API 会以为结构化结果可用。

### 第六步：运行结构化 Agent

新增：

```python
def run_structured_learning_agent(
    question: str = DEFAULT_AGENT_QUESTION,
    *,
    settings: LLMSettings | None = None,
    agent: Any | None = None,
) -> StructuredLearningSuggestion:
    current_agent = agent or create_structured_learning_agent(settings=settings)
    result = current_agent.invoke({"messages": build_learning_agent_messages(question)})
    return extract_structured_agent_response(result)
```

这个函数会成为 5.6 CLI 接入的核心入口。

### 第七步：新增结构化 demo

新建：

```text
ai-learning-assistant/app/langchain_structured_agent_demo.py
```

内容：

```python
from app.langchain_agent import DEFAULT_AGENT_QUESTION, run_structured_learning_agent


def main() -> None:
    suggestion = run_structured_learning_agent(DEFAULT_AGENT_QUESTION)
    print(suggestion.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
```

手动运行后会打印 JSON。

这条命令需要真实 provider 可用，并且 provider 支持当前结构化输出策略所需的工具调用能力。

### 第八步：补充测试

更新：

```text
ai-learning-assistant/tests/test_langchain_agent.py
```

新增测试覆盖：

- `build_learning_agent_response_format()` 返回 `ToolStrategy`。
- `create_structured_learning_agent()` 会把 `response_format` 传给 `create_agent()`。
- `extract_structured_agent_response()` 可以接收 Pydantic 实例。
- `extract_structured_agent_response()` 可以校验 dict。
- 缺少 `structured_response` 时会报错。
- `run_structured_learning_agent()` 会调用 Agent 并返回结构化结果。

新增：

```text
ai-learning-assistant/tests/test_langchain_structured_agent_demo.py
```

用于验证 demo 会打印结构化 JSON。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

运行 LangChain 相关测试：

```powershell
py -3.13 -m pytest tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

运行全量测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

手动运行结构化 Agent demo：

```powershell
py -3.13 -m app.langchain_structured_agent_demo
```

如果 provider 没有配置、网络不可用、模型不支持工具调用或结构化结果不满足 Pydantic 约束，这条手动命令可能失败。自动化测试不会调用真实 provider。

## 7. 常见错误

### 忽略 provider 工具调用兼容性

OpenAI-compatible 不等于每个参数都和 OpenAI 官方完全一致。

例如当前火山引擎 Ark coding 端点可以接受普通 `tools`，但不接受 LangChain `ToolStrategy` 默认强制出的
`tool_choice="required"`。所以项目里保留了一个很窄的兼容包装层，只调整这个参数，不改业务工具和结构化模型。

### 继续解析普通文本

结构化 Agent 已经提供 `structured_response`。

不要再从最后一条 message 里切字符串，也不要写正则解析摘要和行动建议。

### 重新定义一套结构

不要新增 `AgentSuggestion`、`LangChainSuggestion` 之类的重复模型。

Stage 4 已经有 `StructuredLearningSuggestion`，继续复用它。这样 CLI、API、Agent 的返回结构才能保持一致。

### 把缺少 `structured_response` 当成普通文本处理

缺少 `structured_response` 说明结构化 Agent 没按预期完成。

正确做法是抛出明确错误，而不是退回普通文本。

### 提前接入 CLI

CLI 接入会带来菜单、错误提示、展示格式和 provider 不可用时的用户体验问题。

结构化返回路径稳定后再接 CLI，能减少入口层返工。

### 提前实现 streaming

Streaming 是过程事件输出。结构化输出是最终结果契约。

先稳定最终结果，再处理过程事件流。

## 8. 练习

练习 1：解释 `run_learning_agent()` 和 `run_structured_learning_agent()` 的返回值有什么区别。

练习 2：阅读 `StructuredLearningSuggestion`，说明每个字段适合在 CLI 中展示在哪里。

练习 3：把 `extract_structured_agent_response()` 的输入改成缺少 `structured_response` 的 dict，观察错误信息。

练习 4：解释为什么这里使用 `ToolStrategy` 能降低 provider-native 结构化输出差异带来的学习成本。

练习 5：手动运行：

```powershell
py -3.13 -m app.langchain_structured_agent_demo
```

观察真实 provider 返回的结构化 JSON。

## 9. 验收标准

完成后，你应该能做到：

- 解释普通文本输出为什么不适合后续 CLI / API。
- 说清楚 `response_format` 的作用。
- 说清楚 `structured_response` 在 Agent final state 中的位置。
- 看懂 `ToolStrategy(StructuredLearningSuggestion)`。
- 看懂 `create_structured_learning_agent()`。
- 看懂 `extract_structured_agent_response()`。
- 运行 LangChain 相关测试通过。
- 运行全量测试通过。
- 解释为什么 streaming 仍然后置处理。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

结构化 Agent 输出是入口接入前的最后一道数据契约。

| 当前内容 | 后续升级 |
| --- | --- |
| `StructuredLearningSuggestion` | 5.6 CLI 可以稳定展示摘要、行动建议和检查点 |
| `structured_response` | 5.7 FastAPI 可以直接返回结构化 JSON |
| `ToolStrategy` | 后续可对比 provider-native structured output |
| 缺少结构化结果时抛错 | API 层可以转成明确错误响应 |
| 最终结果先稳定 | LangGraph streaming 再处理过程事件 |

Deep Agents 阶段也会依赖结构化结果。

长期任务不是只返回一段文本，而是要返回计划、文件路径、子任务结果、风险和总结。现在先从学习建议这个小结构开始。

## 11. 本课变更清单

新增文件：

- `ai-learning-assistant/app/langchain_structured_agent_demo.py`
- `ai-learning-assistant/tests/test_langchain_structured_agent_demo.py`
- `docs/tutorial/lessons/stage-5/05-05-structured-agent-output.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/langchain_agent.py`
- `ai-learning-assistant/tests/test_langchain_agent.py`

代码变更：

- 新增 `STRUCTURED_LEARNING_AGENT_SYSTEM_PROMPT`。
- 新增 `STRUCTURED_RESPONSE_TOOL_MESSAGE`。
- 新增 `build_learning_agent_response_format()`。
- 新增 `create_structured_learning_agent()`。
- 新增 `extract_structured_agent_response()`。
- 新增 `run_structured_learning_agent()`。
- 新增结构化 Agent demo。
- 增加结构化 Agent 相关测试。

依赖变更：

- 无。继续使用第 5.2 课引入的 `langchain==1.3.12` 和 `langchain-openai==1.3.4`。

环境变量变更：

- 无。

官方文档核对：

- [LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output)
- [LangChain streaming](https://docs.langchain.com/oss/python/langchain/streaming)

下一步：

- 第 5.6 课：CLI 接入 LangChain Agent。
- 用 `run_structured_learning_agent()` 给 CLI 增加一个稳定的 Agent 建议入口。
- CLI 仍先使用非 streaming 响应，不实现 streaming。
