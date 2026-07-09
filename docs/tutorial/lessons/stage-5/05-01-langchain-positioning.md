# 第 5.1 课：LangChain 定位

## 1. 本课目标

阶段 4 已经让项目具备真实 LLM 调用能力：

```text
app/config.py -> 读取 provider 配置
app/llm.py    -> 手写 OpenAI 兼容 chat/completions 调用
app/api.py    -> POST /ai/suggestion
app/cli.py    -> 4. 生成 AI 学习建议
```

从阶段 5 开始，我们进入 LangChain。

但第一课先不急着安装依赖，也不急着把 `llm.py` 改掉。你要先搞清楚：

- LangChain 到底解决什么问题。
- `create_agent` 是什么。
- agent harness 是什么。
- LangChain、LangGraph、Deep Agents 的边界分别在哪里。
- 阶段 4 手写的模型调用，后续会怎样迁移到 LangChain。
- 为什么本阶段先从工具调用开始，而不是直接进入 LangGraph 或 Deep Agents。

本课完成后，你应该能解释：

```text
LangChain 不是“另一个 HTTP 请求库”。
LangChain 负责把 model、tools、prompt 和 agent loop 组合成 agent harness。
LangGraph 是更底层的有状态编排运行时。
Deep Agents 是更完整的高层 agent harness。
```

## 2. 你会新增什么项目能力

本课主要新增理解能力，不新增 LangChain 运行能力。

项目层面只同步当前阶段展示：

```text
CLI header: Current stage: Stage 5
```

本课不会新增：

```text
langchain 依赖
langchain_agent.py
POST /chat
工具调用
RAG
LangGraph State
Deep Agent 文件写入
```

这些会从第 5.2 课开始逐步进入。

本课的价值是避免后面一上来就把代码改乱：

```text
Stage 4 手写 LLM 调用
-> Stage 5 LangChain Agent
-> Stage 6 RAG
-> Stage 7/8 LangGraph
-> Stage 9 Deep Agents
```

每一步都有明确职责，不把所有框架揉成一锅。

## 3. 前置知识

开始前，你应该已经理解：

- `app/config.py` 如何读取 `LLM_PROVIDER`、API Key、base URL 和 model。
- `app/llm.py` 如何构造 messages 并调用 `chat/completions`。
- `StructuredLearningSuggestion` 如何校验模型返回的业务 JSON。
- `POST /ai/suggestion` 和 `GET /suggestion` 为什么分开。
- CLI 为什么直接复用业务函数，而不是通过 HTTP 调本地 API。
- provider 不可用时为什么返回 `503` 或打印明确失败提示。

你还不需要：

- LangChain 的安装命令。
- LangChain provider 适配细节。
- tool decorator。
- LangGraph node / edge。
- Deep Agents 的文件系统和子 Agent。

这些后面会一课一课加。

## 4. 核心概念

### LangChain 的定位

根据当前官方文档，LangChain 现在强调的是：

```text
create_agent = 一个可配置的 agent harness
```

你可以先把 LangChain 理解成：

```text
把模型、工具、prompt 和 agent loop 组合起来的框架。
```

阶段 4 的代码更像这样：

```text
你自己准备 messages
你自己发 HTTP 请求
你自己解析 choices[0].message.content
你自己决定什么时候调用什么函数
```

Stage 5 的目标是逐步升级成：

```text
把 Python 函数注册成 tools
把模型交给 agent
把用户问题交给 agent
让 agent 判断是否需要调用工具
最后返回回答或结构化结果
```

也就是说，LangChain 的重点不只是“调用模型”，而是“让模型在一个受控 harness 里调用工具完成任务”。

### 什么是 agent harness

`harness` 可以先理解成“运行外壳”。

单独的模型只会生成文本。

一个 agent harness 会额外处理：

- 用哪个模型。
- 给模型什么 system prompt。
- 当前有哪些 tools 可用。
- 模型要求调用工具时，如何执行工具。
- 工具结果如何再交回模型。
- 最后如何把结果返回给调用方。

阶段 4 的 `generate_structured_learning_suggestion()` 是一次模型调用：

```text
student -> messages -> model -> structured suggestion
```

阶段 5 的 agent 会变成：

```text
user message
-> agent
-> model 判断要不要调用工具
-> tool 查询学员资料或学习笔记
-> model 基于工具结果回答
```

### `create_agent` 是什么

官方示例中，`create_agent` 的基本形态是：

```python
from langchain.agents import create_agent


agent = create_agent(
    model="provider:model-name",
    tools=[some_tool],
    system_prompt="You are a helpful assistant",
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "用户问题"}]}
)
```

这个示例本课不运行。

它只是让你看清楚三个核心输入：

