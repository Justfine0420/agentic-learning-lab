# 第 5.4 课：多工具调用

## 1. 本课目标

第 5.3 课里，我们已经把一个 Python 函数包装成 LangChain 工具：

```text
read_current_student_profile
```

但只有一个工具时，Agent 还谈不上“选择”。

本课要把 Agent 升级为多工具 Agent，让它可以在多个只读工具之间选择：

```text
read_current_student_profile
read_recent_learning_notes
build_current_rule_based_suggestion
```

本课目标是让你学会：

- 如何组织多个 LangChain tools。
- 如何避免一个工具做太多事。
- 如何给每个工具划清职责边界。
- 如何让 Agent 既能查档案，也能查最近笔记，还能获取离线规则建议。
- 如何用测试验证工具列表、工具边界和工具行为。
- 为什么多工具阶段仍然不做 FastAPI `/chat`、RAG、结构化 Agent 输出或 streaming。

本课仍然坚持只读工具。

不写文件、不改资料、不新增接口。

## 2. 你会新增什么项目能力

完成本课后，LangChain Agent 的工具箱会从：

```text
1 个工具：查询当前学员档案
```

升级为：

```text
3 个工具：
1. 查询当前学员档案
2. 查询最近学习笔记
3. 生成离线规则建议
```

也就是说，Agent 可以把一个学习建议任务拆成多个信息来源：

```text
用户问题
-> 查询学员档案
-> 查询最近学习笔记
-> 查询离线规则建议
-> 综合回答
```

这就是 tool calling 开始有价值的地方。

Agent 不再只是“有一个外部能力”，而是开始面对“什么时候用哪个工具”的问题。

## 3. 前置知识

开始前，你应该已经理解：

- `load_student()` 会读取 `data/student.json`。
- `build_suggestion()` 会根据 Python 水平生成离线规则建议。
- `tool(...)(function)` 可以把 Python 函数包装成 LangChain tool。
- `create_agent(..., tools=[...])` 会把工具列表交给 Agent。
- 第 5.3 课里的工具是只读工具。

还要记住：

```text
多工具不是把所有逻辑塞进一个巨大函数。
多工具是把清晰的小能力暴露给 Agent，让模型自己选择调用路径。
```

## 4. 核心概念

### 为什么要拆多个工具

你当然可以写一个超级工具：

```text
get_everything_about_student()
```

它一次返回：

- 学员档案
- 所有笔记
- 离线建议
- 未来学习计划
- 资料检索结果

这看起来省事，但会让 Agent 失去选择能力。

更好的做法是按职责拆小：

| 工具 | 职责 |
| --- | --- |
| `read_current_student_profile` | 查询姓名、目标、Python 水平，可选包含笔记 |
| `read_recent_learning_notes` | 查询最近 N 条学习笔记 |
| `build_current_rule_based_suggestion` | 根据当前 Python 水平生成离线规则建议 |

这样模型可以根据问题选择工具。

例如：

```text
“我是什么水平？”
```

更适合调用：

```text
read_current_student_profile
```

而：

```text
“结合我最近的笔记给建议”
```

更适合组合调用：

```text
read_current_student_profile
read_recent_learning_notes
build_current_rule_based_suggestion
```

### 为什么继续只读

本课仍然不做写操作。

原因不是写工具难，而是写工具的风险完全不同。

读工具失败，最多是回答不完整。

写工具失败，可能会：

- 覆盖用户资料。
- 删除学习笔记。
- 写入错误计划。
- 造成用户误以为数据已经保存。

写操作需要更严格的边界：

```text
确认机制
错误恢复
幂等设计
审计记录
人类介入
```

这些会更适合放到后续 LangGraph / Deep Agents 阶段。

### Streaming 的后置处理边界

Streaming 属于过程事件输出能力，不是多工具调用的前置条件。
在 Stage 5 当前阶段，课程重点仍然是建立 LangChain Agent 的基础能力：

| 小节 | 当前重点 |
| --- | --- |
| 5.2 | 最小 Agent |
| 5.3 | 第一个工具 |
| 5.4 | 多工具选择 |
| 5.5 | 结构化最终输出 |
| 后续入口接入 | CLI / FastAPI 使用稳定结果 |

Streaming 会引入额外的过程事件层，例如：

```text
模型 token 流
工具调用事件
工具返回事件
```

如果在多工具边界尚未稳定时提前实现 streaming，课程会同时混入几类问题：

- 最终 JSON 如何解析。
- token 流中间态是不是合法 JSON。
- 工具调用事件如何展示。
- API 如何返回流式事件。
- 测试如何稳定断言流式输出。

这些问题都重要，但它们不应该抢占本课的核心目标。
本课只处理多工具选择和工具职责边界；streaming 后置到结构化输出、入口接入和 API 边界稳定之后再实现。

本课程采用的顺序是：

```text
5.5：先稳定 Agent 的结构化最终输出。
后续入口接入：CLI / FastAPI 先使用普通响应。
LangGraph 进阶阶段：系统学习并实现 streaming。
```

这样可以先保证最终结果可解析、可测试、可接入，再处理过程事件如何实时输出。

