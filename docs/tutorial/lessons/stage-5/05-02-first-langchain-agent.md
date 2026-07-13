# 第 5.2 课：创建第一个 LangChain Agent

## 1. 本课目标

第 5.1 课已经讲清楚 LangChain 的定位：

```text
Agent = Model + Harness
```

本课开始写第一个真实 LangChain Agent。

但范围要控制住。本课只做：

```text
model + system_prompt + user messages
```

暂时不做：

```text
tools
RAG
FastAPI /chat
结构化 Agent 输出
LangGraph
Deep Agents
```

本课目标是让你学会：

- 如何安装并固定 LangChain 依赖。
- 如何用 `ChatOpenAI` 连接 OpenAI 兼容 provider。
- 如何复用 Stage 4 的 `LLMSettings`。
- 如何用 `create_agent()` 创建一个没有工具的最小 Agent。
- 如何把当前学员档案整理成 LangChain agent input。
- 如何从 `agent.invoke()` 的返回值里取出最后一条回答。
- 如何用 fake agent 做离线测试，避免单元测试访问真实 provider。

完成后，项目会新增：

```text
app/langchain_agent.py
app/langchain_agent_demo.py
tests/test_langchain_agent.py
tests/test_langchain_agent_demo.py
```

## 2. 你会新增什么项目能力

本课新增一个最小 LangChain Agent 入口：

```text
run_learning_agent(student, question)
```

它的职责是：

```text
student + question
-> build_learning_agent_messages()
-> create_learning_agent()
-> agent.invoke(...)
-> extract_agent_text(...)
-> str
```

当前 Agent 的能力很有限：

```text
只能基于输入里的学员资料回答。
不能主动读取 data/student.json。
不能调用 load_student()。
不能查询笔记。
不能写文件。
```

这是有意的。

第 5.2 课只解决“第一个 Agent 能跑起来”。

第 5.3 课才会把 Python 函数注册成 tool，让 Agent 能主动查询学员资料。

## 3. 前置知识

开始前，你应该已经理解：

- Stage 4 的 `LLMSettings` 里有哪些字段。
- `LLM_PROVIDER=deepseek / volcengine_agent_plan / ollama` 如何影响配置。
- `ChatOpenAI` 是 LangChain 的 OpenAI 兼容聊天模型集成。
- `create_agent()` 可以接收模型实例。
- `agent.invoke({"messages": [...]})` 会返回包含 messages 的结果。
- 单元测试不应该访问真实 provider。

你还应该知道当前的边界：

```text
本课不修改 POST /ai/suggestion。
本课不修改 CLI 菜单。
本课只新增手动 demo。
```

## 4. 核心概念

### 为什么安装两个包

本课新增依赖：

```text
langchain==1.3.12
langchain-openai==1.3.4
```

`langchain` 提供：

```text
create_agent
agent harness
```

`langchain-openai` 提供：

```text
ChatOpenAI
```

虽然我们的 provider 可能是 DeepSeek、火山引擎 Ark Agent Plan 或 Ollama，但它们当前都走 OpenAI 兼容接口。

所以本课先用：

```python
from langchain_openai import ChatOpenAI
```

来复用已有的：

```text
base_url
api_key
model
```

### 为什么不用 `model="openai:xxx"` 字符串

官方示例里经常写：

```python
agent = create_agent(model="openai:gpt-5.5", tools=tools)
```

但我们当前项目已经有自己的 provider 配置：

```text
LLM_PROVIDER
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL
DEEPSEEK_MODEL
VOLCENGINE_AGENT_PLAN_API_KEY
OLLAMA_BASE_URL
```

为了继续复用 Stage 4 的配置层，本课选择先显式创建模型实例：

```python
model = ChatOpenAI(
    model=current_settings.model,
    api_key=current_settings.api_key,
    base_url=current_settings.base_url,
    temperature=0.2,
)
```

再传给：

```python
create_agent(model=model, tools=[], middleware=[...])
```

这样好处是：

- 不需要把 provider 配置拆散到 LangChain 专用环境变量里。
- 可以复用 `.env.example` 里的配置。
- 后续切 DeepSeek、火山引擎或 Ollama 仍然走 `LLM_PROVIDER`。