| 参数 | 作用 |
| --- | --- |
| `model` | 使用哪个模型 |
| `tools` | agent 可以调用哪些 Python 函数 |
| `system_prompt` | agent 的长期角色和行为边界 |

这些概念和阶段 4 的代码可以对应起来：

| Stage 4 | Stage 5 |
| --- | --- |
| `LLMSettings.model` | `create_agent(model=...)` |
| `SYSTEM_INSTRUCTIONS` | `system_prompt` |
| `build_learning_suggestion_messages()` | `agent.invoke({"messages": ...})` |
| `load_student()` | 查询学员资料 tool |
| `build_suggestion()` | 离线建议 tool |
| `generate_structured_learning_suggestion()` | Agent 结构化输出或 Agent 能力之一 |

### tool 是什么

tool 本质上还是 Python 函数。

区别是：普通函数只给你的代码调用，tool 会被 agent 暴露给模型。

例如当前项目里已有这些函数：

```text
load_student()
save_student(student)
build_suggestion(python_level)
generate_structured_learning_suggestion(student)
```

不是所有函数都适合立刻变成 tool。

Stage 5 会优先选择低风险、可读、无副作用或副作用清楚的函数：

```text
查询学员资料
查询学习笔记
生成离线规则建议
```

暂时不把 `save_student()` 直接暴露给 agent。

原因很简单：写入数据有副作用，后续要先设计确认、权限和错误处理。

### LangChain 和 LangGraph 的区别

LangChain 适合回答：

```text
我如何把模型、工具和 prompt 组合成一个 agent？
```

LangGraph 适合回答：

```text
我如何把一个长期、多步骤、有状态、可恢复的流程编排起来？
```

官方文档把 LangGraph 定位为低层编排框架和运行时，重点能力包括：

- durable execution
- streaming
- human-in-the-loop
- persistence
- stateful workflow

放回我们的项目：

Stage 5 用 LangChain 做：

```text
用户问：我今天学什么？
Agent 调工具查 profile / notes
Agent 返回建议
```

Stage 7 用 LangGraph 做：

```text
判断水平 -> 教学 -> 出题 -> 批改 -> 根据结果分支
```

这两类问题不是一回事。

如果你只是要让模型调用工具，先用 LangChain。
如果你要明确控制学习流程状态、节点和分支，再用 LangGraph。

### LangChain 和 Deep Agents 的区别

Deep Agents 更像是更完整的高层 agent harness。

根据官方文档，它内置了更复杂任务常用的能力：

- 规划任务。
- 使用文件系统管理上下文。
- 派发子 Agent。
- 管理长上下文。
- 在关键点等待人工确认。
- 根据长期使用更新记忆、技能和提示。

放回我们的项目：

Stage 5 的目标是：

```text
能调用工具的 AI 助手
```

Stage 9 的目标才是：

```text
自动规划学习任务
写 study_plan.md
调用子 Agent 做研究或审查
生成长期学习总结
```

所以不要在 Stage 5 直接跳到 Deep Agents。

你现在还需要先理解：

```text
模型如何拿到工具
工具如何返回结果
Agent 如何把工具结果变成回答
```

这些是 Deep Agents 之下的基础。

### 为什么不立刻重写 `llm.py`

阶段 4 的 `app/llm.py` 不是废代码。

它让你先学会了：

- provider 配置。
- OpenAI 兼容请求格式。
- messages。
- JSON mode。
- Pydantic 校验。
- fake client 测试。
- provider 错误边界。

Stage 5 不会一上来删除这些经验。

更合理的路线是：

```text
先保留 llm.py
新增 langchain_agent.py
先做一个最小 LangChain Agent
再逐步比较两条路径的职责差异
最后决定哪些能力迁移，哪些保留
```

这样你能看懂“为什么用 LangChain”，而不是只会把代码替换成新库。

## 5. 代码实现

本课不引入 LangChain 依赖，不新增 `langchain_agent.py`。

只做一个阶段展示同步：

打开：

```text
ai-learning-assistant/app/cli.py
```

把：

```python
COURSE_STAGE = "Stage 4"
```

改成：

```python
COURSE_STAGE = "Stage 5"
```

这不是功能变化，只是告诉学习者当前已经进入 Stage 5。

本课不要改：

```text
requirements.txt
.env.example
app/llm.py
app/api.py
app/models.py
```

原因：

- `requirements.txt` 到第 5.2 课再加入 LangChain。
- `.env.example` 当前 provider 配置仍然够用。
- `llm.py` 是 Stage 4 的模型调用基线。
- `api.py` 里的 `/ai/suggestion` 仍然代表当前稳定 AI 建议入口。
- `models.py` 的结构化输出模型仍然是后续 Agent 输出的重要边界。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

