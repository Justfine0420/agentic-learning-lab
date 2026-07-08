# 第 4.3 课：第一次模型调用

## 1. 本课目标

第 4.2 课已经把模型服务配置抽到了 `app/config.py`。

本课开始新增真正的模型调用入口：

```text
ai-learning-assistant/app/llm.py
ai-learning-assistant/app/llm_demo.py
```

你要学会：

- 为什么模型调用要封装到单独模块。
- OpenAI 兼容 `chat/completions` 请求大概长什么样。
- 如何把学员资料整理成模型输入。
- 如何把模型响应解析成普通字符串。
- 如何从命令行跑一次真实模型调用。
- 如何用 fake client 测试模型调用代码，而不是每次测试都访问真实模型。
- 为什么本课还不把现有 `GET /suggestion` 强行改成 AI 调用。

本课会新增真实调用代码，但自动测试不会访问外网，也不会要求真实 API Key。

## 2. 你会新增什么项目能力

本课新增：

```text
app/llm.py
app/llm_demo.py
tests/test_llm.py
tests/test_llm_demo.py
```

新增能力：

```text
Student
-> build_learning_suggestion_messages(...)
-> call_chat_completion(...)
-> AI 生成学习建议文本
```

当前项目会具备一个最小 LLM 调用链路：

```text
python -m app.llm_demo
-> load_student()
-> generate_learning_suggestion(student)
get_llm_settings()
-> require_llm_api_key()
-> POST {base_url}/chat/completions
-> parse choices[0].message.content
```

但注意：

```text
GET /suggestion 仍然返回规则建议。
```

原因很直接：学习者不一定已经有火山、DeepSeek 或 Ollama 可用环境。
如果现在把 `/suggestion` 改成强依赖模型，Stage 3 已经稳定的 API 会因为没有 API Key 或本地模型没启动而失败。

所以本课先完成 `llm.py`。
并提供 `llm_demo.py` 作为手动真实调用入口。
后续再决定何时把它接入 API。

## 3. 前置知识

开始前，你应该已经理解：

- `Student` 是一个 `TypedDict`。
- `config.py` 可以读取 `LLM_PROVIDER`、`base_url`、`model` 和 `api_key`。
- `httpx` 可以发送 HTTP 请求。
- pytest 可以用 fake object 测试代码。
- LLM 响应不是普通函数返回值，需要解析。

本课会使用 OpenAI 兼容接口格式。

火山 Ark Agent Plan、DeepSeek、Ollama 都可以走类似的兼容路径：

- 火山 Ark Agent Plan 官方文档说明 OpenAI 兼容 Base URL 是 `https://ark.cn-beijing.volces.com/api/plan/v3`。
- DeepSeek 官方文档说明 OpenAI 兼容 `base_url` 是 `https://api.deepseek.com`。
- Ollama 官方 OpenAI compatibility 示例使用 `http://localhost:11434/v1/` 和 `api_key='ollama'`。

## 4. 核心概念

### 为什么要有 `llm.py`

不要把模型调用直接写进 `api.py`。

`api.py` 应该负责：

```text
接收请求
读取或保存数据
调用业务函数
返回响应
```

`llm.py` 应该负责：

```text
组织 messages
调用模型服务
处理模型响应
抛出明确错误
```

这样后面进入 LangChain 时，替换调用层会更轻。

当前方向是：

```text
api.py
-> llm.py
-> provider OpenAI-compatible API
```

后面会升级成：

```text
api.py
-> langchain_agent.py
-> tools + model
```

### `chat/completions` 是什么

很多模型服务都支持 OpenAI 兼容的 chat completions 格式。

一次请求通常包含：

```json
{
  "model": "模型名",
  "messages": [
    {"role": "system", "content": "高层规则"},
    {"role": "user", "content": "本次任务"}
  ],
  "temperature": 0.2
}
```

返回值里通常会有：

```text
choices[0].message.content
```

本课就解析这个字段。

注意，4.4 才会做结构化输出。
所以 4.3 只返回普通文本建议。

### system message 和 user message

本项目把稳定规则放到 system message：

```text
你是一个 Python 和 AI Agent 学习助教。
回答必须使用中文，最多 3 条建议。
```

把本次学员上下文放到 user message：

```text
学员姓名
学习目标
Python 水平
最近学习笔记
请生成今天的学习建议
```

这样职责更清楚：

| message | 放什么 |
| --- | --- |
| system | 助教身份、回答风格、长期规则 |
| user | 当前学员资料、本次任务 |

### 为什么测试不用真实模型

真实模型调用有几个问题：

- 需要 API Key。
- 可能产生费用。
- 网络可能失败。
- 模型输出不完全稳定。
- 本地 Ollama 不一定启动。

如果单元测试依赖这些条件，课程会很脆。

所以本课用 fake client。

fake client 会假装自己是 `httpx.Client`，记录请求，并返回固定响应：

```python
{"choices": [{"message": {"content": "建议：复习 FastAPI。"}}]}
```

这样我们能验证：

