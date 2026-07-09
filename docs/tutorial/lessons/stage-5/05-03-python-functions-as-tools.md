# 第 5.3 课：Python 函数变成 LangChain 工具

## 1. 本课目标

第 5.2 课里，我们已经创建了第一个 LangChain Agent，但它还没有工具。

那一课的 Agent 本质上还是：

```text
model + system_prompt + messages
```

本课开始进入 LangChain Agent 的关键能力：

```text
model + system_prompt + messages + tools
```

本课目标是让你学会：

- 什么是 LangChain tool。
- 为什么 tool 本质上就是带说明、参数 schema 和返回值的 Python 函数。
- 如何用 `langchain.tools.tool` 把普通 Python 函数包装成工具。
- 如何把工具传给 `create_agent(..., tools=[...])`。
- 如何让 Agent 从“只读输入消息”升级成“能主动查询当前学员档案”。
- 如何用离线测试验证工具，不依赖真实模型 provider。

本课只做一个工具：

```text
read_current_student_profile
```

它会读取当前 `data/student.json` 中的学员档案，并返回纯文本。

本课不做：

```text
多工具组合
RAG
结构化 Agent 输出
FastAPI /chat
LangGraph
Deep Agents
```

这些会在后续课程逐步加上。

## 2. 你会新增什么项目能力

完成本课后，LangChain Agent 会从“只能基于传入 message 回答”升级为：

```text
用户问题
-> Agent 判断需要学员资料
-> 调用 read_current_student_profile 工具
-> 工具读取 data/student.json
-> Agent 基于工具结果回答
```

也就是说，学员档案不再由外部提前塞进 message。

第 5.2 课的输入方式是：

```text
student + question -> messages
```

第 5.3 课的输入方式变成：

```text
question -> messages
Agent -> tool -> student profile
```

这是一个很关键的变化。

Agent 不再只是“会聊天”，而是开始拥有访问外部能力的入口。

## 3. 前置知识

开始前，你应该已经理解：

- `load_student()` 会从 `data/student.json` 读取学员资料。
- `Student` 是当前项目里的 `TypedDict`。
- `create_agent()` 可以接收 `tools` 参数。
- 第 5.2 课里 `tools=[]` 表示 Agent 没有任何外部能力。
- 单元测试不能依赖真实模型 provider。

你还要记住一个边界：

```text
工具不是魔法。
工具就是 Python 函数。
模型能不能正确调用工具，取决于工具名称、参数、说明和上下文是否清楚。
```

## 4. 核心概念

### 什么是 tool

LangChain 官方文档对 tools 的定位很直接：

```text
tools extend what agents can do
```

工具让 Agent 能够获取实时数据、执行代码、查询数据库，或者调用外部系统。

在代码层面，最简单的 tool 就是一个 Python 函数。

区别是普通函数只给程序员调用，而 tool 还要暴露给模型：

```text
函数名 -> 模型看到的工具名
类型标注 -> 模型看到的输入 schema
docstring / description -> 模型判断何时使用工具的说明
返回值 -> 模型下一轮推理能看到的工具结果
```

所以，一个好工具需要同时服务两类读者：

- Python 运行时：能执行、能返回稳定结果。
- 模型：能理解什么时候该调用、该传什么参数。

### 为什么本课只做只读工具

当前工具只读取学员档案，不写文件。

原因很简单：

- 读操作风险低。
- 适合学习 tool schema 和 tool calling。
- 不会引入数据覆盖、冲突、权限和回滚问题。
- 后续 LangGraph 和 Deep Agents 里会更系统地处理写操作、人类确认和长期任务。

本课的工具边界是：

```text
可以读：姓名、学习目标、Python 水平、学习笔记
不可以写：不修改 data/student.json
不可以删：不删除学习笔记
不可以联网：不查询外部资料
```

### 为什么工具返回字符串

LangChain tools 可以返回字符串、对象、内容块，甚至返回用于更新 graph state 的 `Command`。

本课选择返回字符串：

```python
return "\n".join(lines)
```

原因是：

- 学员档案天然适合人类可读文本。
- 模型可以直接阅读这段文本并生成建议。
- 暂时不引入结构化 tool output。
- 暂时不引入 LangGraph state 更新。

结构化 tool output 会在后续更复杂的课程里再引入。

### 为什么 message 不再塞学员档案

