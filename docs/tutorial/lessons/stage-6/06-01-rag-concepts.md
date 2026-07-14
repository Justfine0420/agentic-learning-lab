# 第 6.1 课：RAG 是什么

## 1. 本课目标

阶段 5 已经让学习助手能够使用 LangChain Agent 调用本地只读工具，读取学员档案、学习笔记和离线规则建议。

```text
用户问题
-> LangChain Agent
-> 读取 profile / notes / rule suggestion
-> 结构化学习建议
```

这条链路仍然有一个明确限制：Agent 不能根据一组本地 Markdown 学习资料回答问题。把所有资料直接拼进每次 prompt 既浪费上下文，也无法说明答案具体来自哪里。

RAG 是为这个问题建立数据路径的方式：先检索与问题有关的资料片段，再把这些片段连同来源交给模型生成回答。

完成后，你应能解释：

```text
RAG = Retrieval-Augmented Generation
      检索增强生成

资料 -> 切分后的片段 -> 检索相关片段 -> 带来源的回答
```

## 2. 你会新增什么项目能力

这一课新增的是 RAG 的共同语言和项目阶段标识，不新增运行时检索能力。

```text
CLI header: Current stage: Stage 6
```

当前项目仍然可以：

- 通过 CLI 和 `POST /chat` 调用结构化 LangChain Agent。
- 读取 `data/student.json` 中的学员档案和学习笔记。
- 使用 `materials/` 存放课程补充资料。

当前项目还不能：

- 加载 Markdown 为 RAG 文档对象。
- 切分资料、生成 embedding 或建立向量索引。
- 按问题检索片段。
- 让 Agent 或 API 基于资料回答并返回来源。
- 用 LangGraph 编排节点、状态、checkpoint、streaming 或 human-in-the-loop。

这些能力会按照 6.2 到 6.6 的顺序逐步加入。先把概念边界讲清，后面的代码才不会变成一堆名称很新、职责很乱的依赖。

## 3. 前置知识

开始前，应已经理解：

- `app/langchain_agent.py` 如何定义只读 `@tool` 并创建 Agent。
- `app/storage.py` 如何读取本地 JSON 学员数据。
- `app/models.py` 中 `StructuredLearningSuggestion` 如何固定 Agent 输出契约。
- `app/api.py` 中 `/chat` 如何把 Agent/provider 错误转换为 `503`。
- `materials/` 目前保存的是 Markdown 补充资料，但应用尚未加载或检索它们。

还不需要掌握：

- 向量数据库的部署和持久化。
- embedding provider 的模型选择与费用控制。
- 复杂 reranker、混合检索或多模态文档解析。
- LangGraph 的 `StateGraph`、节点、边和 checkpoint。

## 4. 核心概念

### RAG 解决什么问题

模型不会自动知道项目目录中的私有资料，也不应该在每次提问时把整份资料库硬塞进 prompt。资料变多时，这种做法会带来三个问题：

- 上下文越来越长，成本和噪声一起增加。
- 与问题无关的内容会干扰回答。
- 调用方无法知道答案依据的是哪一份资料。

RAG 把“找资料”和“基于资料生成”拆开。LangChain 的 Retrieval 文档将 retrieval 描述为从外部数据源取回相关信息的能力；RAG 是把这一步的结果用于生成回答的一种常见方式。

```text
问题：如何为 Python 函数写类型标注？

错误做法：把 materials/ 下所有 Markdown 一次性拼进 prompt。
RAG 做法：只找到讨论类型标注的几个片段，再要求模型据此回答。
```

### RAG 的最小数据流

后续课程会把下面的每一格实现成可测试的代码：

```text
Markdown 资料
-> Document（内容 + source 元数据）
-> chunk（可检索的小片段）
-> embedding（向量表示）
-> vector store / retriever
-> 与问题相关的片段
-> 模型回答 + 来源引用
```

各组件的职责不同：

| 组件 | 解决的问题 | 课程中的对应小节 |
| --- | --- | --- |
| Document | 资料内容和来源如何一起保存 | 6.2 |
| chunk | 一份资料太长时如何拆成可检索片段 | 6.3 |
| embedding | 如何让语义相近的问题和片段更容易匹配 | 6.4 |
| retriever | 如何按问题取回少量候选片段 | 6.4 |
| answer + sources | 如何让回答附带可追溯依据 | 6.5 |
| API | 如何让外部调用方提交问题并获得结果 | 6.6 |

