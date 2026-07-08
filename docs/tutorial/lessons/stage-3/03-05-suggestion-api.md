# 第 3.5 课：学习建议 API

## 1. 本课目标

第 1.5 课已经做过一个命令行版本的学习建议功能：

```python
if student["python_level"] == "beginner":
    print("建议：今天学习变量、函数、字典。")
elif student["python_level"] == "basic":
    print("建议：今天学习类、文件读写、异常处理。")
else:
    print("建议：今天开始学习 LangChain 的 agent。")
```

第 3.3 和第 3.4 课已经把资料和笔记变成了 API：

```http
GET /profile
POST /profile
GET /notes
POST /notes
```

本课要把学习建议也变成 API：

```http
GET /suggestion
```

本课目标不是引入 AI。

本课目标是先把“规则建议”变成一个稳定、可测试、可被后续 Agent 复用的接口。

## 2. 你会新增什么项目能力

本课之后，项目会新增：

```http
GET /suggestion
```

它会读取当前保存的：

```text
student["python_level"]
```

然后返回结构化建议：

```json
{
  "python_level": "beginner",
  "suggestion": "建议：今天学习变量、函数、字典。"
}
```

三档规则保持和阶段 1 一致：

| `python_level` | `suggestion` |
| --- | --- |
| `beginner` | 建议：今天学习变量、函数、字典。 |
| `basic` | 建议：今天学习类、文件读写、异常处理。 |
| 其它值 | 建议：今天开始学习 LangChain 的 agent。 |

同时，本课会把建议规则抽到：

```text
app/suggestions.py
```

这样 CLI 和 API 共用同一份规则。

## 3. 前置知识

开始前确认你已经理解：

- `GET /profile` 会读取学员资料。
- `GET /notes` 会读取学习笔记。
- `load_student()` 会返回完整 `student` 字典。
- `python_level` 是学习建议的判断依据。
- `if/elif/else` 可以表达规则分支。
- Pydantic 响应模型可以约束 API 返回结构。
- pytest 可以测试普通函数，也可以测试 FastAPI route。

本课要串起的链路是：

```text
GET /suggestion
-> load_student()
-> 读取 python_level
-> build_suggestion(python_level)
-> SuggestionResponse
```

## 4. 核心概念

### 不要复制业务规则

第 1 阶段的 CLI 里已经有学习建议规则。

如果本课在 API 里重新写一遍：

```python
if student["python_level"] == "beginner":
    ...
```

就会出现两份规则：

```text
CLI 一份
API 一份
```

以后你改 beginner 的建议时，很可能只改了一边。

所以本课先把规则抽成普通函数：

```python
def build_suggestion(python_level: str) -> str:
    ...
```

然后：

```text
CLI 调它。
API 也调它。
```

这就是“同一条业务规则只维护一份”。

### API 不一定都会修改数据

前两课里：

```http
POST /profile
POST /notes
```

都会写入数据。

但本课的：

```http
GET /suggestion
```

只读取资料并计算建议。

它不应该调用：

```python
save_student()
```

因为生成建议不应该改变学习档案。

### 响应要保持结构化

不要直接返回一个字符串：

```json
"建议：今天学习变量、函数、字典。"
```

更好的方式是返回对象：

```json
{
  "python_level": "beginner",
  "suggestion": "建议：今天学习变量、函数、字典。"
}
```

原因是后续可以扩展：

```text
reason
next_topics
estimated_minutes
source
```

到了 LLM 阶段，这个结构会继续升级成更完整的学习建议对象。

## 5. 代码实现

### 第一步：新增 `app/suggestions.py`

新建文件：

```text
ai-learning-assistant/app/suggestions.py
```

写入：

```python
def build_suggestion(python_level: str) -> str:
    if python_level == "beginner":
        return "建议：今天学习变量、函数、字典。"
    if python_level == "basic":
        return "建议：今天学习类、文件读写、异常处理。"
    return "建议：今天开始学习 LangChain 的 agent。"
```

这里没有使用 `elif`，而是使用两个连续的 `if`。

原因是每个分支都会 `return`。

一旦命中，函数就结束。

### 第二步：让 CLI 复用建议函数

打开：

```text
ai-learning-assistant/app/cli.py
```

新增导入：

```python
from app.suggestions import build_suggestion
```

