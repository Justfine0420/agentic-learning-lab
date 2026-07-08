# Stage 4 补充学习资料：LLM 调用、结构化输出与 AI 建议入口

本文记录 Stage 4 中围绕 LLM Provider 配置、第一次模型调用、结构化输出、CLI / API 接入补充出来的知识点。

- `LLM_PROVIDER`、`.env`、API Key 和 provider 配置层是什么
- `@dataclass(frozen=True)` 为什么适合保存配置
- 为什么不应该在 `api.py` 里直接读取 `DEEPSEEK_API_KEY`
- `python -m app.llm_demo` 和 `python app.llm_demo` 的区别
- OpenAI 兼容 `chat/completions` 请求长什么样
- `system` message、`user` message、prompt、input 和 token 怎么理解
- `httpx.Client.post()`、`response.raise_for_status()` 和 `response.json()` 的作用
- 为什么测试 LLM 调用时使用 fake client
- Pydantic 结构化输出模型、`Field(ge=5, le=180)`、`model_json_schema()` 和 `model_validate_json()`
- `POST /ai/suggestion` 为什么单独提供 AI 建议入口
- 当前 Stage 4 的完整调用链路

## 目录

- [1. Stage 4 在项目中新增了什么](#1-stage-4-在项目中新增了什么)
- [2. LLM 调用解决的是什么问题](#2-llm-调用解决的是什么问题)
- [3. `.env` 和 `.env.example` 的区别](#3-env-和-envexample-的区别)
- [4. `PROJECT_ROOT` 和 `ENV_FILE` 是什么](#4-project_root-和-env_file-是什么)
- [5. `@dataclass(frozen=True)` 的作用](#5-dataclassfrozentrue-的作用)
- [6. Provider 配置层是什么](#6-provider-配置层是什么)
- [7. 为什么不在 `api.py` 里直接读取 API Key](#7-为什么不在-apipy-里直接读取-api-key)
- [8. `python -m app.llm_demo` 为什么要加 `-m`](#8-python--m-appllm_demo-为什么要加--m)
- [9. OpenAI 兼容 `chat/completions` 是什么](#9-openai-兼容-chatcompletions-是什么)
- [10. `messages`、`system` 和 `user` 怎么分工](#10-messagessystem-和-user-怎么分工)
- [11. 为什么只取最近 5 条笔记](#11-为什么只取最近-5-条笔记)
- [12. `httpx.Client` 怎么发送模型请求](#12-httpxclient-怎么发送模型请求)
- [13. `raise_for_status()` 的作用](#13-raise_for_status-的作用)
- [14. `parse_chat_completion_text()` 为什么要单独写](#14-parse_chat_completion_text-为什么要单独写)
- [15. fake client 为什么适合测试 LLM 调用](#15-fake-client-为什么适合测试-llm-调用)
- [16. 结构化输出是什么](#16-结构化输出是什么)
- [17. `Field()`、`min_length`、`ge`、`le` 的含义](#17-fieldmin_lengthgele-的含义)
- [18. `model_json_schema()` 是哪里来的](#18-model_json_schema-是哪里来的)
- [19. `json.dumps(..., ensure_ascii=False, indent=2)` 的作用](#19-jsondumps-ensure_asciifalse-indent2-的作用)
- [20. `model_validate_json()` 做了什么](#20-model_validate_json-做了什么)
- [21. `response_format={"type": "json_object"}` 是什么](#21-response_formattype-json_object-是什么)
- [22. `structured_llm_demo.py` 和 `llm_demo.py` 的区别](#22-structured_llm_demopy-和-llm_demopy-的区别)
- [23. `/suggestion` 和 `/ai/suggestion` 为什么分开](#23-suggestion-和-aisuggestion-为什么分开)
- [24. CLI 中为什么保留离线规则建议](#24-cli-中为什么保留离线规则建议)
- [25. 当前项目中的 Stage 4 数据流](#25-当前项目中的-stage-4-数据流)
- [26. 常见错误与排查](#26-常见错误与排查)

## 1. Stage 4 在项目中新增了什么

Stage 3 已经完成 FastAPI 学习助手 API。

Stage 4 开始让项目具备真实模型调用能力。

当前新增或重点升级的文件包括：

```text
app/config.py                 LLM provider 配置读取
app/llm.py                    LLM 调用封装
app/llm_demo.py               第一次普通文本模型调用入口
app/structured_llm_demo.py    结构化模型调用入口
app/models.py                 结构化学习建议模型
app/api.py                    新增 POST /ai/suggestion
app/cli.py                    新增 AI 学习建议菜单
tests/test_config.py          配置读取测试
tests/test_llm.py             LLM 调用测试
tests/test_llm_demo.py        普通 demo 测试
tests/test_structured_llm_demo.py 结构化 demo 测试
```

Stage 4 的核心能力可以概括成：

```text
学员资料
-> 组织成 messages
-> 调用 OpenAI 兼容模型接口
-> 解析模型返回
-> 用 Pydantic 校验结构化结果
-> 提供 CLI 和 API 入口
```

## 2. LLM 调用解决的是什么问题

Stage 3 的学习建议来自规则函数：

```python
build_suggestion(student["python_level"])
```

规则建议稳定、离线可用，但能力有限。

Stage 4 增加 LLM 调用后，学习建议可以参考：

```text
学员姓名
学习目标
Python 水平
最近学习笔记
```

然后由模型生成更贴近当前上下文的建议。

但是模型调用也会带来新问题：

```text
需要 API Key
可能网络失败
可能产生费用
模型输出不一定稳定
返回内容需要解析和校验
```

所以 Stage 4 没有直接替换所有旧逻辑，而是分层接入。

## 3. `.env` 和 `.env.example` 的区别

项目中有：

```text
.env.example
```

它是配置模板，可以提交到 Git。

真实使用时复制成：

```text
.env
```

然后填写真实 API Key。

`.env` 不应该提交，因为它可能包含密钥：

```text
DEEPSEEK_API_KEY=真实密钥
VOLCENGINE_AGENT_PLAN_API_KEY=真实密钥
```

`.env.example` 只保留变量名和示例默认值：

```text
LLM_PROVIDER=volcengine_agent_plan

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

OLLAMA_API_KEY=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
```

这样别人能知道要配置哪些变量，但不会拿到你的密钥。

## 4. `PROJECT_ROOT` 和 `ENV_FILE` 是什么

当前代码：

```python
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
```

假设文件位置是：

```text
ai-learning-assistant/app/config.py
```

那么：

```python
Path(__file__).resolve()
```

表示当前文件的绝对路径。

```python
.parents[0]
```

是：

```text
ai-learning-assistant/app
```

```python
.parents[1]
```

是：

```text
ai-learning-assistant
```

所以 `PROJECT_ROOT` 就是项目根目录。

```python
ENV_FILE = PROJECT_ROOT / ".env"
```

表示：

```text
ai-learning-assistant/.env
```

这里的 `/` 不是除法，而是 `pathlib.Path` 的路径拼接。

## 5. `@dataclass(frozen=True)` 的作用

当前配置对象使用：

```python
@dataclass(frozen=True)
class LLMProviderConfig:
    api_key_env: str
    base_url_env: str
    model_env: str
    default_base_url: str
    default_model: str
    default_api_key: str = ""
    requires_api_key: bool = True
```

`@dataclass` 会自动生成初始化方法。

`frozen=True` 表示对象创建后不允许修改字段。

配置对象适合只读。
这能避免程序运行中意外改掉 provider 配置。

## 6. Provider 配置层是什么

当前项目支持多个 provider：

```python
LLM_PROVIDERS = {
    "volcengine_agent_plan": ...,
    "volcengine_coding": ...,
    "deepseek": ...,
    "ollama": ...,
}
```

每个 provider 都需要知道：

```text
从哪个环境变量读取 API Key
从哪个环境变量读取 base URL
从哪个环境变量读取 model
默认 base URL 是什么
默认 model 是什么
是否必须要求 API Key
```

`get_llm_settings()` 会根据 `LLM_PROVIDER` 选择当前 provider，然后返回统一的 `LLMSettings`。

后续 `llm.py` 不需要关心当前到底是 DeepSeek、火山还是 Ollama。

它只使用：

```python
current_settings.api_key
current_settings.base_url
current_settings.model
```

这就是配置层的价值：

```text
调用层只关心统一配置
配置层负责 provider 差异
```

## 7. 为什么不在 `api.py` 里直接读取 API Key

不推荐这样写：

```python
# app/api.py
import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
```

原因有几个。

第一，职责混乱。

`api.py` 应该负责：

```text
接收 HTTP 请求
调用业务函数
返回 HTTP 响应
```

配置读取应该属于 `config.py`。

第二，测试麻烦。

如果每个模块都自己读环境变量，测试时就必须到处 patch 环境。

第三，导入时机容易出错。

模块顶层代码只在第一次 import 时执行。
如果 `.env` 还没加载就读取环境变量，后面再加载 `.env` 也不会自动更新那个顶层变量。

一句话总结：

```text
api.py 负责 HTTP 边界
config.py 负责配置来源
llm.py 负责模型调用
```

## 8. `python -m app.llm_demo` 为什么要加 `-m`

正确命令：

```powershell
py -3.13 -m app.llm_demo
```

含义是：

```text
把 app.llm_demo 当成 Python 模块运行
```

对应文件是：

```text
app/llm_demo.py
```

错误命令：

```powershell
python app.llm_demo
```

这会让 Python 去找一个叫 `app.llm_demo` 的文件，而不是模块。

所以会报：

```text
can't open file '...\app.llm_demo'
```

在 IDE 里配置断点调试时，推荐使用：

```text
Module name: app.llm_demo
Working directory: ai-learning-assistant
```

如果 IDE 只能填脚本路径，则填：

```text
Script path: ai-learning-assistant/app/llm_demo.py
Working directory: ai-learning-assistant
```

工作目录很重要。

因为当前代码里有：

```python
DATA_FILE = Path("data/student.json")
```

它会从当前工作目录下找 `data/student.json`。

## 9. OpenAI 兼容 `chat/completions` 是什么

很多模型服务支持类似 OpenAI 的接口格式。

当前项目统一调用：

```text
{base_url}/chat/completions
```

代码：

```python
def build_chat_completions_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"
```

`rstrip("/")` 是为了避免双斜杠。

请求体大致是：

```json
{
  "model": "qwen3:8b",
  "messages": [
    {"role": "system", "content": "你是一个学习助教。"},
    {"role": "user", "content": "请根据学员资料生成建议。"}
  ],
  "temperature": 0.2
}
```

返回值通常包含：

```text
choices[0].message.content
```

当前项目就从这里取模型文本。

## 10. `messages`、`system` 和 `user` 怎么分工

当前代码：

```python
def build_learning_suggestion_messages(student: Student) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": build_learning_suggestion_input(student)},
    ]
```

`system` 放稳定规则：

```text
你是谁
回答风格
必须使用中文
最多 3 条建议
```

`user` 放本次任务：

```text
学员姓名
学习目标
Python 水平
最近学习笔记
请生成今天的学习建议
```

这样拆分以后，后续迁移到 LangChain messages 或 Agent prompt 时更自然。

## 11. 为什么只取最近 5 条笔记

当前代码：

```python
note_lines = "\n".join(f"{index}. {note}" for index, note in enumerate(notes[-5:], start=1))
```

`notes[-5:]` 表示取最后 5 条。

原因是模型上下文不是无限的。

如果把所有历史笔记都塞进去，会带来几个问题：

```text
请求变长
成本变高
响应变慢
模型注意力分散
可能超过上下文窗口
```

当前阶段先用“最近 5 条”作为简单策略。

后续 RAG 阶段会学习更系统的资料筛选方式。

## 12. `httpx.Client` 怎么发送模型请求

当前核心代码：

```python
with httpx.Client(timeout=timeout) as default_client:
    response = default_client.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return parse_chat_completion_text(response.json())
```

`httpx.Client` 是 HTTP 客户端。

`post()` 会发送 POST 请求。

这里传了三个关键参数：

```python
url
headers
json=payload
```

`headers` 包含：

```python
{
    "Authorization": f"Bearer {current_settings.api_key}",
    "Content-Type": "application/json",
}
```

`json=payload` 表示把 Python 字典自动序列化成 JSON 请求体。

`timeout=30.0` 表示最多等 30 秒。

## 13. `raise_for_status()` 的作用

`raise_for_status()` 是 `httpx.Response` 的方法。

它用来检查 HTTP 状态码。

如果响应是 `200 OK`，它什么都不做，代码继续往下执行。

如果响应是 `401 Unauthorized`、`404 Not Found` 或 `500 Internal Server Error`，它会抛出：

```text
httpx.HTTPStatusError
```

这很重要。

没有这一步，代码可能会把错误响应当成正常模型响应去解析，最后报：

```text
LLM response did not contain message content.
```

但真正原因可能是：

```text
API Key 无效
provider URL 写错
模型服务不可用
```

所以顺序应该是：

```text
先确认 HTTP 成功
再解析模型内容
```

## 14. `parse_chat_completion_text()` 为什么要单独写

当前解析函数：

```python
def parse_chat_completion_text(response_data: dict[str, Any]) -> str:
    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("LLM response did not contain message content.") from error

    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM response message content is empty.")

    return content.strip()
```

它单独存在有两个好处。

第一，模型调用和响应解析分开。

第二，测试更简单。

测试可以直接传入：

```python
{"choices": [{"message": {"content": "今天复习 Pydantic。"}}]}
```

不用真的访问网络。

## 15. fake client 为什么适合测试 LLM 调用

真实模型调用不适合作为单元测试依赖。

原因：

```text
需要 API Key
可能产生费用
网络可能失败
模型输出不稳定
本地 Ollama 不一定启动
```

所以测试里使用 fake client。

fake client 做两件事：

```text
记录请求内容
返回固定响应
```

这样可以验证：

```text
URL 是否正确
Authorization header 是否正确
model 是否正确
messages 是否正确
response_format 是否正确
解析逻辑是否正确
```

## 16. 结构化输出是什么

普通 LLM 输出是文本：

```text
建议：今天复习 FastAPI。
```

这种文本适合人读，但不适合程序继续处理。

结构化输出要求模型返回 JSON：

```json
{
  "summary": "今天重点补齐 FastAPI 到 LangChain 的连接。",
  "suggestions": [
    {
      "title": "复习 FastAPI route",
      "description": "重新阅读 /profile 和 /suggestion 的实现。",
      "estimated_minutes": 25
    }
  ],
  "next_checkpoint": "能解释 API 如何调用模型层。"
}
```

程序可以把它校验成：

```python
StructuredLearningSuggestion
```

然后 API 和 CLI 都能稳定读取字段。

## 17. `Field()`、`min_length`、`ge`、`le` 的含义

当前模型：

```python
class LearningSuggestionItem(BaseModel):
    title: str = Field(min_length=1, description="学习建议标题")
    description: str = Field(min_length=1, description="具体要做什么")
    estimated_minutes: int = Field(ge=5, le=180, description="预计学习分钟数")
```

`Field()` 用来给字段增加校验规则和说明。

```python
min_length=1
```

表示字符串不能为空。

```python
ge=5
```

表示 greater than or equal，大于等于 5。

```python
le=180
```

表示 less than or equal，小于等于 180。

所以 `estimated_minutes=20` 合法，`estimated_minutes=3` 和 `estimated_minutes=200` 都不合法。

这里的业务含义是：

```text
一条学习建议预计时间应该在 5 到 180 分钟之间。
```

## 18. `model_json_schema()` 是哪里来的

当前代码：

```python
schema = json.dumps(
    StructuredLearningSuggestion.model_json_schema(),
    ensure_ascii=False,
    indent=2,
)
```

`model_json_schema()` 不是项目自己定义的方法。

它来自：

```python
class StructuredLearningSuggestion(BaseModel):
```

也就是 Pydantic 的 `BaseModel`。

只要继承了 `BaseModel`，模型类就拥有 `model_json_schema()`。

它会根据字段类型和 `Field()` 规则生成 JSON Schema。

例如会描述：

```text
summary 是字符串
suggestions 是数组
suggestions 至少 1 条、最多 3 条
estimated_minutes 是整数，范围 5 到 180
next_checkpoint 是字符串
```

这份 schema 会被放进 prompt，告诉模型应该返回什么结构。

## 19. `json.dumps(..., ensure_ascii=False, indent=2)` 的作用

`model_json_schema()` 返回的是 Python 字典。

prompt 需要的是文本。

所以要用：

```python
json.dumps(...)
```

把字典变成 JSON 字符串。

```python
ensure_ascii=False
```

表示中文不要变成 `\u4eca\u65e5\u5b66\u4e60`，而是保留中文。

```python
indent=2
```

表示缩进 2 个空格，方便阅读。

最终这段 schema 会拼进 user message。

## 20. `model_validate_json()` 做了什么

当前代码：

```python
def parse_structured_learning_suggestion(content: str) -> StructuredLearningSuggestion:
    try:
        return StructuredLearningSuggestion.model_validate_json(content)
    except ValueError as error:
        raise ValueError("LLM response was not a valid structured learning suggestion.") from error
```

`model_validate_json()` 也是 Pydantic `BaseModel` 提供的方法。

它做两件事：

```text
把 JSON 字符串解析成 Python 数据
按 Pydantic 模型校验字段
```

如果模型返回：

```json
{
  "summary": "今天复习。",
  "suggestions": [],
  "next_checkpoint": "继续。"
}
```

会失败。

因为 `suggestions` 要求至少 1 条建议。

## 21. `response_format={"type": "json_object"}` 是什么

当前结构化调用：

```python
content = call_chat_completion(
    messages,
    settings=settings,
    client=client,
    response_format={"type": "json_object"},
)
```

它会把请求体变成：

```json
{
  "model": "...",
  "messages": [],
  "temperature": 0.2,
  "response_format": {
    "type": "json_object"
  }
}
```

作用是请求 provider 尽量返回 JSON 对象。

但要注意：

```text
response_format 不能替代 Pydantic 校验。
```

模型即使返回 JSON，也可能字段不符合业务模型。

所以仍然需要：

```python
StructuredLearningSuggestion.model_validate_json(content)
```

## 22. `structured_llm_demo.py` 和 `llm_demo.py` 的区别

普通 demo：

```powershell
py -3.13 -m app.llm_demo
```

调用：

```python
generate_learning_suggestion(student)
```

返回普通字符串。

结构化 demo：

```powershell
py -3.13 -m app.structured_llm_demo
```

调用：

```python
generate_structured_learning_suggestion(student)
```

返回：

```python
StructuredLearningSuggestion
```

然后打印：

```python
suggestion.model_dump_json(indent=2)
```

也就是结构化 JSON。

## 23. `/suggestion` 和 `/ai/suggestion` 为什么分开

当前 API 有两个建议入口。

离线规则建议：

```text
GET /suggestion
```

AI 建议：

```text
POST /ai/suggestion
```

分开的原因是边界不同。

`GET /suggestion`：

```text
不需要 API Key
不访问网络
稳定可用
适合作为基础功能
```

`POST /ai/suggestion`：

```text
需要 provider 配置
可能请求失败
返回结构化 AI 建议
失败时返回 503
```

这样设计不会破坏 Stage 3 已经稳定的 API。

## 24. CLI 中为什么保留离线规则建议

当前 CLI 菜单：

```text
1. 添加学习笔记
2. 查看学习信息
3. 查看离线规则建议
4. 生成 AI 学习建议
5. 退出
```

保留离线规则建议，是因为 AI provider 可能不可用。

例如：

```text
.env 没有 API Key
Ollama 没启动
网络请求失败
模型返回 JSON 不符合 schema
```

`suggest_with_ai()` 会捕获这些错误，并提示用户可以先使用离线规则建议。

这是一种降级设计。

```text
AI 能用时提供更强能力
AI 不能用时核心学习助手仍然能工作
```

## 25. 当前项目中的 Stage 4 数据流

### 普通文本模型调用

```text
py -3.13 -m app.llm_demo
-> load_student()
-> generate_learning_suggestion(student)
-> build_learning_suggestion_messages(student)
-> call_chat_completion(messages)
-> get_llm_settings()
-> require_llm_api_key()
-> POST {base_url}/chat/completions
-> parse_chat_completion_text(response.json())
-> print(text)
```

### 结构化模型调用

```text
py -3.13 -m app.structured_llm_demo
-> load_student()
-> generate_structured_learning_suggestion(student)
-> build_structured_learning_suggestion_messages(student)
-> StructuredLearningSuggestion.model_json_schema()
-> call_chat_completion(..., response_format={"type": "json_object"})
-> parse_chat_completion_text(response.json())
-> StructuredLearningSuggestion.model_validate_json(content)
-> print(model_dump_json)
```

### API AI 建议调用

```text
POST /ai/suggestion
-> load_student()
-> generate_structured_learning_suggestion(student)
-> provider 请求成功
-> AISuggestionResponse(source="ai", suggestion=suggestion)
```

失败时：

```text
缺少 API Key
provider 请求失败
模型返回结构不合法
```

都会转换成：

```text
503 Service Unavailable
```

### CLI AI 建议调用

```text
py -3.13 -m app.main
-> 选择 4. 生成 AI 学习建议
-> generate_structured_learning_suggestion(student)
-> format_ai_suggestion(suggestion)
-> print 多行中文建议
```

如果失败：

```text
AI 建议暂不可用。
你可以先使用选项 3 获取离线规则建议。
```

## 26. 常见错误与排查

### `ModuleNotFoundError: No module named 'app'`

通常是工作目录错了。

应该进入：

```powershell
cd E:\Code\agentic-learning-lab\ai-learning-assistant
```

再运行：

```powershell
py -3.13 -m app.llm_demo
```

### `can't open file '...\app.llm_demo'`

说明你把模块名当成脚本路径运行了。

错误：

```powershell
python app.llm_demo
```

正确：

```powershell
python -m app.llm_demo
```

### `Missing required environment variable`

说明当前 provider 需要 API Key，但 `.env` 里没有填。

检查：

```text
LLM_PROVIDER
DEEPSEEK_API_KEY
VOLCENGINE_AGENT_PLAN_API_KEY
```

如果使用 Ollama，要确认：

```text
LLM_PROVIDER=ollama
OLLAMA_API_KEY=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
```

并且本地 Ollama 服务已经启动。

### `AI provider request failed`

说明 HTTP 请求失败。

常见原因：

```text
base_url 错误
model 名称错误
API Key 无效
网络不可用
本地模型服务没启动
```

### `LLM response was not a valid structured learning suggestion`

说明模型返回了内容，但没有通过 Pydantic 校验。

可能是：

```text
不是 JSON
缺少 summary
suggestions 是空列表
estimated_minutes 小于 5 或大于 180
next_checkpoint 为空
```

这也是为什么结构化输出不能只依赖 prompt。

prompt 是要求。
Pydantic 校验是程序边界。

### `GET /suggestion` 没有调用 AI

这是当前设计。

`GET /suggestion` 是离线规则建议。

AI 建议入口是：

```text
POST /ai/suggestion
```

CLI 中对应：

```text
4. 生成 AI 学习建议
```

### 断点进不去 demo

IDE 配置建议：

```text
Interpreter:
ai-learning-assistant/.venv/Scripts/python.exe

Working directory:
E:\Code\agentic-learning-lab\ai-learning-assistant

Module name:
app.llm_demo
```

结构化 demo 则是：

```text
Module name:
app.structured_llm_demo
```
