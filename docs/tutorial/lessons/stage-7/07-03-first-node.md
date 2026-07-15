# 第 7.3 课：第一个节点

## 1. 本课目标

第 7.2 课已经定义了 `LearningState` 和 `LearningStateUpdate`。现在要写第一个真正的学习流程节点：

```text
assess_level(state) -> LearningStateUpdate
```

这个节点读取学员的 `python_level`，判断当前应该进入哪个学习主题，并返回局部状态更新。

完成后，你应能解释：

- LangGraph node 为什么可以先写成普通 Python 函数。
- node 为什么接收完整 `LearningState`，但只返回 `LearningStateUpdate`。
- `assess_level()` 为什么不直接修改输入 state。
- 为什么当前仍不创建 `StateGraph`。
- 为什么测试节点逻辑不需要真实 LLM、RAG 或 API。

## 2. 你会新增什么项目能力

`app/graph.py` 新增：

```text
assess_level(state)
```

它会根据 `python_level` 返回推荐主题：

| `python_level` | `current_topic` |
| --- | --- |
| `beginner` | `python_variables_and_io` |
| `basic` | `python_functions_and_modules` |
| `intermediate` | `rag_and_agent_integration` |

返回值形状：

```python
{
    "current_topic": "...",
    "feedback": "...",
    "completed_steps": ["assess_level"],
}
```

当前仍未新增：

- `StateGraph`。
- 多个节点。
- edge。
- 条件分支。
- checkpoint、streaming、human-in-the-loop。
- FastAPI 学习流程接口。

## 3. 前置知识

开始前，应已经理解：

- `LearningState` 保存完整学习流程状态。
- `LearningStateUpdate` 表达节点的局部更新。
- `completed_steps` 使用 `Annotated[list[str], add]` 表示后续应累加。
- `python_level` 只允许 `beginner`、`basic`、`intermediate`。
- Stage 7.2 还没有创建图，只定义了状态结构。

还不需要：

- 调用 `StateGraph`。
- 连接节点和边。
- 把节点暴露为 API。
- 在节点里调用模型。
- 处理用户答案。

## 4. 核心概念

### node 先是普通函数

LangGraph 的节点可以理解成：

```text
输入 state
-> 做一步明确工作
-> 返回 state update
```

因此，学习者可以先用普通 Python 函数验证节点逻辑。等节点职责清楚、测试稳定后，再把它注册进图。

`assess_level()` 的职责只有一个：根据学员 Python 水平选择当前学习主题。

### node 读取完整 state

节点接收完整 `LearningState`，因为它可能需要读取多个字段。例如后续教学节点可能会读取：

```text
student_name
learning_goal
current_topic
material_sources
```

但 `assess_level()` 目前只需要：

```text
python_level
```

读取完整 state 不代表节点应该改完整 state。读什么和写什么要分清。

### node 返回局部 update

`assess_level()` 不返回完整 `LearningState`，而是返回：

```text
current_topic
feedback
completed_steps
```

其他字段，例如 `student_name`、`lesson_question`、`learner_answer`，不属于这个节点的责任，就不应该出现在返回值里。

这种局部更新方式有三个好处：

- 节点职责更小。
- 后续合并状态时更清楚。
- 测试不用构造和断言整份 state。

### 不直接修改输入 state

节点应该把输入 state 当成只读数据。直接修改输入会带来两个问题：

- 测试难以判断变化来自哪里。
- 后续图运行时的状态合并语义会被绕开。

因此当前写法是：

```python
return {
    "current_topic": current_topic,
    "feedback": feedback,
    "completed_steps": ["assess_level"],
}
```

它只描述“这一步要更新什么”，不在原字典上原地写入。

### `completed_steps` 记录节点轨迹

每个节点都可以把自己的名字追加到 `completed_steps`：

```text
["assess_level"]
```

后续多个节点串起来时，轨迹会变成：

```text
["assess_level", "teach_topic", "ask_question", "grade_answer"]
```

这就是第 7.2 课给 `completed_steps` 标注 `add` reducer 的原因。

### 7.3 仍不创建图

当前只写第一个节点。还没有第二个节点，也没有边。创建 `StateGraph` 会让学习者把注意力放到框架 API 上，而不是节点职责上。

后续顺序仍然是：

```text
7.3 单个节点
7.4 多节点流程
7.5 条件分支
7.6 FastAPI 调 Graph
```

## 5. 代码实现

打开：

```text
ai-learning-assistant/app/graph.py
```

先定义不同水平对应的推荐主题和反馈：

