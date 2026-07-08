# 第 4.1 课：LLM 基础概念

## 1. 本课目标

阶段 3 已经把学习助手变成了 FastAPI API。

从阶段 4 开始，项目要第一次接入大模型。真正写代码之前，你必须先知道一次模型调用里到底有哪些东西。

本课目标是讲清楚：

- 什么是 LLM。
- 什么是 `model`。
- 什么是 prompt、message、instructions 和 input。
- 什么是 token。
- 为什么模型调用不是普通函数调用。
- 为什么阶段 4.1 先不写真实 API Key 和真实模型请求。
- 后续 `llm.py` 会负责什么。

本课不改代码、不新增依赖、不要求联网运行。

你现在要先建立概念坐标，下一课再处理 API Key 和环境变量。

## 2. 你会新增什么项目能力

本课不会新增运行能力。

本课新增的是你对项目下一步升级的判断能力：

```text
知道规则建议和 AI 建议的区别。
知道一次模型调用需要 model、instructions、input。
知道为什么 prompt 不是魔法咒语，而是给模型的任务说明。
知道 message 为什么适合表达对话。
知道 token 会影响上下文长度、速度和成本。
知道后续应该把模型调用封装在 llm.py，而不是散落到 route 里。
```

阶段 3 的学习建议接口现在是：

```text
GET /suggestion
-> build_suggestion(student["python_level"])
-> 返回写死规则建议
```

后续阶段 4 会逐步升级成：

```text
GET /suggestion
-> load_student()
-> call_llm(...)
-> 返回 AI 生成的学习建议
```

本课先讲 `call_llm(...)` 背后的概念。

## 3. 前置知识

开始前，你应该已经理解：

- Python 函数如何接收参数并返回结果。
- 字典和列表如何保存结构化数据。
- FastAPI route 如何接收请求并返回响应。
- Pydantic 模型如何表达请求体和响应体。
- `GET /suggestion` 当前如何返回规则建议。
- `storage.py` 当前如何读取学习档案。

你还不需要：

- OpenAI API Key。
- `.env` 配置。
- LangChain。
- LangGraph。
- Deep Agents。

这些后面会逐步进入。

## 4. 核心概念

### LLM 是什么

LLM 是 Large Language Model，大语言模型。

在项目里，你可以先把它理解成：

```text
一个接收文本任务，并生成文本结果的模型服务。
```

例如你给它：

```text
你是一个 Python 学习助教。
学员水平是 beginner。
请生成今天的学习建议。
```

它可能返回：

```text
今天建议先复习变量、函数和字典，然后用一个小练习把三者连起来。
```

注意，它不是普通的 Python 函数。

普通函数更像这样：

```python
def build_suggestion(python_level: str) -> str:
    if python_level == "beginner":
        return "建议：今天学习变量、函数、字典。"
```

输入相同，输出通常完全相同。

LLM 更像一个基于上下文生成结果的模型。

同样的任务，如果上下文、模型、参数或历史消息不同，结果可能不同。

### `model` 是什么

`model` 表示你要调用哪个模型。

可以先理解成：

```text
model = 负责生成结果的大脑型号
```

后续代码里会出现类似：

```python
model="..."
```

不同模型在能力、速度、成本、上下文长度和适合任务上可能不同。

本课程不会在 4.1 固定某个模型名，因为模型列表和推荐会变化。

真正写调用代码时，要以当时官方文档为准。

### prompt 是什么

prompt 是你给模型的任务说明。

不要把 prompt 理解成一句神秘口令。

更准确地说，它是：

```text
你希望模型根据哪些上下文、按照什么角色、完成什么任务、用什么格式回答。
```

一个很弱的 prompt：

```text
给我学习建议。
```

一个更清楚的 prompt：

```text
你是一个 Python 学习助教。
学员当前水平是 beginner。
学员目标是学习 FastAPI。
请给出 3 条今天可以执行的学习建议。
回答要简洁，每条不超过 30 字。
```