第 5.2 课为了让最小 Agent 能跑起来，把学员档案提前放进了用户消息。

到了第 5.3 课，如果仍然这样做，就算我们注册了工具，Agent 也没有真实理由去调用它。

所以本课把 message 收窄为：

```python
return [{"role": "user", "content": f"用户问题：{question}"}]
```

学员档案由工具读取。

这能帮助你看清楚：

```text
messages 是用户输入。
tools 是 Agent 可调用能力。
storage.py 是本地数据来源。
```

三者不要混在一起。

## 5. 代码实现

### 第一步：导入 `tool`

打开：

```text
ai-learning-assistant/app/langchain_agent.py
```

新增导入：

```python
from langchain.tools import tool
```

同时删掉第 5.2 课里用于提前构造学员上下文的导入：

```python
from app.llm import build_learning_suggestion_input
```

新增：

```python
from app.storage import load_student
```

因为本课要让工具自己读取当前学员档案。

### 第二步：把学员档案格式化成工具返回值

新增函数：

```python
def format_student_profile_for_tool(student: Student, *, include_notes: bool = True) -> str:
    name = student["name"] or "未填写"
    goal = student["goal"] or "未填写"
    python_level = student["python_level"] or "未填写"

    lines = [
        f"学员姓名：{name}",
        f"学习目标：{goal}",
        f"Python 水平：{python_level}",
    ]

    if include_notes:
        lines.append("学习笔记：")
        if student["notes"]:
            lines.extend(f"{index}. {note}" for index, note in enumerate(student["notes"], start=1))
        else:
            lines.append("暂无笔记")

    return "\n".join(lines)
```

这个函数不是 LangChain 专属代码。

它只是把项目里的 `Student` 字典转换成一段稳定文本。

先写这个函数，是为了让工具本身更薄：

```text
读取数据 -> 交给格式化函数 -> 返回字符串
```

### 第三步：定义普通 Python 查询函数

新增：

```python
def read_current_student_profile(include_notes: bool = True) -> str:
    """Read the current learner profile from local JSON storage."""
    student = load_student()
    return format_student_profile_for_tool(student, include_notes=include_notes)
```

注意参数：

```python
include_notes: bool = True
```

这个参数会进入工具 schema。

模型可以决定是否包含学习笔记。

本课虽然只有一个参数，但它已经具备 tool 的基本结构：

```text
工具名：read_current_student_profile
输入：include_notes
输出：str
说明：读取本地学员档案
```

### 第四步：用 `tool()` 包装成 LangChain 工具

新增：

```python
read_current_student_profile_tool = tool(
    "read_current_student_profile",
    description=(
        "读取当前保存在本地 JSON 文件中的学员档案，包括姓名、学习目标、Python 水平，"
        "并可按需包含学习笔记。这个工具只读，不会修改任何文件。"
    ),
)(read_current_student_profile)
```

这里有几个细节：

- 工具名使用 `snake_case`。
- 描述明确写出“本地 JSON 文件”。
- 描述明确写出“只读”。
- 工具包装的是普通 Python 函数。

模型会看到工具名、描述和参数 schema，然后决定是否调用。

### 第五步：集中构建工具列表

新增：

```python
def build_learning_agent_tools() -> list[Any]:
    return [read_current_student_profile_tool]
```

现在只有一个工具，为什么还要单独写函数？

因为第 5.4 课会新增更多工具。

提前保留这个入口，后续只需要扩展：

```python
return [
    read_current_student_profile_tool,
    read_learning_notes_tool,
    build_rule_suggestion_tool,
]
```

### 第六步：把工具传给 Agent

修改 `create_learning_agent()`：

```python
def create_learning_agent(
    *,
    settings: LLMSettings | None = None,
    model: Any | None = None,
    tools: list[Any] | None = None,
) -> Any:
    current_model = model or build_langchain_chat_model(settings)
    current_tools = tools if tools is not None else build_learning_agent_tools()

    return create_agent(
        model=current_model,
        tools=current_tools,
        system_prompt=LEARNING_AGENT_SYSTEM_PROMPT,
    )
```

这里保留了 `tools` 参数。

原因是测试和后续课程会用到。

生产路径默认使用：

```python
build_learning_agent_tools()
```

测试路径可以传入 fake tools，避免测试过度绑定真实工具列表。

