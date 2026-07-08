# 第 4.4 课：结构化输出

## 1. 本课目标

第 4.3 课已经完成了第一次模型调用：

```text
Student -> messages -> chat/completions -> 普通文本建议
```

但普通文本有一个问题：

```text
人能读，程序不好处理。
```

本课要把模型输出升级为结构化结果：

```text
Student
-> generate_structured_learning_suggestion(...)
-> StructuredLearningSuggestion
```

你要学会：

- 为什么 AI 应用不能只依赖一段自然语言回答。
- 如何用 Pydantic 定义模型输出结构。
- 如何把 Pydantic schema 放进 prompt。
- 如何请求 provider 返回 JSON 对象。
- 如何用 `model_validate_json()` 校验模型返回内容。
- 如何测试结构化输出的成功和失败路径。

本课仍不把 AI 建议接入 `GET /suggestion`。
当前 API 保持稳定，AI 调用继续先留在 `app/llm.py`。

## 2. 你会新增什么项目能力

本课会更新：

```text
app/models.py
app/llm.py
tests/test_llm.py
```

新增结构化结果模型：

```text
StructuredLearningSuggestion
├── summary
├── suggestions
│   ├── title
│   ├── description
│   └── estimated_minutes
└── next_checkpoint
```

新增调用入口：

```python
generate_structured_learning_suggestion(student)
```

它返回的不是字符串，而是 Pydantic 模型对象。

这意味着后续代码可以稳定访问：

```python
result.summary
result.suggestions[0].title
result.suggestions[0].estimated_minutes
result.next_checkpoint
```

## 3. 前置知识

开始前，你应该已经理解：

- Pydantic `BaseModel` 可以定义字段和校验规则。
- 第 4.3 课的 `call_chat_completion()` 会返回模型文本。
- JSON 是程序之间交换结构化数据的常见格式。
- 模型输出不可信，必须验证。
- 单元测试不能依赖真实 provider。

本课会用到 Pydantic v2 的两个能力：

```python
StructuredLearningSuggestion.model_json_schema()
StructuredLearningSuggestion.model_validate_json(content)
```

前者生成 JSON Schema，用来告诉模型应该返回什么结构。
后者把模型返回的 JSON 字符串解析并校验成 Pydantic 对象。

## 4. 核心概念

### 普通文本为什么不够

第 4.3 课的函数返回：

```text
建议：今天复习 FastAPI，并写一个小接口。
```

这对人类够用。
但如果程序想知道：

- 摘要是什么？
- 有几条建议？
- 每条建议预计多少分钟？
- 下一次学习检查点是什么？

普通文本就很难稳定解析。

你当然可以用字符串切分：

```python
text.split("建议：")
```

但这很脆。
模型稍微换一种表达，解析就会失败。

结构化输出的目标是让模型返回类似：

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

程序可以直接处理这个对象。

### schema 是输出契约

本课会把结构定义放在 `app/models.py`：

```python
class StructuredLearningSuggestion(BaseModel):
    ...
```

它有两层作用：

1. 给程序校验模型输出。
2. 给模型说明应该返回什么字段。

也就是说，它既是 Python 类型，也是输出契约。

后面进入 LangChain 时，你会看到类似概念：

```text
response_format = SomePydanticModel
structured_response
```

LangChain 会替你处理更多细节。
但底层思想仍然是：

```text
先定义结构，再让模型按结构输出，最后校验。
```

### JSON mode 不是最终保证

很多 provider 支持类似：

```json
{"type": "json_object"}
```

它通常表示“请尽量返回 JSON 对象”。

但这不代表结果一定符合业务 schema。
模型可能返回：

```json
{"summary": "继续学习"}
```

这是 JSON，但不是我们要的完整学习建议。

所以本课会做两层约束：

```text
prompt 中放 schema
请求中带 response_format
返回后用 Pydantic 校验
```

不要把结构化输出理解成“相信模型会乖”。
真正可靠的是：

```text
模型生成 + 程序校验
```

## 5. 代码实现

### 第一步：新增结构化建议模型

打开：

```text
ai-learning-assistant/app/models.py
```

新增：

```python
class LearningSuggestionItem(BaseModel):
    title: str = Field(min_length=1, description="学习建议标题")
    description: str = Field(min_length=1, description="具体要做什么")
    estimated_minutes: int = Field(ge=5, le=180, description="预计学习分钟数")
```

这个模型表示一条具体建议。

