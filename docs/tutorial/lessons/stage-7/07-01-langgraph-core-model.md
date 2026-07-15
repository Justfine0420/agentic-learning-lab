# 第 7.1 课：LangGraph 核心模型

## 1. 本课目标

阶段 6 已经完成基础 RAG 闭环：项目能读取本地 Markdown 资料，切分、检索、生成带来源的资料回答，并通过 `POST /ask-materials` 暴露给外部调用方。

现在开始 Stage 7：LangGraph 基础。

这一课先建立 LangGraph 的核心模型，不急着写完整图：

```text
State
-> node
-> edge
-> compiled graph
```

完成后，你应能解释：

- LangGraph 为什么不是 RAG，也不是另一个向量检索库。
- State、node 和 edge 分别是什么。
- 为什么 LangGraph 适合学习流程这类多步骤状态机。
- 为什么当前不会把 `POST /ask-materials` 改成图。
- 为什么第 7.1 课只同步项目阶段标识，不新增 `langgraph` 依赖。

## 2. 你会新增什么项目能力

这一课新增的是 Stage 7 的概念边界和项目阶段标识：

```text
CLI header: Current stage: Stage 7
```

代码只改：

```text
app/cli.py
tests/test_cli.py
```

当前项目仍然可以：

- 运行 CLI。
- 运行 FastAPI。
- 调用结构化 LangChain Agent。
- 通过 `POST /ask-materials` 做本地资料 RAG 问答。

当前项目还不能：

- 定义 `LearningState`。
- 创建 `StateGraph`。
- 添加 LangGraph node 或 edge。
- 跑学习流程状态机。
- 使用 checkpoint、streaming 或 human-in-the-loop。

这些能力会从 7.2 开始逐步加入。先把框架职责讲清楚，后面的代码才不会变成“能跑但没人知道边界”的图。

## 3. 前置知识

开始前，应已经理解：

- Python 字典和 TypedDict 可以表达结构化状态。
- 普通函数可以接收输入并返回结果。
- Stage 5 中 LangChain Agent 负责模型与工具调用。
- Stage 6 中 RAG 负责资料检索和基于证据回答。
- 当前学习助手已经有 CLI、FastAPI、Agent 和 RAG 四条能力线。

还不需要掌握：

- `StateGraph` 的完整 API。
- checkpoint 存储。
- streaming 事件协议。
- human-in-the-loop。
- 多分支恢复和时间旅行。

## 4. 核心概念

### LangGraph 解决什么问题

LangChain Agent 更关注模型如何调用工具。RAG 更关注如何从外部资料里找证据。LangGraph 关注的是另一类问题：多步骤、有状态、需要明确控制流的任务。

学习流程就是典型例子：

```text
评估水平
-> 教一个小知识点
-> 出一道题
-> 批改答案
-> 答对进入下一题
-> 答错回到讲解或提示
```

这个流程不是一次普通函数调用，也不是一次资料检索。它需要记录当前学习状态，并根据结果决定下一步走哪里。

### State 是图里的共享状态

State 是节点之间传递和更新的数据。它可以包含：

```text
student_name
python_level
current_topic
question
answer
is_correct
feedback
```

在 LangGraph 中，节点不会靠隐藏全局变量沟通。节点读取 state，返回对 state 的更新。图把这些更新合并后，再交给下一步节点。

先把 state 想清楚，比先写节点更重要。状态字段混乱，图很快会变成一堆互相猜数据的函数。

### Node 是一步可测试的工作

node 是图中的一个处理步骤。它通常可以理解成一个普通 Python 函数：

```text
state -> partial state update
```

例如：

```text
assess_level
teach_topic
ask_question
grade_answer
```

一个 node 不应该包办整条学习流程。节点越像“一个清楚动作”，后续测试、分支和错误恢复越容易。

### Edge 决定下一步

edge 表达节点之间怎么连接：

```text
assess_level -> teach_topic
teach_topic -> ask_question
ask_question -> grade_answer
```

条件分支也是 edge 的一类：

```text
grade_answer
-> is_correct=True  -> next_topic
-> is_correct=False -> explain_again
```

这就是 LangGraph 比普通顺序函数更适合学习流程的原因：流程结构被显式表达出来，而不是藏在一堆嵌套 `if/else` 里。

### Compile 之后才是可运行图

LangGraph 的 Graph API 会先定义状态、节点和边，再编译成可调用对象。可以把它理解成：

```text
定义图结构
-> 检查图结构
-> compile()
-> invoke()
```

第 7.1 课不写这段代码，是因为当前还没有 `LearningState` 和任何业务节点。直接空降 `StateGraph` 示例，只会让学习者记住 API 拼法，而不是理解它解决的问题。