把原来的 `suggest_next_step()` 改成：

```python
def suggest_next_step() -> None:
    print()
    print("=== 今日学习建议 ===")
    print(build_suggestion(student["python_level"]))
```

这样 CLI 行为不会变，但规则已经不再写在 CLI 里。

### 第三步：新增响应模型

打开：

```text
ai-learning-assistant/app/models.py
```

新增：

```python
class SuggestionResponse(BaseModel):
    python_level: str = ""
    suggestion: str
```

`python_level` 给默认空字符串，是为了兼容旧数据。

如果旧的 `data/student.json` 里还没有有效水平，接口仍然可以返回兜底建议。

### 第四步：新增 `GET /suggestion`

打开：

```text
ai-learning-assistant/app/api.py
```

更新导入：

```python
from app.models import (
    NoteCreate,
    NotesResponse,
    Student,
    StudentProfile,
    StudentProfileResponse,
    SuggestionResponse,
)
from app.storage import load_student, save_student
from app.suggestions import build_suggestion
```

新增接口：

```python
@app.get("/suggestion", response_model=SuggestionResponse)
def get_suggestion() -> SuggestionResponse:
    student = load_student()

    return SuggestionResponse(
        python_level=student["python_level"],
        suggestion=build_suggestion(student["python_level"]),
    )
```

注意：

```python
get_suggestion()
```

没有调用：

```python
save_student()
```

因为读取建议不应该修改数据。

### 第五步：测试建议函数

新增：

```text
ai-learning-assistant/tests/test_suggestions.py
```

写入：

```python
from app.suggestions import build_suggestion


def test_build_suggestion_for_beginner() -> None:
    assert build_suggestion("beginner") == "建议：今天学习变量、函数、字典。"


def test_build_suggestion_for_basic() -> None:
    assert build_suggestion("basic") == "建议：今天学习类、文件读写、异常处理。"


def test_build_suggestion_for_intermediate() -> None:
    assert build_suggestion("intermediate") == "建议：今天开始学习 LangChain 的 agent。"


def test_build_suggestion_falls_back_to_agent_suggestion() -> None:
    assert build_suggestion("") == "建议：今天开始学习 LangChain 的 agent。"
```

为什么要单独测试普通函数？

因为这样不用启动 API，就能确认规则本身是对的。

### 第六步：测试 `GET /suggestion`

继续更新：

```text
ai-learning-assistant/tests/test_api.py
```

新增测试：

```python
def test_get_suggestion_returns_rule_based_suggestion(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Frank",
            "goal": "Review conditionals",
            "python_level": "beginner",
            "notes": ["Need API suggestion"],
        }
    )

    response = client.get("/suggestion")

    assert response.status_code == 200
    assert response.json() == {
        "python_level": "beginner",
        "suggestion": "建议：今天学习变量、函数、字典。",
    }
    assert storage.load_student() == {
        "name": "Frank",
        "goal": "Review conditionals",
        "python_level": "beginner",
        "notes": ["Need API suggestion"],
    }
```

最后这段断言很重要。

它证明 `GET /suggestion` 没有改动学习档案。

再补一个旧数据兜底测试：

```python
def test_get_suggestion_uses_fallback_for_missing_level(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Grace",
            "goal": "",
            "python_level": "",
            "notes": [],
        }
    )

    response = client.get("/suggestion")

    assert response.status_code == 200
    assert response.json() == {
        "python_level": "",
        "suggestion": "建议：今天开始学习 LangChain 的 agent。",
    }
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
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

访问文档：

```text
http://127.0.0.1:8000/docs
```

你应该能看到：

```text
GET /suggestion
```

手动调用：

```http
GET http://127.0.0.1:8000/suggestion
```

响应示例：

```json
{
  "python_level": "beginner",
  "suggestion": "建议：今天学习变量、函数、字典。"
}
```

## 7. 常见错误

### 在 API 里复制一份建议规则

错误方向：

```python
@app.get("/suggestion")
def get_suggestion():
    student = load_student()
    if student["python_level"] == "beginner":
        ...