### 第七步：更新 system prompt

第 5.2 课的 prompt 说：

```text
当前阶段你还没有工具
```

现在这句话必须删掉。

改成：

```python
LEARNING_AGENT_SYSTEM_PROMPT = (
    "你是一个 Python 和 AI Agent 学习助教。"
    "你会根据学员档案、学习目标和笔记，给出清晰、可执行的学习建议。"
    "你现在有一个只读工具，可以查询当前保存在本地 JSON 中的学员档案。"
    "当你需要了解学员姓名、目标、Python 水平或学习笔记时，优先调用工具。"
    "不要编造本地文件里的内容。"
    "回答必须使用中文。"
)
```

prompt 不是权限系统，但它能指导模型更稳定地使用工具。

### 第八步：让 message 只保留问题

修改：

```python
def build_learning_agent_messages(
    question: str = DEFAULT_AGENT_QUESTION,
) -> list[dict[str, str]]:
    return [{"role": "user", "content": f"用户问题：{question}"}]
```

现在 message 里不再包含学员档案。

这一步非常重要。

它让工具调用成为获取学员档案的主路径。

### 第九步：更新运行入口

修改：

```python
def run_learning_agent(
    question: str = DEFAULT_AGENT_QUESTION,
    *,
    settings: LLMSettings | None = None,
    agent: Any | None = None,
) -> str:
    current_agent = agent or create_learning_agent(settings=settings)
    result = current_agent.invoke({"messages": build_learning_agent_messages(question)})
    return extract_agent_text(result)
```

第 5.2 课的签名是：

```python
run_learning_agent(student, question)
```

第 5.3 课改成：

```python
run_learning_agent(question)
```

因为学员资料现在由 tool 查询。

### 第十步：更新 demo

打开：

```text
ai-learning-assistant/app/langchain_agent_demo.py
```

改成：

```python
from app.langchain_agent import DEFAULT_AGENT_QUESTION, run_learning_agent


def main() -> None:
    answer = run_learning_agent(DEFAULT_AGENT_QUESTION)
    print(answer)


if __name__ == "__main__":
    main()
```

demo 不再手动调用 `load_student()`。

如果真实 provider 支持 tool calling，并且 `.env` 配置可用，Agent 会在运行过程中决定调用 `read_current_student_profile`。

### 第十一步：新增和更新测试

本课更新：

```text
ai-learning-assistant/tests/test_langchain_agent.py
ai-learning-assistant/tests/test_langchain_agent_demo.py
```

重点测试：

- `format_student_profile_for_tool()` 能稳定格式化学员档案。
- `include_notes=False` 时不返回笔记。
- `read_current_student_profile()` 会读取 storage。
- `build_learning_agent_tools()` 会返回 `read_current_student_profile`。
- 工具对象可以通过 `.invoke(...)` 调用。
- `create_learning_agent()` 默认传入工具列表。
- `build_learning_agent_messages()` 只包含用户问题。
- `run_learning_agent()` 不再接收 student。
- demo 不再自己加载 student。

这里仍然不测试真实 provider。

真实模型工具调用属于人工验收：

```powershell
py -3.13 -m app.langchain_agent_demo
```

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

如果你用 Ollama，需要本地 Ollama 已启动，且 `.env` 中的模型名可用。

如果你用 DeepSeek 或火山引擎 Ark Agent Plan，需要 API Key 和 Base URL 配置正确。

## 7. 常见错误

### 工具没有 docstring 或 description

工具描述不是写给自己看的。

它会帮助模型判断什么时候调用工具。

不要写成：

```python
def read_current_student_profile(...):
    return ...
```

至少要有 docstring，最好为关键业务工具提供明确 description。

### 工具名乱写

不要用：

```text
Read Current Student Profile!
查询当前学员档案
```

工具名建议使用：

```text
read_current_student_profile
```

这类 `snake_case` 名称对不同 provider 更稳。

### 让工具偷偷写文件

本课工具是只读工具。

不要在里面调用：

```python
save_student(...)
```

写操作要等后续课程有明确边界后再做。

### message 里仍然塞完整学员档案

如果 message 里已经有全部学员资料，模型可能不调用工具。

本课的学习点就是：

```text
让 Agent 通过 tool 获取外部信息
```

所以 message 只放用户问题。

### 单元测试跑真实模型

