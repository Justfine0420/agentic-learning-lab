# 第 7.2 课：定义 LearningState

## 1. 本课目标

第 7.1 课已经建立 LangGraph 的核心模型：

```text
State
-> node
-> edge
-> compiled graph
```

现在要先定义学习流程的状态结构。没有清楚的 state，后面的 node 和 edge 都会变成靠猜字段协作的函数。

完成后，你应能解释：

- 为什么 LangGraph 图要先定义 State schema。
- 为什么 `LearningState` 放在 `app/graph.py`，而不是塞进 API 或 CLI。
- 为什么节点通常返回 partial update，而不是整份 state。
- 为什么 `completed_steps` 需要 reducer 语义。
- 为什么当前仍不新增显式 `langgraph` 依赖、不创建 `StateGraph`。

## 2. 你会新增什么项目能力

项目新增：

```text
app/graph.py
tests/test_graph.py
```

核心结构：

```text
LearningState
LearningStateUpdate
create_initial_learning_state()
```

当前能做到：

- 从已有 `Student` 字典创建学习流程初始状态。
- 固定学习流程状态字段，包括学员信息、当前主题、题目、答案、批改结果、反馈、资料来源和已完成步骤。
- 用 `LearningStateUpdate` 表达节点后续可返回的局部状态更新。
- 给 `completed_steps` 标注累加式 reducer 语义，为后续 LangGraph 接入做准备。
- 初始化状态时拒绝未知 `python_level` 和空白 `current_topic`。

仍未新增：

- `langgraph` 依赖。
- `StateGraph` 实例。
- node 函数。
- edge 或条件分支。
- checkpoint、streaming、human-in-the-loop。
- API 路由。

## 3. 前置知识

开始前，应已经理解：

- `TypedDict` 如何描述字典结构。
- `Student` 当前包含 `name`、`goal`、`python_level` 和 `notes`。
- LangGraph 的 State 是节点之间共享和更新的数据。
- 节点可以只返回自己负责更新的字段。
- `Annotated` 可以给类型附加额外元信息。

还不需要：

- 编译 LangGraph。
- 编写 node。
- 使用 checkpoint。
- 处理并发分支。
- 持久化学习会话。

## 4. 核心概念

### State schema 是流程契约

学习流程会逐步经历：

```text
读取学员状态
-> 选择学习主题
-> 出题
-> 接收答案
-> 批改
-> 生成反馈
-> 进入下一步
```

每一步都需要读写一些字段。如果没有统一 schema，每个节点就会自己发明字段名，例如：

```text
answer
learner_answer
user_answer
student_answer
```

字段一乱，流程就很快失控。`LearningState` 的作用就是把这些字段先定下来。

### `LearningState` 保存整份图状态

当前状态设计为：

```python
class LearningState(TypedDict):
    student_name: str
    learning_goal: str
    python_level: PythonLevel
    current_topic: str
    lesson_question: str
    learner_answer: str
    is_correct: bool | None
    feedback: str
    material_sources: list[str]
    completed_steps: Annotated[list[str], add]
```

这些字段分成几类：

| 字段 | 用途 |
| --- | --- |
| `student_name`、`learning_goal`、`python_level` | 从已有学员资料带入图 |
| `current_topic` | 当前教学主题 |
| `lesson_question` | 后续出题节点生成的问题 |
| `learner_answer` | 学员提交的答案 |
| `is_correct` | 批改节点给出的判断 |
| `feedback` | 给学员看的反馈 |
| `material_sources` | 后续 RAG 节点可附带的资料来源 |
| `completed_steps` | 记录已经走过的流程步骤 |

### `LearningStateUpdate` 表达节点的局部输出

LangGraph 节点通常不需要返回完整 state。比如批改节点只需要更新：

```python
{
    "is_correct": True,
    "feedback": "答对了。",
    "completed_steps": ["grade_answer"],
}
```

因此项目定义：

```python
class LearningStateUpdate(TypedDict, total=False):
    current_topic: str
    lesson_question: str
    learner_answer: str
    is_correct: bool | None
    feedback: str
    material_sources: list[str]
    completed_steps: list[str]
```