```

这样 CLI 和 API 会有两份规则。

正确方向是：

```python
build_suggestion(student["python_level"])
```

### `GET /suggestion` 修改了数据

错误写法：

```python
student = load_student()
student["last_suggestion"] = build_suggestion(student["python_level"])
save_student(student)
```

本课还没有设计 `last_suggestion` 字段。

不要偷偷改数据结构。

### 直接返回字符串

可以这样写：

```python
return build_suggestion(student["python_level"])
```

但不建议。

因为后续扩展会困难。

本课使用：

```python
SuggestionResponse
```

保持结构化返回。

### 忘记测试兜底分支

旧数据里可能出现：

```json
{
  "python_level": ""
}
```

如果测试只覆盖 `beginner`，就不知道旧数据会不会坏。

所以本课补了空字符串兜底测试。

### 把本课写成 AI 建议

第 3.5 仍然是规则建议。

不要引入：

```text
OpenAI API
LangChain
LLM prompt
```

这些会放到后面的 LLM 和 LangChain 阶段。

## 8. 练习

练习 1：把 `python_level` 保存为 `basic`，调用 `GET /suggestion`，确认返回类、文件读写、异常处理建议。

练习 2：把 `python_level` 保存为 `intermediate`，调用 `GET /suggestion`，确认返回 LangChain agent 建议。

练习 3：给 `build_suggestion()` 增加一个新的分支：

```python
if python_level == "intermediate":
    return "建议：今天学习 LangChain 工具调用。"
```

然后更新测试。

练习 4：尝试把 `GET /suggestion` 改成直接返回字符串，观察 `/docs` 里的响应结构变化。

练习完成后，建议恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- 存在 `app/suggestions.py`。
- 存在 `build_suggestion(python_level: str) -> str`。
- CLI 的 `suggest_next_step()` 复用 `build_suggestion()`。
- 存在 `SuggestionResponse`。
- 存在 `GET /suggestion`。
- `GET /suggestion` 使用 `load_student()`。
- `GET /suggestion` 不调用 `save_student()`。
- `GET /suggestion` 返回 `python_level` 和 `suggestion`。
- `beginner` 返回变量、函数、字典建议。
- `basic` 返回类、文件读写、异常处理建议。
- `intermediate` 和旧数据空值返回 LangChain agent 建议。
- pytest 测试覆盖普通建议函数和 API route。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。
- 没有引入 LLM、LangChain 或数据库。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课的 `build_suggestion()` 是后续 AI 建议能力的前置版本。

| 现在 | 后续升级 |
| --- | --- |
| `build_suggestion()` | LLM 生成个性化建议 |
| `GET /suggestion` | LangChain 工具或 Agent API |
| `SuggestionResponse` | 结构化学习建议模型 |
| `python_level` 分支 | LangGraph 条件边 |
| 规则建议 | Deep Agents 生成学习计划前的基础输入 |

到了 LLM 阶段，建议不再只靠三条写死规则。

但现在先保留规则建议有两个好处：

- 不需要 API Key，学习者可以稳定运行。
- 后续替换成 LLM 时，有一份明确的旧行为可以对照。

到了 LangGraph 阶段：

```text
if python_level == "beginner"
```

会升级成条件边。

到了 Deep Agents 阶段，学习建议会变成长期学习计划的一部分。

所以本课的重点不是“建议文本有多聪明”。

重点是让建议能力变成可复用、可测试、结构化的项目能力。

## 11. 本课变更清单

新增文件：

- `ai-learning-assistant/app/suggestions.py`
- `ai-learning-assistant/tests/test_suggestions.py`
- `docs/tutorial/lessons/stage-3/03-05-suggestion-api.md`

修改文件：

- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_api.py`
- `ai-learning-assistant/README.md`
- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `docs/tutorial/README.md`
- `README.md`

新增模型：

```python
SuggestionResponse
```

新增接口：

```http
GET /suggestion
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

API 人工验证：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

然后访问：

```text
http://127.0.0.1:8000/docs
```

验证结果：

- `GET /suggestion` 可以读取当前 Python 水平。
- `GET /suggestion` 可以返回规则学习建议。
- `GET /suggestion` 不会修改 `data/student.json`。
- CLI 和 API 共用 `build_suggestion()`。
- pytest 测试全部通过。
- Python 文件可以编译通过。

下一步：

- 第 3.6 课：API 错误处理，补充更稳定的错误响应。
- 第 3.7 课：存储边界与数据库迁移预告，解释为什么当前使用 JSON，以及未来何时迁移到 SQLite / PostgreSQL。