`Document` 不只是字符串。至少要保留内容和来源路径，例如：

```text
page_content: "Python 类型标注可以说明参数和返回值的预期类型。"
metadata.source: "materials/python_basics.md"
```

来源元数据不能等到回答完成才临时拼出来。检索阶段丢失来源，后续就无法可靠地展示引用，也无法定位错误资料。

### chunk、embedding 和 retriever 不是同一个东西

这三个术语经常被混为一谈，但它们分别解决不同问题：

```text
chunk      = 把长文拆成适合检索的片段
embedding  = 把问题和片段映射到可比较的向量空间
retriever  = 根据问题返回候选片段的接口
```

向量库只是保存和查询向量的一种实现，不等于完整 RAG。即使检索命中了片段，系统仍需要规定：片段如何传给模型、模型如何避免超出证据回答、来源如何返回给调用方。

### 有来源不等于答案一定正确

RAG 的目标是让答案有可检查的依据，不是保证模型永远正确。一个健康的回答边界至少包括：

- 检索结果不支持答案时，明确说明资料不足。
- 只把检索到的片段视为依据，不把模型记忆伪装成资料结论。
- 把来源作为结构化结果的一部分返回，而不是在回答末尾随意编造文件名。
- 测试检索、来源和失败路径，不用一次真实模型调用替代全部测试。

### RAG、LangChain Agent 和 LangGraph 的边界

阶段 5 的 LangChain Agent 解决的是“模型如何选择并调用工具”。阶段 6 的 RAG 会新增一种读资料能力：retriever。它可以被普通业务函数调用，也可以在后续作为 Agent 的只读工具。

```text
LangChain Agent：模型、工具、prompt 和 Agent loop
RAG：从外部资料取回证据，再让模型据此回答
LangGraph：对长期、有状态、多步骤流程做低层编排
```

LangGraph 官方概述把它定位为长时间运行的有状态 Agent 的低层编排框架与运行时，重点包括持久执行、streaming、人机协作和记忆。这些能力很重要，但它们不替代 RAG 的资料加载、切分和检索。

当前阶段不会提前创建 `StateGraph`。后续学习流程需要“评估水平 -> 教学 -> 出题 -> 批改 -> 条件分支”时，才进入 Stage 7 的 node、edge 和 state。RAG 在此之前先解决一个更小的问题：回答时如何拿到可追溯的资料证据。

### RAG 和微调的边界

RAG 是在请求时读取和检索外部资料；微调是改变模型参数以学习模式或行为。课程中的本地学习资料会变化，也需要显示来源，因此先使用 RAG。它不要求把资料拿去训练模型，也不应把可更新的 Markdown 误当成微调数据集。

## 5. 代码实现

这一课只同步 CLI 的阶段展示，并为它加回归断言。

打开：

```text
ai-learning-assistant/app/cli.py
```

把：

```python
COURSE_STAGE = "Stage 5"
```

改为：

```python
COURSE_STAGE = "Stage 6"
```

`show_header()` 已经集中读取 `COURSE_STAGE`，因此不需要复制展示逻辑。测试直接覆盖对学习者可见的输出：

```python
def test_show_header_displays_stage_6(capsys) -> None:
    cli.show_header()

    assert capsys.readouterr().out == (
        "Project: AI Learning Assistant\n"
        "Current stage: Stage 6\n"
    )
```

范围外的文件包括：

```text
requirements.txt
.env.example
app/rag.py
app/langchain_agent.py
app/api.py
app/models.py
```

它们分别会在资料加载、切分、embedding、检索、回答和 API 小节中按实际需要变化。此时增加占位函数、空路由或未经验证的依赖，只会把后续每一课的责任稀释掉。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

先运行与本课改动直接相关的测试：

```powershell
py -3.13 -m pytest tests/test_cli.py
```

再运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

手动启动 CLI 后，开头应显示：

```text
Project: AI Learning Assistant
Current stage: Stage 6
```