### 为什么本课 `tools=[]`

Agent 最重要的能力之一是 tool calling。

但本课故意不用工具：

```python
tools=[]
```

原因是课程要分层：

| 小节 | 目标 |
| --- | --- |
| 5.2 | 先创建能跑的最小 Agent |
| 5.3 | 把 Python 函数变成 tool |
| 5.4 | 组合多个工具 |
| 5.5 | Agent 结构化输出 |
| 5.6 | FastAPI 接入 Agent |

如果现在就定义工具，你会同时面对：

```text
LangChain 安装
ChatOpenAI 配置
create_agent
tool schema
tool 调用
结果解析
测试隔离
```

这会把学习压力堆在一起。

本课只把最小 Agent 跑通。

### `agent.invoke()` 返回什么

LangChain agent 的返回结果通常包含：

```text
messages
```

最后一条消息一般是 Agent 的最终回答。

本课写一个小函数：

```python
extract_agent_text(agent_result)
```

它支持从两类结构里取文本：

```text
message.content
message.content_blocks
```

这样做是为了让 demo 和测试都更稳：

- 有些对象直接有 `content`。
- 有些示例会打印 `content_blocks`。
- 测试里可以用普通字典模拟返回结果。

### 为什么单元测试用 fake agent

真实 Agent 会访问模型 provider。

单元测试不应该依赖：

- API Key。
- 外网。
- Ollama 是否启动。
- provider 是否稳定。
- 当前模型价格和限流。

所以本课测试：

```text
create_learning_agent() 是否把 model、tools、system_prompt 传对
build_learning_agent_messages() 是否组织了正确输入
extract_agent_text() 是否能解析返回
run_learning_agent() 是否调用 agent.invoke()
```

真实 provider 调用只放到手动 demo：

```powershell
py -3.13 -m app.langchain_agent_demo
```

## 5. 代码实现

### 第一步：更新依赖

打开：

```text
ai-learning-assistant/requirements.txt
```

新增：

```text
langchain==1.3.12
langchain-openai==1.3.4
```

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

如果你只想安装本课新增依赖，也可以运行：

```powershell
py -3.13 -m pip install "langchain==1.3.12" "langchain-openai==1.3.4"
```

本课程当前还没有创建 `.venv`。

所以这些包会安装到你当前 `py -3.13` 对应的 Python 环境中。

### 第二步：新增 `app/langchain_agent.py`

新建：

```text
ai-learning-assistant/app/langchain_agent.py
```

核心导入：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRequest, dynamic_prompt
from langchain_openai import ChatOpenAI
```

同时复用已有配置：

```python
from app.config import LLMSettings, get_llm_settings, require_llm_api_key
from app.llm import build_learning_suggestion_input
```

### 第三步：用 `@dynamic_prompt` 定义 Agent prompt

新增：

```python
LEARNING_AGENT_SYSTEM_PROMPT = (
    "你是一个 Python 和 AI Agent 学习助教。"
    "你会根据学员档案、学习目标和笔记，给出清晰、可执行的学习建议。"
    "当前阶段你还没有工具，只能基于输入里的学员资料回答。"
    "回答必须使用中文。"
)


@dynamic_prompt
def build_learning_agent_system_prompt(_: ModelRequest) -> str:
    return LEARNING_AGENT_SYSTEM_PROMPT
```

注意这里明确写了：

```text
当前阶段你还没有工具
```

这是为了避免学习者误以为这个 Agent 已经能主动查询本地数据。

### 第四步：创建 LangChain Chat 模型

新增：

```python
def build_langchain_chat_model(settings: LLMSettings | None = None) -> ChatOpenAI:
    current_settings = require_llm_api_key(settings or get_llm_settings())

    return ChatOpenAI(
        model=current_settings.model,
        api_key=current_settings.api_key,
        base_url=current_settings.base_url,
        temperature=0.2,
        timeout=30.0,
        max_retries=1,
    )
```

这一步把 Stage 4 的配置层接到 LangChain。

### 第五步：创建最小 Agent

新增：

```python
def create_learning_agent(
    *,
    settings: LLMSettings | None = None,
    model: Any | None = None,
) -> Any:
    current_model = model or build_langchain_chat_model(settings)

    return create_agent(
        model=current_model,
        tools=[],
        middleware=[build_learning_agent_system_prompt],
    )
