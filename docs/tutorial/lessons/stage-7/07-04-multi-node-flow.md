# 第 7.4 课：多节点流程

## 1. 本课目标

第 7.3 课已经把第一个节点 `assess_level(state)` 写成了普通 Python 函数。现在要把学习流程扩展成四个节点，并用真实的 LangGraph `StateGraph` 按固定顺序串起来：

```text
assess_level -> teach_topic -> ask_question -> grade_answer
```

完成后，你应该能解释：

- 为什么 LangGraph 节点仍然可以先写成普通函数。
- `StateGraph(LearningState)` 负责什么。
- `START` 和 `END` 为什么不是业务节点。
- `add_edge()` 如何表达固定执行顺序。
- `completed_steps` 为什么会在图运行时累加四个节点。
- 为什么当前只做线性流程，不做答对/答错条件分支。

## 2. 你会新增什么项目能力

`app/graph.py` 新增三个学习流程节点：

```text
teach_topic(state)
ask_question(state)
grade_answer(state)
```

同时新增一个图构造函数：

```text
create_basic_learning_graph()
```

它会构建并编译一个固定顺序的学习图：

```text
START
  -> assess_level
  -> teach_topic
  -> ask_question
  -> grade_answer
  -> END
```

图运行完成后，最终 state 会包含：

- 根据 `python_level` 推荐出的 `current_topic`。
- 对应主题的讲解反馈。
- 对应主题的问题 `lesson_question`。
- 批改结果 `is_correct`。
- 最终反馈 `feedback`。
- 完整节点轨迹 `completed_steps`。

当前仍未新增：

- 条件分支。
- checkpoint。
- streaming。
- human-in-the-loop。
- FastAPI 学习流程接口。
- 真实 LLM 调用或 RAG 调用。

## 3. 前置知识

开始前，应该已经理解：

- `LearningState` 是学习流程共享状态。
- `LearningStateUpdate` 是节点返回的局部更新。
- `completed_steps: Annotated[list[str], add]` 表示多个节点返回的列表会累加。
- `assess_level()` 会根据 `python_level` 选择学习主题。
- 第 7.3 课没有创建 `StateGraph`，因为还没有多节点流程。

还不需要理解：

- 条件边 `add_conditional_edges()`。
- checkpoint saver。
- stream events。
- API 会话状态。
- 多用户并发。

这些会放到后续课程。

## 4. 核心概念

### 多节点不是把代码写成一个大函数

如果直接写一个大函数：

```python
def run_flow(state):
    ...
```

确实也能按顺序执行。但是这样会把“判断水平、讲解主题、提出问题、批改答案”混在一起。后续要加分支、暂停、恢复、追踪时，就很难知道每一步在哪里发生。

LangGraph 的做法是把每一步拆成 node：

```text
一个节点 = 读取 state -> 做一步工作 -> 返回局部 update
```

节点越清楚，图越容易测试和扩展。

### `StateGraph` 是图的构建器

`StateGraph(LearningState)` 告诉 LangGraph：

```text
这张图运行时使用 LearningState 作为共享状态结构。
```

它不是立即运行图，而是用来注册节点和边：

```python
builder = StateGraph(LearningState)
builder.add_node("assess_level", assess_level)
builder.add_edge(START, "assess_level")
graph = builder.compile()
```

只有 `compile()` 之后，才得到可以 `invoke()` 的图对象。

### `START` 和 `END`

`START` 表示图入口，`END` 表示图结束。它们不是业务节点，不会改状态，只用来描述流程边界。

这条边：

```python
builder.add_edge(START, "assess_level")
```

表示图从 `assess_level` 开始。

这条边：

```python
builder.add_edge("grade_answer", END)
```

表示 `grade_answer` 结束后，图运行完成。

### 固定顺序 edge

第 7.4 课只使用普通 edge：

```text
A -> B -> C -> D
```

普通 edge 不判断条件，只表达固定顺序。无论答案对错，当前图都会跑到 `END`。

第 7.5 课才会根据 `is_correct` 增加条件分支，让答对和答错走不同路径。

### 节点返回局部更新

每个节点仍然返回 `LearningStateUpdate`，不是整份 state。

例如 `ask_question()` 只负责提出问题：

```python
return {
    "lesson_question": TOPIC_QUESTIONS[topic],
    "completed_steps": ["ask_question"],
}
```