## 5. 代码实现

### 第一步：导入离线规则建议函数

打开：

```text
ai-learning-assistant/app/langchain_agent.py
```

新增：

```python
from app.suggestions import build_suggestion
```

这个函数来自 Stage 3。

它根据 `python_level` 返回离线建议，不依赖模型 provider。

### 第二步：更新 system prompt

第 5.3 课的 prompt 只说有一个只读工具。

本课改成多个只读工具：

```python
LEARNING_AGENT_SYSTEM_PROMPT = (
    "你是一个 Python 和 AI Agent 学习助教。"
    "你会根据学员档案、学习目标和笔记，给出清晰、可执行的学习建议。"
    "你现在有多个只读工具，可以查询当前保存在本地 JSON 中的学员档案、最近学习笔记和离线规则建议。"
    "当你需要了解学员姓名、目标、Python 水平、学习笔记或基础建议时，优先调用合适的工具。"
    "不要编造本地文件里的内容。"
    "回答必须使用中文。"
)
```

这里的重点是：

```text
调用合适的工具
```

因为从本课开始，Agent 不再只有一个选择。

### 第三步：更新默认问题

修改：

```python
DEFAULT_AGENT_QUESTION = "请先查询当前学习档案、最近笔记和离线规则建议，再生成今天的学习建议。"
```

这个默认问题是 demo 用的。

它会引导真实模型尝试组合多个工具。

### 第四步：增加笔记条数边界

新增：

```python
def normalize_note_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 10:
        return 10
    return limit
```

为什么要限制？

因为工具参数来自模型。

模型可能传：

```text
-1
0
999
```

工具应该自己守住边界。

本课把最近笔记条数限制在：

```text
1 到 10
```

### 第五步：格式化最近学习笔记

新增：

```python
def format_recent_notes_for_tool(notes: list[str], *, limit: int = 5) -> str:
    current_limit = normalize_note_limit(limit)
    if not notes:
        return "最近学习笔记：\n暂无笔记"

    recent_notes = notes[-current_limit:]
    lines = [f"最近学习笔记（最多 {current_limit} 条）："]
    lines.extend(f"{index}. {note}" for index, note in enumerate(recent_notes, start=1))
    return "\n".join(lines)
```

注意这里用的是：

```python
notes[-current_limit:]
```

也就是取最后 N 条笔记。

这比返回全部笔记更稳。

### 第六步：新增最近笔记查询函数

新增：

```python
def read_recent_learning_notes(limit: int = 5) -> str:
    """Read recent learner notes from local JSON storage."""
    student = load_student()
    return format_recent_notes_for_tool(student["notes"], limit=limit)
```

它仍然是普通 Python 函数。

下一步才包装成工具。

### 第七步：新增离线规则建议函数

新增：

```python
def build_current_rule_based_suggestion() -> str:
    """Build the current offline rule-based learning suggestion."""
    student = load_student()
    return build_suggestion(student["python_level"])
```

这个工具复用了 Stage 3 的规则建议能力。

它的意义是：

```text
让 Agent 可以把稳定规则建议作为参考，而不是全部依赖模型自由发挥。
```

### 第八步：包装新工具

新增最近笔记工具：

```python
read_recent_learning_notes_tool = tool(
    "read_recent_learning_notes",
    description=(
        "读取当前保存在本地 JSON 文件中的最近学习笔记。参数 limit 表示最多返回几条，"
        "会被限制在 1 到 10 之间。这个工具只读，不会修改任何文件。"
    ),
)(read_recent_learning_notes)
```

新增离线规则建议工具：

```python
build_current_rule_based_suggestion_tool = tool(
    "build_current_rule_based_suggestion",
    description=(
        "根据当前学员的 Python 水平生成离线规则学习建议。这个工具只使用本地规则，"
        "不会调用大模型，也不会修改任何文件。"
    ),
)(build_current_rule_based_suggestion)
```

两个工具都明确写了：

```text
只读
不会修改文件
```

### 第九步：更新工具列表

修改：

```python
def build_learning_agent_tools() -> list[Any]:
    return [
        read_current_student_profile_tool,
        read_recent_learning_notes_tool,
        build_current_rule_based_suggestion_tool,
    ]
```

这个函数现在才真正体现价值。

后续所有 Agent 工具都从这里集中注册。

### 第十步：补充测试

更新：

```text
ai-learning-assistant/tests/test_langchain_agent.py
```

新增测试覆盖：

- `normalize_note_limit()` 会把 limit 限制在 1 到 10。
- `format_recent_notes_for_tool()` 只返回最近 N 条笔记。
- 空笔记时返回“暂无笔记”。
- `read_recent_learning_notes()` 会读取 storage。
- `build_current_rule_based_suggestion()` 会读取当前 Python 水平并生成规则建议。
- `build_learning_agent_tools()` 会返回 3 个工具。
- 最近笔记 tool 可以 `.invoke(...)`。
- 规则建议 tool 可以 `.invoke({})`。
- `create_learning_agent()` 默认带 3 个工具。

本课仍然不让 pytest 调真实模型。

真实 provider 工具选择行为放在手动 demo 中观察。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