```

`model` 参数是为了测试。

测试时可以传 fake model，避免创建真实 `ChatOpenAI`。

### 第六步：构造 Agent 输入消息

新增：

```python
def build_learning_agent_messages(
    student: Student,
    question: str = DEFAULT_AGENT_QUESTION,
) -> list[dict[str, str]]:
    content = "\n\n".join(
        [
            build_learning_suggestion_input(student),
            f"用户问题：{question}",
        ]
    )
    return [{"role": "user", "content": content}]
```

这里复用了 Stage 4 的：

```text
build_learning_suggestion_input(student)
```

所以输入内容仍然包括：

- 学员姓名。
- 学习目标。
- Python 水平。
- 最近 5 条笔记。
- 当前问题。

### 第七步：解析 Agent 返回文本

新增：

```python
def extract_agent_text(agent_result: Mapping[str, Any]) -> str:
    ...
```

它会读取最后一条 message 的：

```text
content
content_blocks
```

如果没有消息或内容为空，就抛出：

```python
ValueError
```

### 第八步：封装运行入口

新增：

```python
def run_learning_agent(
    student: Student,
    question: str = DEFAULT_AGENT_QUESTION,
    *,
    settings: LLMSettings | None = None,
    agent: Any | None = None,
) -> str:
    current_agent = agent or create_learning_agent(settings=settings)
    result = current_agent.invoke({"messages": build_learning_agent_messages(student, question)})
    return extract_agent_text(result)
```

这是本课最重要的业务入口。

但它现在只供 demo 和后续课程使用。

还不接 CLI 菜单，也不接 FastAPI。

### 第九步：新增手动 demo

新建：

```text
ai-learning-assistant/app/langchain_agent_demo.py
```

写入：

```python
from app.langchain_agent import DEFAULT_AGENT_QUESTION, run_learning_agent
from app.storage import load_student


def main() -> None:
    student = load_student()
    answer = run_learning_agent(student, DEFAULT_AGENT_QUESTION)
    print(answer)


if __name__ == "__main__":
    main()