- URL 拼接对不对。
- Authorization header 对不对。
- JSON payload 对不对。
- 响应解析对不对。

不用真的访问模型。

## 5. 代码实现

### 第一步：新增 `app/llm.py`

新增文件：

```text
ai-learning-assistant/app/llm.py
```

它先定义系统提示：

```python
SYSTEM_INSTRUCTIONS = (
    "你是一个 Python 和 AI Agent 学习助教。"
    "你会根据学员目标、Python 水平和最近笔记，给出简短、可执行的今日学习建议。"
    "回答必须使用中文，最多 3 条建议。"
)
```

这段文字会放进 system message。

### 第二步：拼接 chat completions URL

新增函数：

```python
def build_chat_completions_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"
```

如果 provider 的 `base_url` 是：

```text
http://localhost:11434/v1/
```

最终 URL 会变成：

```text
http://localhost:11434/v1/chat/completions
```

### 第三步：把 Student 变成模型输入

新增函数：

```python
def build_learning_suggestion_input(student: Student) -> str:
    ...
```

它会把当前学员数据整理成文本：

```text
学员姓名：Alice
学习目标：学习 LangChain
Python 水平：basic
最近学习笔记：
1. FastAPI route 是普通函数加装饰器
2. Pydantic 可以校验请求体
请生成今天的学习建议。
```

注意，只放最近 5 条笔记。

这是为后面的 RAG 和 token 控制做铺垫：

```text
不要把所有历史内容无脑塞给模型。
```

### 第四步：构造 messages

新增函数：

```python
def build_learning_suggestion_messages(student: Student) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": build_learning_suggestion_input(student)},
    ]
```

这就是最小对话输入。

### 第五步：解析模型响应

新增函数：

```python
def parse_chat_completion_text(response_data: dict[str, Any]) -> str:
    ...
```

它读取：

```text
choices[0].message.content
```

如果响应里没有这个字段，抛出：

```text
ValueError
```

不要在这里悄悄返回空字符串。
错误越早暴露，后面越好排查。

### 第六步：调用模型

核心函数：

```python
def call_chat_completion(
    messages: list[dict[str, str]],
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
    timeout: float = 30.0,
) -> str:
    ...
```

它会：

1. 读取或接收 `LLMSettings`。
2. 检查云端 provider 是否有 API Key。
3. 拼接 URL。
4. 发送 `POST` 请求。
5. 解析响应文本。

`client` 参数是为了测试。
测试时传入 fake client。
真实运行时不传，它会创建 `httpx.Client`。

### 第七步：生成学习建议

最终对外函数：

```python
def generate_learning_suggestion(
    student: Student,
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
) -> str:
    messages = build_learning_suggestion_messages(student)
    return call_chat_completion(messages, settings=settings, client=client)
```

后面 API 或 LangChain 阶段会复用这个入口。

### 第八步：新增手动调用入口

新增文件：

```text
ai-learning-assistant/app/llm_demo.py
```

它只做三件事：

```python
from app.llm import generate_learning_suggestion
from app.storage import load_student


def main() -> None:
    student = load_student()
    suggestion = generate_learning_suggestion(student)
    print(suggestion)


if __name__ == "__main__":
    main()
```

这个入口会读取当前 `data/student.json`，然后调用本课新增的 LLM 封装。

注意，它不是新的业务逻辑层。
它只是为了让第 4.3 课能用一条固定命令完成第一次真实模型调用。

### 第九步：新增测试

新增：

```text
ai-learning-assistant/tests/test_llm.py
ai-learning-assistant/tests/test_llm_demo.py
```

测试覆盖：