```python
LEVEL_TOPIC_RECOMMENDATIONS: dict[PythonLevel, tuple[str, str]] = {
    "beginner": (
        "python_variables_and_io",
        "你可以先从变量、输入输出和字符串练习开始，先把最小 Python 程序跑顺。",
    ),
    "basic": (
        "python_functions_and_modules",
        "你已经有基础，可以进入函数拆分、模块化和简单测试练习。",
    ),
    "intermediate": (
        "rag_and_agent_integration",
        "你可以开始复盘 RAG、LangChain Agent 和 API 入口如何组合。",
    ),
}
```

然后新增节点函数：

```python
def assess_level(state: LearningState) -> LearningStateUpdate:
    python_level = _validate_python_level(state["python_level"])
    current_topic, feedback = LEVEL_TOPIC_RECOMMENDATIONS[python_level]

    return {
        "current_topic": current_topic,
        "feedback": feedback,
        "completed_steps": ["assess_level"],
    }
```

测试文件：

```text
ai-learning-assistant/tests/test_graph.py
```

新增测试要证明：

- 三种合法 `python_level` 会映射到不同主题。
- 节点返回非空反馈。
- 节点记录 `completed_steps=["assess_level"]`。
- 节点不会原地修改输入 state。
- 非法 `python_level` 会被拒绝。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行图相关测试：

```powershell
py -3.13 -m pytest tests/test_graph.py
```

运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/graph.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_graph.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

手动查看节点输出：

```powershell
py -3.13 -c "from app.graph import assess_level, create_initial_learning_state; from app.storage import create_default_student; student=create_default_student(); student['python_level']='basic'; print(assess_level(create_initial_learning_state(student)))"
```

不需要真实 provider、本地 Ollama 或 FastAPI 服务。

## 7. 常见错误

### 直接修改传入的 state

不要在节点里写：

```python
state["current_topic"] = "..."
return state
```

这样会绕开后续图的更新合并语义，也让测试更难定位副作用。

### 返回整份 LearningState

节点只负责一步更新。`assess_level()` 不应该返回 `student_name`、`learner_answer`、`material_sources` 等无关字段。

### 把节点写成模型调用

判断 `python_level` 是确定性规则，不需要 LLM。能用普通代码明确完成的判断，不要交给模型增加不稳定性。

### 在节点里读取 JSON 文件

当前 state 已经包含所需字段。节点不应该自己调用 `load_student()`，否则图状态和持久化状态会混在一起。

### 现在就接入 StateGraph

单节点还没有流程结构。先把节点输入、输出和测试稳定，再进入多节点和边。

## 8. 练习

练习 1：为 `beginner`、`basic`、`intermediate` 分别写出你认为合适的 `current_topic`。

练习 2：解释为什么 `assess_level()` 不应该直接调用 RAG。

练习 3：如果 `assess_level()` 返回整份 state，会带来哪些维护问题？

练习 4：为 `assess_level()` 增加一个测试，证明输入 state 没有被修改。

练习 5：思考第 7.4 课如果要接第二个节点，应该接在 `assess_level()` 后面的是什么。

## 9. 验收标准

完成后，应能做到：

- 实现 `assess_level(state) -> LearningStateUpdate`。
- 根据 `python_level` 返回不同 `current_topic`。
- 返回非空 `feedback`。
- 返回 `completed_steps=["assess_level"]`。
- 拒绝未知 `python_level`。
- 证明节点不会原地修改输入 state。
- 说明当前仍没有 `StateGraph`、edge、checkpoint 或 API。
- 运行 `py -3.13 -m pytest tests/test_graph.py` 通过。
- 运行完整 `pytest` 和 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| `assess_level()` | 7.4：作为多节点流程的第一个节点 |
| `LearningStateUpdate` | 后续所有 node 统一返回局部更新 |
| `completed_steps` | 多节点执行时记录完整轨迹 |
| `current_topic` | 教学节点根据主题生成讲解或问题 |
| `feedback` | 后续 API 可以返回给前端或 CLI |
| RAG 函数层 | 后续资料讲解节点可按 `current_topic` 调用 |
| 条件分支 | 7.5：根据 `is_correct` 决定下一步 |
| checkpoint / streaming | Stage 8：恢复流程与过程输出 |

课程继续使用同一条真实代码主线：

```text
ai-learning-assistant/
```

不会为这节课创建单独的示例项目或代码快照。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-7/07-03-first-node.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/graph.py`
- `ai-learning-assistant/tests/test_graph.py`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- 新增 `LEVEL_TOPIC_RECOMMENDATIONS`。
- 新增 `assess_level()`。
- 增加水平映射、无副作用和非法水平的节点测试。

新增依赖：无。

环境变量变更：无。

官方文档核对：

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)

下一步：第 7.4 课，串联多节点流程。