### LangGraph 不替代现有能力

Stage 7 不会删除：

```text
GET /suggestion
POST /ai/suggestion
POST /chat
POST /ask-materials
```

LangGraph 是下一层流程编排。它可以在后续节点中复用已有能力，例如：

```text
teach_topic node -> 调用 RAG 回答资料问题
advisor node     -> 调用 LangChain Agent 生成建议
```

但这些复用必须在流程状态和节点职责明确之后再做。

## 5. 代码实现

这一课只同步 CLI 的阶段展示。

打开：

```text
ai-learning-assistant/app/cli.py
```

把：

```python
COURSE_STAGE = "Stage 6"
```

改为：

```python
COURSE_STAGE = "Stage 7"
```

测试同步更新：

```python
def test_show_header_displays_stage_7(capsys) -> None:
    cli.show_header()

    assert capsys.readouterr().out == (
        "Project: AI Learning Assistant\n"
        "Current stage: Stage 7\n"
    )
```

本次不新增：

```text
langgraph
app/graph.py
tests/test_graph.py
LearningState
StateGraph
```

第 7.2 才开始定义学习流程的 state。没有 state 就先写图，属于倒着来。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行本课直接相关测试：

```powershell
py -3.13 -m pytest tests/test_cli.py
```

运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

手动查看 CLI 开头：

```powershell
py -3.13 -m app.main
```

应看到：

```text
Project: AI Learning Assistant
Current stage: Stage 7
```

无需安装 LangGraph，也无需配置真实 provider。当前没有新增图运行时代码。

## 7. 常见错误

### 以为 LangGraph 就是 RAG

不对。RAG 解决资料检索和证据增强；LangGraph 解决流程状态、节点和分支。后续可以在 node 中调用 RAG，但两者不是同一层能力。

### 一上来就写 `StateGraph`

没有明确 state、node 和 edge 时，先写 API 只会得到一个形式正确但业务模糊的图。第 7.1 课先建立模型，第 7.2 再定义 `LearningState`。

### 把所有逻辑塞进一个 node

如果一个节点同时评估、教学、出题、批改和生成总结，它就只是换了名字的大函数。图的价值在于把步骤拆清楚，并让边表达流程。

### 把 edge 写成隐藏的 if/else

条件分支应该成为图结构的一部分。否则学习流程在哪里分支、如何测试、失败后回到哪里，都会变得不透明。

### 认为 Stage 7 会替换现有 API

不会。现有 CLI、FastAPI、Agent 和 RAG 能力是后续图节点可以复用的业务能力。LangGraph 是编排层，不是把已有接口推倒重写。

## 8. 练习

练习 1：把“学习一节 Python 类型标注课程”拆成 4 个 node 名称。

练习 2：写出这些 node 之间最简单的 edge 顺序。

练习 3：给“答对 / 答错”设计一个条件分支，不写代码，只写流程。

练习 4：列出你认为 `LearningState` 至少需要的 5 个字段。

练习 5：解释为什么 `POST /ask-materials` 不应该在 7.1 被改成 LangGraph。

## 9. 验收标准

完成后，应能做到：

- 解释 LangGraph 与 LangChain Agent、RAG 的职责边界。
- 解释 State、node、edge 和 compiled graph 的关系。
- 说明学习流程为什么适合用状态图表达。
- 说明为什么当前不新增 `langgraph` 依赖和 `app/graph.py`。
- 将 CLI header 同步为 `Current stage: Stage 7`。
- 运行 `py -3.13 -m pytest tests/test_cli.py` 通过。
- 运行完整 `pytest` 和 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前概念 | 后续升级 |
| --- | --- |
| State | 7.2：定义 `LearningState` |
| node | 7.3：实现第一个学习流程节点 |
| edge | 7.4：串联多节点流程 |
| 条件分支 | 7.5：答对 / 答错走不同路径 |
| compiled graph | 7.6：通过 FastAPI 调用学习流程 |
| RAG 函数层 | 后续可作为资料讲解节点复用 |
| LangChain Agent | 后续可作为建议或计划节点复用 |
| checkpoint / streaming / human-in-the-loop | Stage 8：LangGraph 进阶 |
| 长任务规划与文件产物 | Stage 9：Deep Agents |

课程继续使用同一条真实代码主线：

```text
ai-learning-assistant/
```

不会为这节课创建单独的示例项目或代码快照。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-7/07-01-langgraph-core-model.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/tests/test_cli.py`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- CLI 阶段展示从 `Stage 6` 同步为 `Stage 7`。
- 更新对 `show_header()` 输出的回归测试。

新增依赖：无。

环境变量变更：无。

官方文档核对：

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)

下一步：第 7.2 课，定义 `LearningState`。