```

运行：

```powershell
py -3.13 -m app.langchain_agent_demo
```

这条命令需要真实 provider 配置。

如果你使用云端 provider，需要 `.env` 里有 API Key。

如果你使用 Ollama，需要本地 Ollama 已启动，并且模型已经可用。

### 第十步：新增离线测试

新增：

```text
tests/test_langchain_agent.py
tests/test_langchain_agent_demo.py
```

测试重点：

- `ChatOpenAI` 使用 `LLMSettings` 里的 model、base URL、API Key。
- 缺少 API Key 时仍然会失败。
- `create_learning_agent()` 传入 `tools=[]` 和注解式 prompt middleware。
- Agent 输入消息包含学员档案和用户问题。
- `extract_agent_text()` 能解析 `content` 和 `content_blocks`。
- `run_learning_agent()` 会调用 fake agent 的 `invoke()`。
- demo 会读取 student 并打印回答。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行测试：

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

如果 provider 没配置，这条 demo 会失败。

这是正常的。

自动化测试不依赖真实 provider。

## 7. 常见错误

### 把本课 Agent 当成工具型 Agent

本课 Agent 还没有工具：

```python
tools=[]
```

它不会主动调用 `load_student()`。

学员资料是你提前塞进 message 的。

### 忘记安装 `langchain-openai`

只有 `langchain` 不够。

本课使用：

```python
from langchain_openai import ChatOpenAI
```

所以必须安装：

```text
langchain-openai
```

### 把 API Key 写进代码

不要把密钥写进：

```text
app/langchain_agent.py
```

继续通过 `.env` 和 `LLMSettings` 读取。

### 让测试访问真实模型

不要在单元测试里调用真实 provider。

用 fake agent 或 monkeypatch 测边界。

真实模型调用放在：

```powershell
py -3.13 -m app.langchain_agent_demo
```

### 直接把 Agent 接进 FastAPI

本课不做 `POST /chat`。

因为此时 Agent 还没有工具，也没有明确 API 错误边界。

API 接入留到第 5.6 课。

### 以为 `langchain` 不会带入 `langgraph`

当前安装 `langchain==1.3.12` 时会安装 `langgraph` 相关依赖。

这不代表我们已经开始学习 LangGraph。

在本课程里，LangGraph 的正式使用从 Stage 7 开始。

## 8. 练习

练习 1：解释为什么本课使用 `ChatOpenAI`，而不是继续手写 `httpx.post()`。

练习 2：解释为什么本课使用模型实例：

```python
create_agent(model=current_model, tools=[], ...)
```

而不是直接使用：

```python
create_agent(model="openai:xxx", ...)
```

练习 3：把 `DEFAULT_AGENT_QUESTION` 改成另一个问题，运行 demo 观察回答变化。

练习 4：解释为什么本课不把 `load_student()` 注册成 tool。

练习 5：阅读 `tests/test_langchain_agent.py`，说明 fake agent 测试了什么。

练习 6：用自己的话解释：

```text
Agent 现在不是“自己会查资料”，而是“基于你传进去的 messages 回答”。
```

## 9. 验收标准

完成本课后，你应该能做到：

- 解释 `langchain` 和 `langchain-openai` 的分工。
- 看懂 `build_langchain_chat_model()`。
- 看懂 `create_learning_agent()`。
- 解释 `@dynamic_prompt` 如何把 prompt 注入模型调用。
- 解释为什么本课 `tools=[]`。
- 看懂 `build_learning_agent_messages()` 如何复用 Stage 4 输入构造。
- 看懂 `extract_agent_text()` 为什么要处理 `content` 和 `content_blocks`。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。
- 在 provider 可用时，能手动运行 `py -3.13 -m app.langchain_agent_demo`。
- 知道第 5.3 课才开始把 Python 函数变成工具。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课把 Stage 5 从概念推进到真实代码：

| 本课内容 | 后续升级 |
| --- | --- |
| `ChatOpenAI` | 后续继续复用 provider 配置 |
| `create_agent(..., tools=[], middleware=[...])` | 5.3 改为带工具的 Agent |
| `build_learning_agent_messages()` | 后续对话 API 和记忆输入基础 |
| `extract_agent_text()` | 5.5 结构化 Agent 输出前的文本基线 |
| `app/langchain_agent.py` | Stage 5 的 Agent 主模块 |
| fake agent 测试 | 后续工具调用、RAG、Graph 测试策略 |

LangGraph 还没开始。

但你现在已经能看到一个重要事实：

```text
LangChain agent 本身就返回一个消息状态。
```

这会为后续 LangGraph 的 `State`、`messages`、node 和 edge 打基础。

Deep Agents 也还没开始。

但 Deep Agents 之后会建立在更强的 Agent harness 上。

所以现在先把最小 Agent 跑通，是必要步骤。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-5/05-02-first-langchain-agent.md`
- `ai-learning-assistant/app/langchain_agent.py`
- `ai-learning-assistant/app/langchain_agent_demo.py`
- `ai-learning-assistant/tests/test_langchain_agent.py`
- `ai-learning-assistant/tests/test_langchain_agent_demo.py`

修改文件：

- `README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/requirements.txt`
- `docs/tutorial/README.md`

代码变更：

- 新增 `build_langchain_chat_model()`。
- 新增 `create_learning_agent()`。
- 新增 `build_learning_agent_messages()`。
- 新增 `extract_agent_text()`。
- 新增 `run_learning_agent()`。
- 新增 LangChain Agent 手动 demo。
- 新增 LangChain Agent 离线测试。

新增依赖：

- `langchain==1.3.12`
- `langchain-openai==1.3.4`

环境变量变更：

- 无。继续复用第 4.2 课的 provider 配置。

官方文档核对：

- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [ChatOpenAI integration](https://docs.langchain.com/oss/python/integrations/chat/openai)

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install "langchain==1.3.12" "langchain-openai==1.3.4" --disable-pip-version-check --progress-bar off --no-input
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py
```

下一步：

- 第 5.3 课：Python 函数变工具。
- 把 `load_student()` 或只读查询函数注册为 LangChain tool。
- 让 Agent 不只是“读输入”，而是能主动调用工具查询学员资料。