区别不是文案长短，而是任务边界是否清楚。

### instructions 是什么

在一些模型调用接口里，`instructions` 用来放比较稳定的高层行为要求。

例如：

```text
你是一个耐心、直接、重视练习的 Python 学习助教。
你只给适合当前水平的建议。
```

它更像“这个助手长期应该怎么做”。

而某一次具体问题可以放在 `input` 里。

例如：

```text
学员水平：beginner
学习目标：掌握 FastAPI
请生成今日学习建议。
```

你可以先这样区分：

| 名称 | 适合放什么 |
| --- | --- |
| `instructions` | 稳定角色、长期规则、回答风格 |
| `input` | 本次具体任务、用户问题、当前数据 |

### input 是什么

`input` 是本次请求给模型的具体内容。

在学习助手里，它可能来自：

```text
student["name"]
student["goal"]
student["python_level"]
student["notes"]
```

例如：

```text
学员：Alice
目标：学习 LangChain
Python 水平：basic
最近笔记：
1. FastAPI route 是普通函数加装饰器
2. Pydantic 会校验请求体

请生成今天的学习建议。
```

后续 `llm.py` 的一部分工作，就是把项目里的结构化数据整理成模型能理解的 `input`。

### message 是什么

message 用来表达对话中的一条消息。

常见角色包括：

```text
system / developer / user / assistant
```

你现在不需要死记所有角色差异。

先建立最小理解：

| 角色 | 可以先理解成 |
| --- | --- |
| system / developer | 高优先级规则或开发者约束 |
| user | 用户提出的问题 |
| assistant | 模型之前给出的回答 |

对话不是只有最后一句话。

如果你要让模型理解上下文，就要把必要的历史消息或状态传给它。

这也是为什么后面 LangGraph 会重要：它可以更明确地管理“当前学到哪一步、上一轮答了什么、下一步该做什么”。

### token 是什么

token 是模型处理文本时使用的基本片段。

它不完全等于中文字符，也不完全等于英文单词。

你可以先把它理解成：

```text
模型读写文本时的计量单位。
```

token 影响三件事：

- 上下文长度：一次请求能放多少内容。
- 响应长度：模型最多能生成多少内容。
- 成本和速度：输入输出越多，通常越慢也越贵。

所以后续做 RAG 时，不能把所有资料一股脑塞给模型。

你要先检索相关片段，再把最有用的内容放进输入。

### 模型调用不是普通函数调用

普通函数调用：

```text
输入参数 -> 确定逻辑 -> 返回结果
```

模型调用：

```text
模型 + instructions + input + 上下文 + 参数
-> 生成结果
```

所以你要额外关心：

- 输入是否清楚。
- 输出是否稳定。
- 是否需要结构化输出。
- 出错时如何重试或降级。
- 结果是否需要验证。

这就是为什么后续课程不会把模型调用直接写进 route。

## 5. 代码实现

本课不改代码。

当前项目仍然使用规则函数生成学习建议：

```text
ai-learning-assistant/app/suggestions.py
```

当前 API 仍然是：

```text
GET /suggestion
-> build_suggestion(...)
```

后续阶段 4 会新增：

```text
ai-learning-assistant/app/llm.py
```

它会负责封装模型调用。

先不要把模型调用直接写到：

```text
app/api.py
```

原因很简单：route 应该表达 API 流程，模型调用细节应该被隔离。

未来更合理的方向是：

```text
api.py
-> llm.py
-> OpenAI / 其它模型服务
```

或者再往后：

```text
api.py
-> langchain_agent.py
-> tools / model
```

## 6. 运行方式

本课不需要运行新代码。

仍然可以运行当前测试，确认阶段 3 项目没有被破坏：

