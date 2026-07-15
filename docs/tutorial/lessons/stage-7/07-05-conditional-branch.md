# 第 7.5 课：条件分支

## 1. 本课目标

第 7.4 课已经把学习流程串成固定顺序：

```text
assess_level -> teach_topic -> ask_question -> grade_answer
```

现在要让图根据批改结果走不同路径：

```text
grade_answer
  -> 答对：recommend_next_topic
  -> 答错：review_current_topic
```

完成后，你应该能解释：

- 为什么条件分支必须依赖 state 中已经写入的字段。
- `add_conditional_edges()` 里的路由函数负责什么。
- 为什么 `route_by_answer()` 只返回路线名，不直接修改 state。
- 为什么答对和答错要落到不同节点，而不是把所有逻辑塞进 `grade_answer()`。
- 为什么第 7.5 课仍然不接 FastAPI、checkpoint、streaming 或真实模型调用。

## 2. 你会新增什么项目能力

`app/graph.py` 新增一个路由类型：

```python
AnswerRoute = Literal["recommend_next_topic", "review_current_topic"]
```

新增一个路由函数：

```python
route_by_answer(state)
```

新增两个分支节点：

```python
recommend_next_topic(state)
review_current_topic(state)
```

新增一个条件分支图：

```python
create_branching_learning_graph()
```

它会构建并编译这张图：

```text
START
  -> assess_level
  -> teach_topic
  -> ask_question
  -> grade_answer
      -- route_by_answer: recommend_next_topic --> recommend_next_topic
      -- route_by_answer: review_current_topic --> review_current_topic
  -> END
```

注意，`route_by_answer` 不是一个业务节点。它不会写入 state，也不会出现在 `completed_steps` 中。它只是告诉 LangGraph：下一步应该去哪个 node。

当前仍未新增：

- FastAPI 学习流程接口。
- checkpoint。
- streaming。
- human-in-the-loop。
- 多轮会话状态保存。
- 真实 LLM 批改。

## 3. 前置知识

开始前，应该已经理解：

- `LearningState` 是整张图共享的状态。
- 节点读取 state，返回局部 `LearningStateUpdate`。
- `completed_steps` 使用 reducer 累加节点轨迹。
- `grade_answer()` 会把批改结果写入 `is_correct`。
- `create_basic_learning_graph()` 是固定顺序图，保留用于对照。

还不需要理解：

- checkpoint saver 如何恢复中断流程。
- streaming event 如何推给前端。
- API 会话 ID 如何绑定图状态。
- 数据库如何保存学习流程历史。

这些会放到后续课程。

## 4. 核心概念

### 条件边读取的是当前 state

条件分支不是靠函数参数临时传一个布尔值。LangGraph 会先运行源节点，合并这个节点返回的 update，然后再把当前 state 交给路由函数。

在这一节里，源节点是：

```python
grade_answer(state)
```

它会返回：

```python
{
    "is_correct": True,
    "feedback": "回答抓住了关键点，可以进入下一步练习。",
    "completed_steps": ["grade_answer"],
}
```

或者：

```python
{
    "is_correct": False,
    "feedback": "这次还没有命中关键点，可以围绕这个问题重答：...",
    "completed_steps": ["grade_answer"],
}
```

接着 `route_by_answer(state)` 读取合并后的 `state["is_correct"]`，决定下一步。

### 路由函数只负责选路

`route_by_answer()` 的职责很窄：

```python
def route_by_answer(state: LearningState) -> AnswerRoute:
    if state["is_correct"] is True:
        return "recommend_next_topic"
    if state["is_correct"] is False:
        return "review_current_topic"
    raise ValueError("is_correct must be set before routing")
```

它不生成反馈，不改 `current_topic`，不追加 `completed_steps`。

原因很简单：路由函数不是业务节点。它只是把 state 映射成一个路线名。

### 分支节点负责业务动作

答对后的节点：

```python
def recommend_next_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": NEXT_TOPIC_HINTS[topic],
        "completed_steps": ["recommend_next_topic"],
    }
```

答错后的节点：

```python
def review_current_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": REVIEW_TOPIC_HINTS[topic],
        "completed_steps": ["review_current_topic"],
    }
```

这两个节点才是实际业务动作，所以它们会写 `feedback`，也会追加 `completed_steps`。

### 条件边不是 if else 的花哨写法

普通 Python 当然可以这样写：

```python
if is_correct:
    recommend_next_topic(state)
else:
    review_current_topic(state)
```

但 LangGraph 的价值不在于替代 `if`，而在于把流程结构显式建成图：

```python
builder.add_conditional_edges(
    "grade_answer",
    route_by_answer,
    {
        "recommend_next_topic": "recommend_next_topic",
        "review_current_topic": "review_current_topic",
    },
)
```

这让后续扩展更清楚：

- 可以给不同分支加更多节点。
- 可以给关键节点加 checkpoint。
- 可以追踪每次运行实际经过的路径。
- 可以在 API 层把图当成一个稳定执行单元。