它不应该顺手修改 `python_level`、`material_sources` 或其他无关字段。

### `completed_steps` 会累加

四个节点分别返回：

```text
["assess_level"]
["teach_topic"]
["ask_question"]
["grade_answer"]
```

因为 `LearningState.completed_steps` 使用了 `Annotated[list[str], add]`，LangGraph 合并状态时会把它们累加为：

```text
["assess_level", "teach_topic", "ask_question", "grade_answer"]
```

这就是第 7.2 课提前给 reducer 做铺垫的原因。

### `feedback` 只保存最新反馈

当前 `feedback` 是普通字符串字段，没有 reducer。多个节点返回 `feedback` 时，后面的更新会覆盖前面的更新。

这不是 bug。当前项目只需要给学习者展示最近一步反馈。后续如果要保留完整对话或每一步讲解记录，需要另增列表字段，而不是滥用一个字符串字段。

## 5. 代码实现

安装依赖后，`requirements.txt` 显式包含：

```text
langgraph==1.2.8
```

因为项目代码已经直接使用 `StateGraph`、`START` 和 `END`，不能只依赖 `langchain` 的传递依赖。

打开：

```text
ai-learning-assistant/app/graph.py
```

新增导入：

```python
from langgraph.graph import END, START, StateGraph
```

第一个节点 `assess_level()` 保留上一节的职责：根据 `python_level` 选择主题。

新增主题讲解、问题和答案关键词：

```python
TOPIC_LESSONS = {
    "python_variables_and_io": "...",
    "python_functions_and_modules": "...",
    "rag_and_agent_integration": "...",
}

TOPIC_QUESTIONS = {
    "python_variables_and_io": "变量主要帮我们解决什么问题？",
    "python_functions_and_modules": "函数为什么能让代码更容易维护？",
    "rag_and_agent_integration": "RAG 回答为什么需要保留 sources？",
}

TOPIC_ANSWER_KEYWORDS = {
    "python_variables_and_io": ("保存", "数据", "值", "名字"),
    "python_functions_and_modules": ("复用", "拆分", "维护", "测试"),
    "rag_and_agent_integration": ("来源", "证据", "追溯", "溯源", "资料", "source", "sources"),
}
```

新增主题校验 helper：

```python
def _get_topic(state: LearningState) -> str:
    topic = state["current_topic"].strip()
    if topic not in TOPIC_LESSONS:
        raise ValueError("current_topic is not supported")
    return topic
```

教学节点：

```python
def teach_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": TOPIC_LESSONS[topic],
        "completed_steps": ["teach_topic"],
    }
```

出题节点：

```python
def ask_question(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "lesson_question": TOPIC_QUESTIONS[topic],
        "completed_steps": ["ask_question"],
    }
```

批改节点：

```python
def grade_answer(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)
    answer = state["learner_answer"].strip().lower()
    keywords = TOPIC_ANSWER_KEYWORDS[topic]
    is_correct = answer != "" and any(keyword in answer for keyword in keywords)
    if is_correct:
        feedback = "回答抓住了关键点，可以进入下一步练习。"
    else:
        question = state["lesson_question"] or TOPIC_QUESTIONS[topic]
        feedback = f"这次还没有命中关键点，可以围绕这个问题重答：{question}"

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "completed_steps": ["grade_answer"],
    }
```

最后构建固定顺序图：

```python
def create_basic_learning_graph():
    builder = StateGraph(LearningState)
    builder.add_node("assess_level", assess_level)
    builder.add_node("teach_topic", teach_topic)
    builder.add_node("ask_question", ask_question)
    builder.add_node("grade_answer", grade_answer)

    builder.add_edge(START, "assess_level")
    builder.add_edge("assess_level", "teach_topic")
    builder.add_edge("teach_topic", "ask_question")
    builder.add_edge("ask_question", "grade_answer")
    builder.add_edge("grade_answer", END)

    return builder.compile()
```

测试文件：

```text
ai-learning-assistant/tests/test_graph.py
```

新增测试覆盖：

- `teach_topic()` 返回主题讲解。
- `ask_question()` 返回主题问题。
- `grade_answer()` 能判断答对。
- `grade_answer()` 能判断答错。
- `create_basic_learning_graph().invoke(state)` 能按固定顺序跑完四个节点。
- 不支持的 `current_topic` 会被节点拒绝。