`total=False` 表示这些字段都不是每次更新必须提供。后续 node 可以只返回自己负责的字段。

### reducer 决定字段如何合并

LangGraph State 不只是字段集合，还要知道节点返回更新时如何合并。默认语义通常是替换字段值；但有些字段需要累加。

例如 `completed_steps` 应该保留流程历史：

```text
["assess_level"] + ["teach_topic"] + ["grade_answer"]
```

所以它使用：

```python
completed_steps: Annotated[list[str], add]
```

这里的 `add` 来自 `operator.add`。后续接入 LangGraph 时，这个标注可以告诉图运行时：新步骤应该追加，而不是覆盖旧列表。

### 初始状态来自现有 Student

项目已有 `Student`：

```python
class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]
```

`create_initial_learning_state()` 负责把它转换成图需要的状态：

```text
Student
-> LearningState
```

这一步不会读取文件，也不会调用模型。调用方可以从 CLI、API 或测试里先取得 `Student`，再生成初始 state。

`python_level` 会在初始化时校验，只允许：

```text
beginner
basic
intermediate
```

不要把无效学习水平放进图状态。类型标注是给开发者和工具看的，运行时入口仍要拒绝坏数据。

### 7.2 仍不创建 `StateGraph`

当前只定义状态结构。没有 node 和 edge 时，创建 `StateGraph` 只是空架子。后续顺序是：

```text
7.2 定义 LearningState
7.3 实现第一个 node
7.4 串联多个 node
7.5 添加条件分支
7.6 暴露 API
```

这个顺序让每一步都有可测试的业务产物。

## 5. 代码实现

新增：

```text
ai-learning-assistant/app/graph.py
```

先定义 Python 水平类型：

```python
from operator import add
from typing import Annotated, Literal, TypedDict, cast

from app.models import Student


PythonLevel = Literal["beginner", "basic", "intermediate"]
VALID_PYTHON_LEVELS: tuple[PythonLevel, ...] = ("beginner", "basic", "intermediate")
```

定义完整 state：

```python
class LearningState(TypedDict):
    student_name: str
    learning_goal: str
    python_level: PythonLevel
    current_topic: str
    lesson_question: str
    learner_answer: str
    is_correct: bool | None
    feedback: str
    material_sources: list[str]
    completed_steps: Annotated[list[str], add]
```

定义节点局部更新：

```python
class LearningStateUpdate(TypedDict, total=False):
    current_topic: str
    lesson_question: str
    learner_answer: str
    is_correct: bool | None
    feedback: str
    material_sources: list[str]
    completed_steps: list[str]
```

校验学习水平：

```python
def _validate_python_level(python_level: str) -> PythonLevel:
    if python_level not in VALID_PYTHON_LEVELS:
        raise ValueError("python_level must be beginner, basic, or intermediate")
    return cast(PythonLevel, python_level)
```

创建初始状态：

```python
def create_initial_learning_state(
    student: Student,
    *,
    current_topic: str = "python_basics",
) -> LearningState:
    topic = current_topic.strip()
    if topic == "":
        raise ValueError("current_topic must not be empty")

    return {
        "student_name": student["name"],
        "learning_goal": student["goal"],
        "python_level": _validate_python_level(student["python_level"]),
        "current_topic": topic,
        "lesson_question": "",
        "learner_answer": "",
        "is_correct": None,
        "feedback": "",
        "material_sources": [],
        "completed_steps": [],
    }
```

新增测试：

```text
ai-learning-assistant/tests/test_graph.py
```

测试覆盖：

- 学员资料会被映射到初始 state。
- 空白 `current_topic` 会被拒绝。
- 未知 `python_level` 会被拒绝。
- `completed_steps` 保留 `Annotated[..., add]` 标注。
- `LearningStateUpdate` 可以表达局部 node 输出。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行新增测试：

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

手动查看初始状态：