```powershell
cd ai-learning-assistant
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

如果你想回看当前规则建议接口：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

然后访问：

```text
GET http://127.0.0.1:8000/suggestion
```

它现在仍然返回规则建议，不是 AI 生成建议。

## 7. 常见错误

### 以为 LLM 一定会返回同样结果

不要把 LLM 当成普通 `if/else` 函数。

它是生成式模型。

如果你需要稳定结构，后面要学习结构化输出和结果校验。

### 把 prompt 写成一句模糊愿望

例如：

```text
帮我学 Python。
```

这太宽。

更好的输入要包含：

```text
当前水平
学习目标
已有笔记
希望输出的格式
```

### 在 route 里直接调用模型

不要在 `api.py` 里到处散落模型请求。

短期看省事，长期会导致：

- API 难测。
- 错误处理混乱。
- 后续切换 LangChain 时要大改。
- API Key 和配置容易被写散。

模型调用应该先封装到 `llm.py`。

### 在课程一开始就硬编码 API Key

API Key 不应该写进代码。

后面会用 `.env` 或环境变量读取。

本课先不做这一步。

### 不理解 token 就开始塞资料

模型上下文不是无限的。

资料越多越不一定越好。

后面 RAG 阶段会专门解决“怎么只给模型相关资料”的问题。

## 8. 练习

练习 1：用自己的话解释下面 4 个词：

```text
model
prompt
message
token
```

练习 2：把下面的弱 prompt 改得更清楚：

```text
给我学习建议。
```

要求包含：

```text
学员水平
学习目标
输出条数
输出格式
```

练习 3：观察当前项目，回答：

```text
如果要让 /suggestion 变成 AI 生成建议，需要哪些数据作为 input？
```

至少列出：

```text
name
goal
python_level
notes
```

练习 4：判断哪些内容适合放进 `instructions`，哪些适合放进 `input`：

| 内容 | instructions 还是 input |
| --- | --- |
| 你是一个 Python 学习助教 | instructions |
| 学员水平是 beginner | input |
| 回答要适合初学者 | instructions |
| 学员今天新增了 3 条笔记 | input |
| 输出 3 条建议 | input |

练习 5：解释为什么不能把所有学习资料直接塞给模型。

## 9. 验收标准

本课完成时，你应该能做到：

- 解释 LLM 和普通函数的区别。
- 解释 `model` 是什么。
- 解释 prompt 不是魔法口令，而是任务说明。
- 区分 `instructions` 和 `input`。
- 解释 message 为什么适合表达对话。
- 解释 token 会影响上下文长度、速度和成本。
- 说出当前 `/suggestion` 仍然是规则建议，不是 AI 建议。
- 说出后续模型调用应该封装到 `llm.py`。
- 知道 API Key 不应该硬编码到代码里。
- `py -3.13 -m pytest` 继续通过。
- `py_compile` 继续通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课是后续所有 Agent 框架的地基。

| 本课概念 | 后续升级 |
| --- | --- |
| prompt | LangChain prompt / agent instructions |
| model | LangChain agent 的模型配置 |
| message | 对话历史、Graph state、Agent trace |
| input | 工具参数、RAG 查询、Graph 节点输入 |
| token | RAG chunk、上下文管理、Deep Agents 长任务压缩 |
| `llm.py` | LangChain / LangGraph / Deep Agents 之前的最小模型调用层 |

LangChain 会把模型和工具组合起来。

LangGraph 会把多步骤对话和学习流程变成可控状态机。

Deep Agents 会处理更长的任务、文件系统和子 Agent。

但它们都绕不开一个基础问题：

```text
你到底给模型什么输入，希望模型按什么规则输出？
```

这就是本课要先讲清楚的东西。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-4/04-01-llm-basic-concepts.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`

代码变更：

- 无。

新增依赖：

- 无。

环境变量变更：

- 无。

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

验证结果：

- 本课不改变运行逻辑。
- 当前 API 和存储测试应继续通过。
- 第一次真实模型调用保留到后续课程。

下一步：

- 第 4.2 课：配置 API Key。
- 用 `.env` 或环境变量安全读取密钥。
- 准备第 4.3 课的第一次真实模型调用。