- URL 拼接。
- 学员上下文格式化。
- 最近 5 条笔记限制。
- system/user message 结构。
- 模型响应解析。
- 缺失响应内容时报错。
- OpenAI 兼容请求体。
- `generate_learning_suggestion()` 会携带学员上下文。
- `llm_demo.main()` 会加载学员资料、调用 LLM 封装并打印结果。

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
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py
```

手动跑第一次真实模型调用：

```powershell
py -3.13 -m app.llm_demo
```

这条命令必须在 `ai-learning-assistant/` 目录下运行。

如果你在仓库外层目录运行：

```powershell
python -m app.llm_demo
```

会看到：

```text
ModuleNotFoundError: No module named 'app'
```

原因是 `app/` 包在 `ai-learning-assistant/` 目录里，不在仓库根目录里。

如果你已经启动 Ollama，并且本地有 `.env`：

```text
LLM_PROVIDER=ollama
OLLAMA_MODEL=你的本地模型名
```

如果你使用火山或 DeepSeek，需要先在 `.env` 填好真实 API Key。

本课自动验收不要求跑这条真实调用命令。
但课程目标是“第一次模型调用”，所以手动验收时应该至少跑通一次 `py -3.13 -m app.llm_demo`。

## 7. 常见错误

### 把测试写成必须访问真实模型

不要这样做。

单元测试要稳定。
真实模型调用适合手动验收或后续集成测试。

### 忘记处理 base URL 末尾斜杠

如果 `base_url` 是：

```text
http://localhost:11434/v1/
```

直接拼接可能得到：

```text
http://localhost:11434/v1//chat/completions
```

所以代码使用：

```python
base_url.rstrip("/")
```

### 解析响应时假设永远有 content

模型服务可能返回错误格式，也可能因为 provider 差异导致字段不符合预期。

本课用 `ValueError` 明确暴露：

```text
LLM response did not contain message content.
```

### 一次性把所有笔记都塞给模型

现在只取最近 5 条笔记。

这不是为了偷懒，而是为了让你从现在开始意识到：

```text
模型上下文是有限的。
```

后续 RAG 会更系统地解决“给模型哪些资料”的问题。

### 现在就替换 `/suggestion`

不要急。

`GET /suggestion` 是已经稳定的规则接口。
本课只新增 LLM 能力，不破坏已有 API。

后面接入 API 时，可以做成：

```text
GET /suggestion      -> 规则建议
POST /ai/suggestion  -> AI 建议
```

或者再设计一个降级策略。

### 在仓库根目录运行 demo

如果你当前目录是：

```powershell
E:\Code\agentic-learning-lab
```

下面这条命令会失败：

```powershell
python -m app.llm_demo
```

正确方式是先进入真实项目目录：

```powershell
cd ai-learning-assistant
py -3.13 -m app.llm_demo
```

## 8. 练习

练习 1：解释为什么 `llm.py` 不应该写在 `api.py` 里。

练习 2：阅读 `build_learning_suggestion_input()`，回答它为什么只取最近 5 条笔记。

练习 3：把 fake client 返回内容改成：

```text
建议：今天写一个 FastAPI 小接口。
```

观察测试是否仍然通过。

练习 4：手动构造一个缺少 `choices` 的响应，确认 `parse_chat_completion_text()` 会抛出 `ValueError`。

练习 5：如果你本机有 Ollama，启动服务后用 `LLM_PROVIDER=ollama` 试一次真实调用。

练习 6：在 `data/student.json` 里保留一条学习笔记，再运行 `py -3.13 -m app.llm_demo`，观察模型建议是否使用了这条笔记。

## 9. 验收标准

完成本课后，你应该能做到：

- 解释为什么模型调用要封装到 `llm.py`。
- 解释 `chat/completions` 请求体里的 `model`、`messages` 和 `temperature`。
- 解释 system message 和 user message 的区别。
- 解释为什么单元测试使用 fake client。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。
- 在 provider 配置可用时，能运行 `py -3.13 -m app.llm_demo` 打印一段 AI 学习建议。
- 知道当前 `GET /suggestion` 还没有接入 AI。
- 能说明真实模型调用需要 `.env` 和 provider 环境准备。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课是进入 LangChain 前的最后一层手写模型调用基础。

| 本课内容 | 后续升级 |
| --- | --- |
| `build_learning_suggestion_messages()` | LangChain prompt / messages |
| `call_chat_completion()` | LangChain chat model 调用 |
| `generate_learning_suggestion()` | Agent 工具或业务入口 |
| fake client 测试 | 后续 mock model / graph node 测试 |
| 最近 5 条笔记 | RAG 检索和上下文控制 |

LangChain 会帮你封装更多模型调用细节。
但如果你没亲手写过一次 `chat/completions`，后面看到 LangChain 的 `model`、`messages`、tool call 和 structured output 时会缺少底层直觉。

LangGraph 会把模型调用放进 node。
这个 node 里最终仍然需要一个类似 `generate_learning_suggestion()` 的函数。

Deep Agents 会做更长任务。
长任务更依赖清晰的模型调用边界、错误处理和上下文控制。

## 11. 本课变更清单

新增文件：

- `ai-learning-assistant/app/llm.py`
- `ai-learning-assistant/app/llm_demo.py`
- `ai-learning-assistant/tests/test_llm.py`
- `ai-learning-assistant/tests/test_llm_demo.py`
- `docs/tutorial/lessons/stage-4/04-03-first-llm-call.md`

修改文件：

- `README.md`
- `ai-learning-assistant/README.md`
- `docs/tutorial/README.md`

代码变更：

- 新增 `SYSTEM_INSTRUCTIONS`。
- 新增 `build_chat_completions_url()`。
- 新增 `build_learning_suggestion_input()`。
- 新增 `build_learning_suggestion_messages()`。
- 新增 `parse_chat_completion_text()`。
- 新增 `call_chat_completion()`。
- 新增 `generate_learning_suggestion()`。
- 新增 `llm_demo.main()`，用于从命令行读取学员资料并发起一次真实模型调用。

新增依赖：

- 无。继续复用 `httpx` 和 `python-dotenv`。

环境变量变更：

- 无。继续复用第 4.2 课的 provider 配置。

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py
py -3.13 -m app.llm_demo
```

下一步：

- 第 4.4 课：结构化输出，让 AI 返回更稳定、可解析的学习建议。