### 路线名和节点名可以相同

这一节里，路线名和节点名保持一致：

```python
{
    "recommend_next_topic": "recommend_next_topic",
    "review_current_topic": "review_current_topic",
}
```

左边是路由函数返回的路线名，右边是实际要进入的 node 名。

它们可以不一样，但初学阶段别自找麻烦。保持一致，读代码的人不用绕弯。

### 找不到批改结果要直接失败

如果 `is_correct` 还是 `None`，说明图还没有完成批改，或者有人绕过了 `grade_answer()`。

这时不能默认走复习，也不能默认答对。正确做法是直接失败：

```python
raise ValueError("is_correct must be set before routing")
```

这是防止流程状态被静默污染。学习流程里最烦的是“看起来能跑”，但其实走错了路径。

## 5. 代码实现

### 5.1 增加路线类型和分支文案

`app/graph.py` 先增加路线类型：

```python
AnswerRoute = Literal["recommend_next_topic", "review_current_topic"]
```

再给每个主题准备答对和答错后的反馈：

```python
NEXT_TOPIC_HINTS: dict[str, str] = {
    "python_variables_and_io": "下一步可以练习把输入、变量和打印组合成一个小脚本。",
    "python_functions_and_modules": "下一步可以练习把重复逻辑拆成函数，并把函数放进独立模块。",
    "rag_and_agent_integration": "下一步可以练习把检索、引用 sources 和回答生成串成一个稳定流程。",
}

REVIEW_TOPIC_HINTS: dict[str, str] = {
    "python_variables_and_io": "先回看变量如何给数据命名，再用自己的话解释变量保存了什么。",
    "python_functions_and_modules": "先回看函数的复用、拆分和测试价值，再重新回答维护性问题。",
    "rag_and_agent_integration": "先回看 sources 如何支撑证据追溯，再重新说明为什么不能丢来源。",
}
```

这里仍然不用真实模型。第 7 阶段先把图结构讲清楚，LLM 批改和资料检索可以在后面接入。

### 5.2 增加路由函数

```python
def route_by_answer(state: LearningState) -> AnswerRoute:
    if state["is_correct"] is True:
        return "recommend_next_topic"
    if state["is_correct"] is False:
        return "review_current_topic"
    raise ValueError("is_correct must be set before routing")
```

这里故意用 `is True` 和 `is False`，不是直接写：

```python
if state["is_correct"]:
    ...
```

因为 `is_correct` 的类型是：

```python
bool | None
```

`None` 是一个重要状态，表示“还没批改”。它必须被单独拦住。

### 5.3 增加两个分支节点

```python
def recommend_next_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": NEXT_TOPIC_HINTS[topic],
        "completed_steps": ["recommend_next_topic"],
    }
```

```python
def review_current_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": REVIEW_TOPIC_HINTS[topic],
        "completed_steps": ["review_current_topic"],
    }
```

两个节点都调用 `_get_topic(state)`。这样如果上游给了不支持的主题，错误会在节点边界暴露，不会生成乱七八糟的反馈。

### 5.4 创建条件分支图

固定顺序图 `create_basic_learning_graph()` 保留不动。第 7.5 课新增一个函数：

```python
def create_branching_learning_graph():
    builder = StateGraph(LearningState)
    builder.add_node("assess_level", assess_level)
    builder.add_node("teach_topic", teach_topic)
    builder.add_node("ask_question", ask_question)
    builder.add_node("grade_answer", grade_answer)
    builder.add_node("recommend_next_topic", recommend_next_topic)
    builder.add_node("review_current_topic", review_current_topic)

    builder.add_edge(START, "assess_level")
    builder.add_edge("assess_level", "teach_topic")
    builder.add_edge("teach_topic", "ask_question")
    builder.add_edge("ask_question", "grade_answer")
    builder.add_conditional_edges(
        "grade_answer",
        route_by_answer,
        {
            "recommend_next_topic": "recommend_next_topic",
            "review_current_topic": "review_current_topic",
        },
    )
    builder.add_edge("recommend_next_topic", END)
    builder.add_edge("review_current_topic", END)

    return builder.compile()
```

关键点只有一个：

```python
builder.add_conditional_edges(...)
```

它表示：`grade_answer` 结束后，不再固定进入 `END`，而是先调用 `route_by_answer` 选择下一条边。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行图测试：

```powershell
py -3.13 -m pytest tests/test_graph.py
```

手动检查答对路径：

```powershell
py -3.13 -c "from app.graph import create_branching_learning_graph, create_initial_learning_state; from app.storage import create_default_student; student=create_default_student(); student['python_level']='basic'; state=create_initial_learning_state(student); state['learner_answer']='函数可以复用逻辑，也能拆分代码。'; print(create_branching_learning_graph().invoke(state)['completed_steps'])"
```

期望看到：

```text
['assess_level', 'teach_topic', 'ask_question', 'grade_answer', 'recommend_next_topic']
```