运行测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py
```

查看 CLI 阶段展示：

```powershell
py -3.13 -m app.main
```

启动后应该看到：

```text
Current stage: Stage 5
```

本课不需要运行真实 LangChain agent。

## 7. 常见错误

### 以为 LangChain 只是封装 HTTP 请求

如果只是发 HTTP 请求，阶段 4 的 `app/llm.py` 已经做到了。

LangChain 的价值在于把模型、工具、prompt 和 agent loop 组合起来。

### 以为 LangGraph 是 LangChain 的新名字

不是。

LangChain 偏向模型、工具和 agent harness。
LangGraph 偏向有状态流程编排、持久化、恢复、人工介入和流式运行。

### 以为 Deep Agents 会替代 LangChain

Deep Agents 是更高层的 harness。

你可以把它理解成在更完整的任务执行场景里，帮你内置规划、文件系统、子 Agent 和上下文管理。

它不是让你跳过工具、模型和 agent loop 基础。

### 一进入 Stage 5 就删除 `llm.py`

不要这样做。

`llm.py` 是你理解模型调用边界的基础，也是后续对比 LangChain agent 的参照物。

### 把所有项目函数都暴露成 tool

不要把有副作用的函数随便交给 agent。

例如：

```text
save_student(student)
```

它会修改本地数据。

后续如果要让 agent 写数据，要先有确认、权限和测试边界。

### 在没有官方文档核对时硬写 API

LangChain 生态变化很快。

框架 API、provider 集成和推荐实践都可能变化。

本课程进入每个外部框架小节前，都要先核对官方文档。

## 8. 练习

练习 1：用自己的话解释：

```text
LangChain = model + tools + prompt + agent harness
```

练习 2：观察当前项目，列出 3 个未来可能变成 tool 的函数。

建议从这些里选：

```text
load_student()
build_suggestion()
generate_structured_learning_suggestion()
```

练习 3：判断下面哪个函数暂时不适合直接暴露给 agent，并说明原因：

```text
load_student()
build_suggestion()
save_student()
```

练习 4：解释什么时候用 LangChain，什么时候用 LangGraph。

练习 5：解释 Deep Agents 为什么放在 Stage 9，而不是 Stage 5。

练习 6：画出当前 Stage 4 和未来 Stage 5 的调用链：

```text
Stage 4:
CLI/API -> llm.py -> provider

Stage 5:
CLI/API -> langchain_agent.py -> agent -> tools/model
```

练习 7：阅读官方文档链接，确认 `create_agent` 当前所在模块：

```text
from langchain.agents import create_agent
```

## 9. 验收标准

完成本课后，你应该能做到：

- 解释 LangChain 当前推荐的 `create_agent` 定位。
- 解释 agent harness 是什么。
- 解释 model、tools、system prompt 在 agent 里的职责。
- 说清 Stage 4 的 `llm.py` 和 Stage 5 的 `langchain_agent.py` 未来如何分工。
- 说清 LangChain 和 LangGraph 的边界。
- 说清 Deep Agents 为什么放到后续阶段。
- 解释为什么本课不安装 LangChain。
- 解释为什么本课不删除 `llm.py`。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。
- CLI 启动时展示 `Current stage: Stage 5`。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课是 Stage 5 的入口。

| 本课概念 | 后续升级 |
| --- | --- |
| `create_agent` | 第 5.2 课创建第一个 LangChain Agent |
| `tools` | 第 5.3 课把 Python 函数变成工具 |
| agent harness | 第 5.4 课组合多个工具 |
| system prompt | 第 5.5 课约束结构化 Agent 输出 |
| CLI/API 入口 | 第 5.6 课接入 `POST /chat` |
| tool 调用边界 | Stage 6 RAG retriever 工具 |
| 明确流程控制 | Stage 7 LangGraph State / node / edge |
| 长任务规划 | Stage 9 Deep Agents |

从这里开始，课程会逐步把“模型生成建议”升级成“Agent 会调用工具完成学习任务”。

但路线仍然保持一条真实代码主线：

```text
ai-learning-assistant/
```

不会为每课复制一份代码。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-5/05-01-langchain-positioning.md`

修改文件：

- `README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/cli.py`
- `docs/tutorial/README.md`

代码变更：

- CLI 阶段展示从 `Stage 4` 同步为 `Stage 5`。

新增依赖：

- 无。

环境变量变更：

- 无。

官方文档核对：

- [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents overview](https://docs.langchain.com/oss/python/deepagents/overview)

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py
```

下一步：

- 第 5.2 课：创建第一个 LangChain Agent。
- 正式加入 LangChain 依赖。
- 新增 `app/langchain_agent.py`。
- 先做最小 agent，再把项目函数逐步注册为 tools。