```powershell
py -3.13 -c "from app.graph import create_initial_learning_state; from app.storage import create_default_student; student=create_default_student(); student['name']='Alice'; student['goal']='学习 LangGraph'; student['python_level']='basic'; print(create_initial_learning_state(student))"
```

这一步不需要真实 provider，也不需要本地 Ollama。

## 7. 常见错误

### 把 Student 直接当成图状态

`Student` 是本地学习档案，字段更偏持久化资料。`LearningState` 是学习流程运行时状态，除了学员资料，还要包含当前主题、题目、答案、反馈和流程步骤。两者不能混用。

### 把所有字段都塞成字符串

`is_correct` 应该是 `bool | None`，因为流程开始时尚未批改。`material_sources` 和 `completed_steps` 应该是列表，因为后续可能有多个来源和多个步骤。

### 让每个 node 返回完整 state

节点只应该返回自己负责的局部更新。强迫每个 node 返回整份 state，会让节点之间互相覆盖字段，也会增加重复代码。

### 忘记 reducer 语义

`completed_steps` 是历史记录，不能每次更新都覆盖。先用 `Annotated[list[str], add]` 表达这个意图，后续接入 LangGraph 时才能自然保留步骤轨迹。

### 在 7.2 就新增显式 LangGraph 依赖

现在还没有 graph runtime 代码。显式新增依赖必须服务真实实现，不是为了让课程看起来“进入框架了”。后续真正创建图时，再根据官方接口和当前环境决定是否需要锁定 `langgraph` 版本。

## 8. 练习

练习 1：说明 `Student` 和 `LearningState` 的字段差异。

练习 2：给 `teach_topic` node 写一个可能返回的 `LearningStateUpdate` 字典。

练习 3：解释为什么 `is_correct` 不能只用 `bool`，而要允许 `None`。

练习 4：如果 `completed_steps` 没有 reducer，后续多个节点更新它时会出现什么问题？

练习 5：判断下面哪些字段应该放进 `LearningState`，哪些应该留在持久化或配置层：

```text
student_name
api_key
current_topic
provider_base_url
feedback
```

## 9. 验收标准

完成后，应能做到：

- 定义 `LearningState`，包含学习流程需要的核心字段。
- 定义 `LearningStateUpdate`，表达 node 的局部更新。
- 使用 `Annotated[list[str], add]` 给 `completed_steps` 标注累加语义。
- 使用 `create_initial_learning_state()` 从 `Student` 创建初始状态。
- 拒绝空白 `current_topic`。
- 拒绝未知 `python_level`。
- 说明当前仍未创建 `StateGraph`、node、edge 或 API。
- 运行 `py -3.13 -m pytest tests/test_graph.py` 通过。
- 运行完整 `pytest` 和 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| `LearningState` | 7.3：第一个 node 读取并更新 state |
| `LearningStateUpdate` | 7.3 到 7.5：节点统一返回局部更新 |
| `completed_steps` reducer | 后续图执行时保留流程轨迹 |
| `material_sources` | 后续 RAG node 可记录资料来源 |
| `is_correct` | 7.5：条件分支根据批改结果走不同路径 |
| 初始 state 工厂函数 | 7.6：API 调 Graph 前构造会话状态 |
| checkpoint | Stage 8：持久化和恢复状态 |
| Deep Agents | Stage 9：长任务可读取或生成学习计划状态 |

课程继续使用同一条真实代码主线：

```text
ai-learning-assistant/
```

不会为这节课创建单独的示例项目或代码快照。

## 11. 本课变更清单

新增文件：

- `ai-learning-assistant/app/graph.py`
- `ai-learning-assistant/tests/test_graph.py`
- `docs/tutorial/lessons/stage-7/07-02-learning-state.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- 新增 `LearningState`。
- 新增 `LearningStateUpdate`。
- 新增 `create_initial_learning_state()`。
- 新增 `tests/test_graph.py` 覆盖初始状态、空 topic、未知学习水平、reducer 标注和局部更新。

新增依赖：无。

环境变量变更：无。

官方文档核对：

- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)

下一步：第 7.3 课，实现第一个学习流程节点。