手动检查答错路径：

```powershell
py -3.13 -c "from app.graph import create_branching_learning_graph, create_initial_learning_state; from app.storage import create_default_student; student=create_default_student(); student['python_level']='intermediate'; state=create_initial_learning_state(student); state['learner_answer']='因为这样比较好看。'; print(create_branching_learning_graph().invoke(state)['completed_steps'])"
```

期望看到：

```text
['assess_level', 'teach_topic', 'ask_question', 'grade_answer', 'review_current_topic']
```

## 7. 常见错误

### 把路由函数写成节点

`route_by_answer()` 不需要 `builder.add_node(...)`。

它是 `add_conditional_edges()` 的第二个参数，不是图里的业务节点。如果把它注册成 node，就会混淆“选路”和“做事”。

### 在路由函数里改 state

不要在路由函数里写：

```python
state["feedback"] = "..."
```

节点返回 update，路由函数返回路线名。职责混了，后续图会很难测试。

### 忽略 `None`

不要写：

```python
return "recommend_next_topic" if state["is_correct"] else "review_current_topic"
```

这会把 `None` 当成答错。`None` 表示还没批改，应该直接失败。

### 提前删除固定顺序图

`create_basic_learning_graph()` 是第 7.4 课的成果，也是对照样本。不要因为新增条件分支图就删掉它。

后续读者能通过两个函数对比：

```text
固定 edge：add_edge(...)
条件 edge：add_conditional_edges(...)
```

### 在 7.5 接入 API

第 7.6 课才会处理 FastAPI 调 Graph。

这一节只验证图内部的分支逻辑。别把 API 请求体、会话 ID、并发状态和图分支混在一起讲，否则初学者会连错在哪里都看不出来。

## 8. 练习

练习 1：把 `route_by_answer()` 的 `None` 分支删掉，改成普通 `if/else`，观察哪类错误会被吞掉。看完就改回来。

练习 2：新增一个测试，让 beginner 学员答对变量问题后进入 `recommend_next_topic`。

练习 3：新增一个测试，让 beginner 学员答错变量问题后进入 `review_current_topic`。

练习 4：尝试把路线名改成 `correct` 和 `incorrect`，然后修改 `add_conditional_edges()` 的映射。理解左边路线名和右边节点名的区别。

练习 5：思考下一节 API 调用时，请求体至少需要哪些字段才能运行这张图。

## 9. 验收标准

完成这一节后，应该满足：

- `app/graph.py` 保留 `create_basic_learning_graph()`。
- `app/graph.py` 新增 `create_branching_learning_graph()`。
- `route_by_answer()` 在 `is_correct=True` 时返回 `recommend_next_topic`。
- `route_by_answer()` 在 `is_correct=False` 时返回 `review_current_topic`。
- `route_by_answer()` 在 `is_correct=None` 时抛出 `ValueError`。
- 答对路径的 `completed_steps` 以 `recommend_next_topic` 结尾。
- 答错路径的 `completed_steps` 以 `review_current_topic` 结尾。
- `py -3.13 -m pytest tests/test_graph.py` 通过。
- 整体 `py -3.13 -m pytest` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

第 7.5 课解决的是“图怎么根据状态选择下一步”。

这正是后续很多复杂能力的基础：

| 当前能力 | 后续会怎么扩展 |
| --- | --- |
| `is_correct` 条件分支 | 根据模型评分、资料检索结果或用户选择走不同路径 |
| `route_by_answer()` | 后续可替换成更复杂的路由函数 |
| `recommend_next_topic` | 可以进入下一阶段学习任务 |
| `review_current_topic` | 可以进入复习、补充资料或再次提问 |
| `completed_steps` | 可以作为调试、追踪和学习报告的基础 |

第 7.6 课会把图接入 FastAPI，让外部请求可以触发一次学习流程。

## 11. 本课变更清单

代码变更：

- `ai-learning-assistant/app/graph.py`
  - 新增 `AnswerRoute`。
  - 新增 `NEXT_TOPIC_HINTS` 和 `REVIEW_TOPIC_HINTS`。
  - 新增 `route_by_answer()`。
  - 新增 `recommend_next_topic()`。
  - 新增 `review_current_topic()`。
  - 新增 `create_branching_learning_graph()`。

测试变更：

- `ai-learning-assistant/tests/test_graph.py`
  - 覆盖答对路由。
  - 覆盖答错路由。
  - 覆盖缺少批改结果的拒绝路径。
  - 覆盖两个分支节点。
  - 覆盖条件分支图的答对和答错执行路径。

文档变更：

- `docs/tutorial/lessons/stage-7/07-05-conditional-branch.md`
  - 新增第 7.5 课。
- `docs/tutorial/README.md`
  - 更新课程索引和当前学习位置。
- `README.md`
  - 更新仓库当前进度。
- `ai-learning-assistant/README.md`
  - 更新真实项目当前 LangGraph 能力说明。

官方接口参考：

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/use-graph-api)
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