无需为这个概念课配置真实 embedding 模型或调用真实 provider。

## 7. 常见错误

### 把所有资料放进一个 prompt

小样例看起来能运行，不代表它可以扩展。资料越多，噪声、上下文长度和来源不透明的问题就越明显。RAG 的第一步是先缩小证据范围。

### 以为有向量库就完成了 RAG

向量检索只能返回候选片段。没有来源、回答边界和失败处理，系统仍然无法解释“为什么这样回答”。

### 把检索到的片段当成绝对事实

检索可能命中陈旧、片面的或错误的资料。回答必须能指向来源，也必须在资料不足时承认不知道。

### 以为 RAG 就是 LangGraph

RAG 是资料检索和证据增强的模式；LangGraph 是对状态化流程进行编排的运行时。它们可以组合，但没有互相替代关系。

### 在 6.1 就增加向量库和 API

现在还没有确定文档加载、chunk 元数据和 embedding 策略。提前堆叠依赖会掩盖这些设计决策，也无法形成有针对性的测试。

### 把现有 `/chat` 偷偷改成 RAG 入口

`/chat` 当前代表结构化 Agent 学习建议。RAG API 会在 6.6 明确命名、定义输入输出和错误边界，不能让同一条路由承载两个不同契约。

## 8. 练习

练习 1：用自己的话解释下面两条路径的差别。

```text
把全部资料拼进 prompt
问题 -> retriever -> 少量相关片段 -> 回答 + sources
```

练习 2：为“如何给函数添加类型标注？”写出 RAG 流程中应该出现的 source、chunk、问题和回答来源。

练习 3：查看 `ai-learning-assistant/materials/`，说明为什么 Markdown 文件还不能直接算作 RAG 能力。

练习 4：判断下列需求属于 RAG 还是 LangGraph：

```text
A. 根据问题找回类型标注资料，并展示文件来源。
B. 学员答错后回到教学节点，答对后进入下一题，并允许中断后恢复。
```

练习 5：说明在资料没有覆盖问题时，API 和回答应该如何表现，才不会把猜测伪装成资料结论。

## 9. 验收标准

完成后，应能做到：

- 解释 RAG 中 retrieval、augmentation 和 generation 的职责。
- 区分 Document、chunk、embedding、vector store 和 retriever。
- 解释为什么 `source` 元数据必须从资料加载阶段保留到响应阶段。
- 说明 RAG 不等于“把所有资料拼进 prompt”，也不等于“装一个向量库”。
- 说清 RAG、LangChain Agent 和 LangGraph 各自解决的问题。
- 说明当前项目还没有 RAG 运行时实现，以及它将在 6.2 到 6.6 中如何逐步形成。
- 运行 `py -3.13 -m pytest tests/test_cli.py` 通过。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过，并在 CLI 中看到 `Current stage: Stage 6`。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前概念 | 后续升级 |
| --- | --- |
| Markdown 资料 | 6.2：加载为带来源的 Document |
| 长文难以直接检索 | 6.3：按策略切分 chunk |
| 问题和资料的相关性 | 6.4：embedding、向量索引和 retriever |
| 带证据的回答 | 6.5：answer + sources 契约 |
| 外部调用入口 | 6.6：`POST /ask-materials` |
| retriever | 后续可以成为 LangChain Agent 的只读工具 |
| 多步骤学习会话 | Stage 7：LangGraph State、node 和 edge |
| 持久执行、streaming、人机协作 | Stage 8：LangGraph 进阶 |
| 长任务规划和文件产物 | Stage 9：Deep Agents |

课程继续使用同一条真实代码主线：

```text
ai-learning-assistant/
```

不会为这节课创建单独的示例项目或代码快照。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-6/06-01-rag-concepts.md`

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

- CLI 阶段展示从 `Stage 5` 同步为 `Stage 6`。
- 新增对 `show_header()` 输出的回归测试。

新增依赖：无。

环境变量变更：无。

官方文档核对：

- [LangChain Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangGraph 概述（中文参考）](https://langchain-doc.cn/v1/python/langgraph/overview.html)

下一步：第 6.2 课，加载本地学习资料并保留来源元数据。