字段说明：

| 字段 | 含义 |
| --- | --- |
| `title` | 建议标题 |
| `description` | 具体要做什么 |
| `estimated_minutes` | 预计学习时间，限制在 5 到 180 分钟 |

再新增：

```python
class StructuredLearningSuggestion(BaseModel):
    summary: str = Field(min_length=1, description="今日学习建议摘要")
    suggestions: list[LearningSuggestionItem] = Field(
        min_length=1,
        max_length=3,
        description="1 到 3 条可执行学习建议",
    )
    next_checkpoint: str = Field(min_length=1, description="下一次学习前要确认的检查点")
```

这就是 AI 建议的完整结构。

它要求：

- 必须有 `summary`。
- 必须有 1 到 3 条 `suggestions`。
- 每条建议都必须有标题、描述和预计分钟数。
- 必须有 `next_checkpoint`。

### 第二步：导入 `json` 和结构化模型

打开：

```text
ai-learning-assistant/app/llm.py
```

把导入改成：

```python
import json
from typing import Any

import httpx

from app.config import LLMSettings, get_llm_settings, require_llm_api_key
from app.models import StructuredLearningSuggestion, Student
```

`json` 用来把 schema 转成适合放进 prompt 的字符串。

### 第三步：构造结构化输出 messages

新增函数：

```python
def build_structured_learning_suggestion_messages(student: Student) -> list[dict[str, str]]:
    schema = json.dumps(
        StructuredLearningSuggestion.model_json_schema(),
        ensure_ascii=False,
        indent=2,
    )
    user_content = "\n\n".join(
        [
            build_learning_suggestion_input(student),
            "请只返回一个 JSON 对象，不要返回 Markdown，不要返回代码块。",
            "JSON 必须符合下面的 schema：",
            schema,
        ]
    )

    return [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": user_content},
    ]
```

这里有三个关键点。

第一，继续复用第 4.3 课的学员上下文：

```python
build_learning_suggestion_input(student)
```

第二，明确要求只返回 JSON 对象：

```text
不要返回 Markdown，不要返回代码块。
```

第三，把 Pydantic schema 放进 prompt：

```python
StructuredLearningSuggestion.model_json_schema()
```

这能让模型知道字段名、嵌套结构和基本约束。

### 第四步：让模型调用支持 `response_format`

把 `call_chat_completion()` 的参数改成：

```python
def call_chat_completion(
    messages: list[dict[str, str]],
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
    response_format: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> str:
```

然后在 payload 里加入：

```python
if response_format is not None:
    payload["response_format"] = response_format
```

这样普通文本调用仍然不受影响。

结构化调用可以传：

```python
response_format={"type": "json_object"}
```

### 第五步：解析结构化结果

新增：

```python
def parse_structured_learning_suggestion(content: str) -> StructuredLearningSuggestion:
    try:
        return StructuredLearningSuggestion.model_validate_json(content)
    except ValueError as error:
        raise ValueError("LLM response was not a valid structured learning suggestion.") from error
```

这个函数只做一件事：

```text
把模型返回的 JSON 字符串变成 Pydantic 对象。
```

如果模型返回普通文本：

```text
建议：今天复习 FastAPI。
```

它会报错。

如果模型返回 JSON 但字段不符合要求，也会报错。

### 第六步：新增结构化建议入口

新增：

```python
def generate_structured_learning_suggestion(
    student: Student,
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
) -> StructuredLearningSuggestion:
    messages = build_structured_learning_suggestion_messages(student)
    content = call_chat_completion(
        messages,
        settings=settings,
        client=client,
        response_format={"type": "json_object"},
    )
    return parse_structured_learning_suggestion(content)
```

这就是本课最重要的新入口。

它的返回值是：

```python
StructuredLearningSuggestion
```

不是普通字符串。

### 第七步：补充测试

打开：

```text
ai-learning-assistant/tests/test_llm.py
```

本课新增测试覆盖：

- `call_chat_completion()` 可以传入 `response_format`。
- 结构化 messages 包含 schema。
- 有效 JSON 可以解析成 Pydantic 对象。
- 普通文本会被拒绝。
- schema 不匹配会被拒绝。
- `generate_structured_learning_suggestion()` 会使用 JSON mode 和 schema。

重点不是测试模型是否聪明。
重点是测试我们的程序边界：