运行本课相关测试：

```powershell
py -3.13 -m pytest tests/test_langchain_agent.py tests/test_langchain_agent_demo.py
```

运行全量测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py
```

手动运行 LangChain Agent：

```powershell
py -3.13 -m app.langchain_agent_demo
```

这条命令需要真实 provider 可用。

如果 provider 不支持 tool calling，手动 demo 可能无法按预期调用工具。

这不影响本课的自动化测试，因为测试验证的是工具和 Agent 组装逻辑。

## 7. 常见错误

### 把多个能力塞进一个工具

不要把档案、笔记、建议全塞进一个工具。

这会让工具变成黑箱，模型也失去选择空间。

### 不限制工具参数

`limit` 来自模型，不要相信它一定合理。

本课用：

```python
normalize_note_limit(limit)
```

把它限制在 1 到 10。

### 让规则建议工具调用模型

`build_current_rule_based_suggestion` 是离线规则工具。

它不应该调用 LLM。

如果它又调用模型，就会让“规则建议”和“AI 建议”的边界变乱。

### 在单元测试里断言真实工具调用顺序

工具调用顺序由模型决定。

pytest 不应该测试真实 provider 的行为。

本课测试：

```text
工具函数正确
工具对象可调用
工具列表正确
Agent 创建时带工具
```

真实模型是否先查档案再查笔记，放在人工 demo 观察。

### 提前实现 streaming

不要在本课加 streaming。

当前阶段还没有完成结构化 Agent 最终输出。

先把多工具边界稳定下来，再处理过程事件输出。

## 8. 练习

练习 1：解释为什么 `read_recent_learning_notes` 不应该直接返回所有笔记。

练习 2：把 `limit` 分别设为 `0`、`3`、`99`，观察 `normalize_note_limit()` 的结果。

练习 3：解释 `build_current_rule_based_suggestion` 为什么不应该调用大模型。

练习 4：阅读 `build_learning_agent_tools()`，说明每个工具的职责。

练习 5：手动运行：

```powershell
py -3.13 -m app.langchain_agent_demo
```

观察模型是否尝试组合多个工具。

练习 6：思考一个问题：如果后续要新增“写学习计划到文件”的工具，需要哪些安全边界？

## 9. 验收标准

完成本课后，你应该能做到：

- 解释为什么多工具要拆职责。
- 看懂 `normalize_note_limit()`。
- 看懂 `format_recent_notes_for_tool()`。
- 看懂 `read_recent_learning_notes()`。
- 看懂 `build_current_rule_based_suggestion()`。
- 解释 3 个工具分别什么时候应该被调用。
- 解释为什么本课仍然只做只读工具。
- 解释 streaming 为什么要后置到结构化输出和入口接入之后。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课让 Stage 5 从“单工具 Agent”进入“多工具 Agent”。

| 本课内容 | 后续升级 |
| --- | --- |
| 多个只读工具 | 5.5 结构化 Agent 输出 |
| 最近笔记工具 | 6.x RAG 资料读取前的本地上下文查询基础 |
| 离线规则建议工具 | 后续作为 AI 建议的稳定参考 |
| 工具参数边界 | LangGraph 节点输入校验和 Deep Agents 工具治理 |
| 不做 streaming | 后续 LangGraph streaming 阶段系统实现 |

关于 streaming 的后置顺序：

```text
先稳定最终结构化结果，再处理过程事件流。
```

更稳的路线是：

```text
5.5：先把 Agent 最终输出变成结构化结果。
后续入口接入：CLI / FastAPI 先使用普通响应。
8.2：在 LangGraph 进阶阶段系统学习 Streaming。
```

这样可以先掌握最终结果的稳定结构，再学习过程事件如何流式输出。

Deep Agents 后续也会更依赖这种工具边界。

因为长期任务不是靠一个大 prompt 完成的，而是靠模型在多个工具、文件、子 Agent 和上下文之间做选择。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-5/05-04-multiple-tools.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/langchain_agent.py`
- `ai-learning-assistant/tests/test_langchain_agent.py`

代码变更：

- 新增 `normalize_note_limit()`。
- 新增 `format_recent_notes_for_tool()`。
- 新增 `read_recent_learning_notes()`。
- 新增 `build_current_rule_based_suggestion()`。
- 新增 `read_recent_learning_notes_tool`。
- 新增 `build_current_rule_based_suggestion_tool`。
- `build_learning_agent_tools()` 从 1 个工具扩展到 3 个工具。
- 更新 Agent system prompt 和默认问题。
- 增加多工具相关测试。

依赖变更：

- 无。继续使用第 5.2 课已引入的 `langchain==1.3.12` 和 `langchain-openai==1.3.4`。

环境变量变更：

- 无。

官方文档核对：

- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain streaming](https://docs.langchain.com/oss/python/langchain/streaming)

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest tests/test_langchain_agent.py tests/test_langchain_agent_demo.py
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py
```

下一步：

- 第 5.5 课：结构化 Agent 输出。
- 设计学习计划输出结构。
- 说明 streaming 的拆分边界，但暂不实现真正流式输出。