核心图测试断言：

```python
assert result["completed_steps"] == [
    "assess_level",
    "teach_topic",
    "ask_question",
    "grade_answer",
]
```

这条断言证明图运行和 reducer 合并都生效了。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
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

手动查看图运行结果：

```powershell
py -3.13 -c "from app.graph import create_basic_learning_graph, create_initial_learning_state; from app.storage import create_default_student; student=create_default_student(); student['python_level']='basic'; state=create_initial_learning_state(student); state['learner_answer']='函数可以复用逻辑，也能拆分代码。'; print(create_basic_learning_graph().invoke(state)['completed_steps'])"
```

这条命令不需要真实 provider、Ollama、RAG 索引或 FastAPI 服务。

## 7. 常见错误

### 把多个节点合成一个大函数

流程能跑不代表结构对。LangGraph 的价值在于把步骤拆开，让每一步可测试、可追踪、可扩展。

### 忘记 `compile()`

`StateGraph` 是 builder。注册节点和边之后必须调用：

```python
graph = builder.compile()
```

否则没有可执行的图对象。

### 把 `START` 和 `END` 当成业务节点

它们只表示图边界，不处理业务，也不返回 state update。

### 在 7.4 提前做条件分支

当前图是固定顺序。即使 `grade_answer()` 返回 `is_correct=False`，图也会结束。根据答对/答错选择下一步属于第 7.5 课。

### 期待 `feedback` 保存所有节点消息

`feedback` 是字符串字段，后面的节点会覆盖前面的反馈。要保存完整过程，需要设计列表字段和 reducer。当前只保留最新反馈。

### 在节点里调用真实模型

教学、出题、批改在这里都是确定性规则。先把图结构跑通，再把 LLM、RAG 或 API 接进来。把所有东西一口气塞进节点，会让错误来源变得混乱。

## 8. 练习

练习 1：画出当前图的节点和边，标出 `START` 与 `END`。

练习 2：解释为什么 `teach_topic()` 不应该修改 `lesson_question`。

练习 3：给 `grade_answer()` 增加一个新的正确关键词，并补一个测试。

练习 4：把 `learner_answer` 改成空字符串，观察 `is_correct` 和 `feedback`。

练习 5：思考第 7.5 课应该如何根据 `is_correct` 决定下一步节点。

## 9. 验收标准

完成后，应该能做到：

- 显式依赖 `langgraph==1.2.8`。
- 实现 `teach_topic()`、`ask_question()` 和 `grade_answer()`。
- 实现 `create_basic_learning_graph()`。
- 图使用 `StateGraph(LearningState)`。
- 图包含 `START -> assess_level -> teach_topic -> ask_question -> grade_answer -> END`。
- `graph.invoke(state)` 能返回完整最终 state。
- `completed_steps` 按四个节点顺序累加。
- `grade_answer()` 能返回 `is_correct=True` 和 `is_correct=False` 两类结果。
- 不支持的 `current_topic` 会被拒绝。
- 能解释为什么当前没有条件分支、checkpoint、streaming 或 API。
- `py -3.13 -m pytest tests/test_graph.py` 通过。
- 完整 `pytest` 和 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| 固定顺序 edge | 7.5：根据 `is_correct` 增加条件分支 |
| `grade_answer()` | 条件分支的判定来源 |
| `completed_steps` | 后续用于追踪流程执行路径 |
| `create_basic_learning_graph()` | 7.6：成为 FastAPI 学习流程接口的核心执行对象 |
| `LearningState` | Stage 8：接入 checkpoint 和恢复能力 |
| 节点拆分 | Deep Agents 阶段理解规划、执行和总结的任务拆分基础 |

LangGraph 现在开始真正进入项目代码，但仍然保持确定性。先让图结构可测，后面再接模型和外部状态。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-7/07-04-multi-node-flow.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/app/graph.py`
- `ai-learning-assistant/tests/test_graph.py`

代码变更：

- 显式新增 `langgraph==1.2.8`。
- 新增主题讲解、问题和关键词表。
- 新增 `teach_topic()`、`ask_question()`、`grade_answer()`。
- 新增 `create_basic_learning_graph()`。
- 增加节点单测和图运行测试。

新增依赖：

- `langgraph==1.2.8`

环境变量变更：无。

官方文档核对：

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)

下一步：第 7.5 课，条件分支。