```text
只接受符合 schema 的结构化结果。
```

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
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py
```

如果你已经配置好 provider，可以手动试结构化调用。
例如 Ollama：

```text
LLM_PROVIDER=ollama
OLLAMA_MODEL=你的本地模型名
```

手动调用：

```powershell
py -3.13 -c "from app.llm import generate_structured_learning_suggestion; student={'name':'Alice','goal':'学习 LangChain','python_level':'basic','notes':['Pydantic 可以校验模型输出']}; result=generate_structured_learning_suggestion(student); print(result.model_dump())"
```

这条真实调用不是自动验收要求。
自动测试仍然使用 fake client。

## 7. 常见错误

### 只要求模型“返回 JSON”，但不校验

这是半成品。

模型返回：

```json
{"summary": "继续学习"}
```

也是 JSON。
但它缺少 `suggestions` 和 `next_checkpoint`。

所以必须用 Pydantic 校验。

### 把 schema 写死在 prompt 里

不要手写一大段 JSON schema 字符串。

本课直接从 Pydantic 模型生成：

```python
StructuredLearningSuggestion.model_json_schema()
```

这样模型定义和 prompt 契约不会分裂。

### 让结构化输出直接影响现有 API

不要急着改 `GET /suggestion`。

当前阶段还没有设计 AI API 的错误降级、超时、费用控制和 provider 不可用时的响应。

本课只完成结构化调用层。

### 忽略失败测试

结构化输出最重要的测试不是“成功返回”。
更重要的是失败路径：

- 普通文本要失败。
- 缺字段要失败。
- 空列表要失败。
- 不合理的分钟数要失败。

这些失败能保护后续 API 和 LangChain Agent。

## 8. 练习

练习 1：解释 `summary`、`suggestions` 和 `next_checkpoint` 分别适合放什么内容。

练习 2：把测试里的 `estimated_minutes` 改成 `3`，观察为什么会失败。

练习 3：把 fake client 返回的 JSON 删除 `next_checkpoint` 字段，观察报错。

练习 4：打印 `StructuredLearningSuggestion.model_json_schema()`，看看 Pydantic 生成了什么。

练习 5：解释为什么 `response_format={"type": "json_object"}` 不能替代 Pydantic 校验。

## 9. 验收标准

完成本课后，你应该能做到：

- 解释为什么普通文本不适合长期作为程序输入。
- 解释结构化输出和 JSON mode 的区别。
- 解释 Pydantic schema 在 prompt 和校验中的双重作用。
- 看懂 `LearningSuggestionItem` 和 `StructuredLearningSuggestion`。
- 看懂 `parse_structured_learning_suggestion()` 为什么会拒绝无效输出。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。
- 知道当前 `GET /suggestion` 仍未接入 AI。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课是后续 Agent 开发的关键铺垫。

| 本课内容 | 后续升级 |
| --- | --- |
| Pydantic 输出模型 | LangChain structured output |
| `model_json_schema()` | prompt/schema 契约 |
| `model_validate_json()` | 模型输出校验 |
| `generate_structured_learning_suggestion()` | Agent 或 Graph 节点返回结构 |
| 失败路径测试 | Agent 输出稳定性测试 |

LangChain 的结构化输出会把 schema 和模型调用封装得更好。
但你现在已经知道它在解决什么问题。

LangGraph 的 node 不应该返回难以解析的长文本。
后续学习流程里的“判断水平”“出题”“批改”都更适合返回结构化状态。

Deep Agents 会写计划和总结文件。
长任务里更需要结构化中间结果，否则任务执行过程很难恢复、审查和继续。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-4/04-04-structured-output.md`

修改文件：

- `README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/llm.py`
- `ai-learning-assistant/tests/test_llm.py`
- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `docs/tutorial/README.md`

代码变更：

- 新增 `LearningSuggestionItem`。
- 新增 `StructuredLearningSuggestion`。
- 新增 `build_structured_learning_suggestion_messages()`。
- `call_chat_completion()` 新增可选 `response_format` 参数。
- 新增 `parse_structured_learning_suggestion()`。
- 新增 `generate_structured_learning_suggestion()`。
- 新增结构化输出相关测试。

新增依赖：

- 无。继续复用已有 `pydantic`、`httpx`、`pytest`。

环境变量变更：

- 无。继续复用第 4.2 课的 provider 配置。

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py
```

下一步：

- 第 4.5 课：把 AI 建议封装为独立 API，设计 provider 不可用时的错误和降级边界。