不要把真实 provider 调用写进 pytest。

pytest 应该验证：

- Python 函数是否正确。
- tool 对象是否存在。
- agent 创建时是否带上工具。
- fake agent 是否被正确调用。

真实模型工具调用放在手动 demo 里验收。

### 以为工具调用一定每次发生

工具调用由模型决定。

如果问题很简单，模型可能直接回答。

所以 prompt 里要写清楚：

```text
当你需要了解学员姓名、目标、Python 水平或学习笔记时，优先调用工具。
```

这不是绝对保证，但能提升稳定性。

## 8. 练习

练习 1：解释 `read_current_student_profile()` 为什么先是普通 Python 函数，再被包装成 LangChain tool。

练习 2：解释 `include_notes: bool = True` 会如何影响工具 schema。

练习 3：把 `include_notes=False` 传给工具对象：

```python
read_current_student_profile_tool.invoke({"include_notes": False})
```

观察返回结果。

练习 4：解释为什么 `run_learning_agent()` 不再接收 `student`。

练习 5：在 `data/student.json` 里添加两条笔记，手动运行：

```powershell
py -3.13 -m app.langchain_agent_demo
```

观察模型是否引用了笔记内容。

练习 6：阅读测试文件，说明哪些测试是测 Python 函数，哪些测试是测 LangChain tool 包装。

## 9. 验收标准

完成本课后，你应该能做到：

- 解释 tool 和普通 Python 函数的关系。
- 解释工具名称、类型标注、docstring、description 各自有什么作用。
- 看懂 `format_student_profile_for_tool()`。
- 看懂 `read_current_student_profile()`。
- 看懂 `read_current_student_profile_tool` 是如何创建的。
- 看懂 `build_learning_agent_tools()` 为什么要存在。
- 解释为什么本课工具只读。
- 解释为什么工具返回字符串。
- 解释为什么 message 不再塞完整学员档案。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。
- 在 provider 可用时，能手动运行 `py -3.13 -m app.langchain_agent_demo`。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课把 Stage 5 推进到真正的 tool calling 基础。

| 本课内容 | 后续升级 |
| --- | --- |
| `read_current_student_profile` | 5.4 增加更多查询工具 |
| `tool(...)(function)` | 后续所有 Agent 工具的基础写法 |
| `build_learning_agent_tools()` | 5.4 多工具列表入口 |
| 只读工具 | 后续引入写操作前的安全边界 |
| 工具返回字符串 | 后续升级为结构化 tool output |
| message 只放问题 | 后续对话 API、RAG 和 Graph 状态的输入边界 |

LangGraph 会继续使用“函数”这个概念。

区别是：

```text
LangChain tool：模型决定什么时候调用。
LangGraph node：流程图决定什么时候执行。
```

Deep Agents 也会继续使用工具。

但 Deep Agents 会把工具放在更完整的长期任务 harness 里，配合规划、文件系统、子 Agent 和上下文管理。

所以你现在要先把最小 tool 模型学扎实。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-5/05-03-python-functions-as-tools.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/langchain_agent.py`
- `ai-learning-assistant/app/langchain_agent_demo.py`
- `ai-learning-assistant/tests/test_langchain_agent.py`
- `ai-learning-assistant/tests/test_langchain_agent_demo.py`

代码变更：

- 新增 `format_student_profile_for_tool()`。
- 新增 `read_current_student_profile()`。
- 新增 `read_current_student_profile_tool`。
- 新增 `build_learning_agent_tools()`。
- `create_learning_agent()` 默认传入只读学员档案工具。
- `build_learning_agent_messages()` 改为只包含用户问题。
- `run_learning_agent()` 不再接收 `student`。
- `app/langchain_agent_demo.py` 不再手动加载 student。
- 更新 LangChain Agent 相关测试。

依赖变更：

- 无。继续使用第 5.2 课已引入的 `langchain==1.3.12` 和 `langchain-openai==1.3.4`。

环境变量变更：

- 无。继续复用第 4.2 课的 provider 配置。

官方文档核对：

- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest tests/test_langchain_agent.py tests/test_langchain_agent_demo.py
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py
```

下一步：

- 第 5.4 课：多工具调用。
- 增加查询学习笔记、生成规则建议等工具。
- 让 Agent 在多个工具之间选择，而不是只会查学员档案。
