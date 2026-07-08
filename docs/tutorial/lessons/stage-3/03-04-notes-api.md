# 第 3.4 课：学习笔记 API

## 1. 本课目标

第 3.3 课已经完成了学员资料 API：

```http
GET /profile
POST /profile
```

它能读取和更新：

```text
name
goal
python_level
```

并且会保留已有：

```text
student["notes"]
```

本课开始把学习笔记也暴露成 API：

```http
GET /notes
POST /notes
```

本课目标是让 FastAPI 能管理阶段 1 就出现过的学习笔记列表：

```text
GET /notes   读取当前所有学习笔记
POST /notes  添加一条新的学习笔记，并保存到 data/student.json
```

注意，本课只做笔记 API。

学习建议 API 会放到第 3.5 课。

## 2. 你会新增什么项目能力

本课之后，项目会新增两个接口：

```http
GET /notes
POST /notes
```

`GET /notes` 返回当前保存的学习笔记：

```json
{
  "notes": [
    "Read FastAPI docs",
    "Write API tests"
  ],
  "note_count": 2
}
```

`POST /notes` 接收请求体：

```json
{
  "content": "Learn request body validation"
}
```

然后把新笔记追加到：

```text
student["notes"]
```

并保存到：

```text
data/student.json
```

如果原来已有学员资料，本课不会修改它们。

也就是说，添加笔记不会清空：

```text
student["name"]
student["goal"]
student["python_level"]
```

## 3. 前置知识

开始前确认你已经理解：

- `load_student()` 会从 JSON 文件读取完整 `student` 字典。
- `save_student(student)` 会保存完整 `student` 字典。
- `student["notes"]` 是一个 `list[str]`。
- `list.append(value)` 会把新元素追加到列表末尾。
- Pydantic 模型可以校验请求体。
- `response_model` 可以声明接口返回结构。
- pytest 里可以用 `tmp_path` 隔离真实文件。

本课会继续串起这条链路：

```text
FastAPI route
-> Pydantic 请求体校验
-> load_student()
-> 修改 notes 列表
-> save_student()
-> response_model 返回结构化结果
```

## 4. 核心概念

### 笔记新增不是覆盖，而是追加

学习笔记天然是列表。

所以新增一条笔记时，不应该这样写：

```python
student["notes"] = [note.content]
```

这会把旧笔记全部覆盖。

正确行为是：

```python
student["notes"].append(note.content)
```

这和阶段 1 的 CLI 版本是同一个核心动作，只是入口从命令行变成了 HTTP API。

### 请求模型只接收一条笔记

本课新增请求模型：

```python
class NoteCreate(BaseModel):
    content: str = Field(min_length=1)
```

为什么字段名叫 `content`，而不是直接叫 `note`？

因为后面笔记可能会扩展：

```text
content
created_at
source
tags
```

现在只保存字符串，但模型先用更稳定的名字。

### 响应模型返回列表和数量

本课新增响应模型：

```python
class NotesResponse(BaseModel):
    notes: list[str] = Field(default_factory=list)
    note_count: int = 0
```

它返回两个信息：

| 字段 | 含义 |
| --- | --- |
| `notes` | 当前所有学习笔记 |
| `note_count` | 当前笔记数量 |

`note_count` 看起来可以由调用方自己算，但 API 直接返回它有两个好处：

- 前端或 Agent 不需要重复计算。
- 后续做学习状态摘要时，可以直接读取数量。

### 使用 `Field(default_factory=list)`

你可能会问，为什么不写：

```python
notes: list[str] = []
```

在 Python 里，可变默认值容易引发共享状态问题。

Pydantic 会做一些保护，但作为学习习惯，列表默认值优先写成：

```python
Field(default_factory=list)
```

这比直接写 `[]` 更稳。

## 5. 代码实现

### 第一步：更新 `app/models.py`

打开：

```text
ai-learning-assistant/app/models.py
```

新增两个模型：

```python
class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class NotesResponse(BaseModel):
    notes: list[str] = Field(default_factory=list)
    note_count: int = 0
```

完整相关代码如下：

```python
from typing import TypedDict

from pydantic import BaseModel, Field


class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]


class StudentProfile(BaseModel):
    name: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    python_level: str = Field(pattern="^(beginner|basic|intermediate)$")


class StudentProfileResponse(BaseModel):
    name: str = ""
    goal: str = ""
    python_level: str = ""
    note_count: int = 0


class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class NotesResponse(BaseModel):
    notes: list[str] = Field(default_factory=list)
    note_count: int = 0
```

### 第二步：更新 `app/api.py`

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
)
from app.storage import load_student, save_student
```

新增 `GET /notes`：

```python
@app.get("/notes", response_model=NotesResponse)
def get_notes() -> NotesResponse:
    student = load_student()

    return NotesResponse(
        notes=student["notes"],
        note_count=len(student["notes"]),
    )
```

新增 `POST /notes`：

```python
@app.post("/notes", response_model=NotesResponse)
def add_note(note: NoteCreate) -> NotesResponse:
    student = load_student()
    student["notes"].append(note.content)
    save_student(student)

    return NotesResponse(
        notes=student["notes"],
        note_count=len(student["notes"]),
    )
```

这里有两个关键点：

```python
student["notes"].append(note.content)
```

表示追加，而不是覆盖。

```python
save_student(student)
```

表示新笔记会保存到 JSON 文件，不只是临时存在内存里。

### 第三步：更新 `tests/test_api.py`

继续使用第 3.3 课引入的临时文件隔离函数：

```python
def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"
```

测试 `GET /notes`：

```python
def test_get_notes_returns_saved_notes(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Dana",
            "goal": "Review APIs",
            "python_level": "basic",
            "notes": ["Read FastAPI docs", "Write API tests"],
        }
    )

    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json() == {
        "notes": ["Read FastAPI docs", "Write API tests"],
        "note_count": 2,
    }
```

测试 `POST /notes` 会追加笔记，并保留学员资料：

```python
def test_post_notes_appends_note_and_keeps_profile(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Eve",
            "goal": "Build note API",
            "python_level": "intermediate",
            "notes": ["Existing note"],
        }
    )

    response = client.post(
        "/notes",
        json={
            "content": "New API note",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "notes": ["Existing note", "New API note"],
        "note_count": 2,
    }
    assert storage.load_student() == {
        "name": "Eve",
        "goal": "Build note API",
        "python_level": "intermediate",
        "notes": ["Existing note", "New API note"],
    }
```

测试空笔记会被拒绝：

```python
def test_post_notes_rejects_empty_note(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)

    response = client.post(
        "/notes",
        json={
            "content": "",
        },
    )

    assert response.status_code == 422
```

为什么空字符串会返回 `422`？

因为模型里写了：

```python
content: str = Field(min_length=1)
```

FastAPI 会在进入 route 函数前先完成请求体校验。

校验失败时，函数不会执行，数据也不会保存。

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
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/__init__.py tests/test_storage.py tests/test_api.py
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
GET /notes
POST /notes
```

也可以手动调用：

```http
GET http://127.0.0.1:8000/notes
```

以及：

```http
POST http://127.0.0.1:8000/notes
```

请求体：

```json
{
  "content": "Learn FastAPI notes API"
}
```

成功后响应类似：

```json
{
  "notes": [
    "Existing note",
    "Learn FastAPI notes API"
  ],
  "note_count": 2
}
```

## 7. 常见错误

### 把旧笔记覆盖掉

错误写法：

```python
student["notes"] = [note.content]
```

这会让旧笔记丢失。

正确写法：

```python
student["notes"].append(note.content)
```

### 添加笔记后忘记保存

错误写法：

```python
student = load_student()
student["notes"].append(note.content)
return NotesResponse(notes=student["notes"], note_count=len(student["notes"]))
```

这次请求看起来成功，但重启后数据会丢。

正确写法要加：

```python
save_student(student)
```

### 笔记接口修改了学员资料

`POST /notes` 的职责只是添加笔记。

它不应该改：

```text
name
goal
python_level
```

所以测试里要断言保存后的完整 `student` 字典。

### 使用真实 `data/student.json` 做测试

API 测试不能污染真实学习数据。

继续使用：

```python
tmp_path
```

临时切换：

```python
storage.DATA_FILE
storage.BROKEN_DATA_FILE
```

### 把学习建议接口提前做了

第 3.4 只做笔记 API。

不要顺手加：

```http
GET /suggestion
```

学习建议 API 放到第 3.5 课。

## 8. 练习

练习 1：调用两次 `POST /notes`，再调用 `GET /notes`，确认两条笔记都存在。

练习 2：先调用 `POST /profile` 更新学员资料，再调用 `POST /notes` 添加笔记，确认 `data/student.json` 里资料和笔记都还在。

练习 3：把请求体改成：

```json
{
  "content": ""
}
```

观察接口返回状态码和错误信息。

练习 4：尝试少传 `content` 字段：

```json
{}
```

观察 FastAPI 如何提示字段缺失。

练习完成后，建议恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `GET /notes` 存在。
- `POST /notes` 存在。
- `GET /notes` 使用 `load_student()`。
- `POST /notes` 使用 `load_student()` 和 `save_student()`。
- `POST /notes` 会追加新笔记，而不是覆盖旧笔记。
- `POST /notes` 不修改 `name`、`goal`、`python_level`。
- 合法 `POST /notes` 返回 `200`。
- 空 `content` 返回 `422`。
- 响应中包含 `notes` 和 `note_count`。
- API 测试使用临时文件，不污染真实 `data/student.json`。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。
- 没有提前实现学习建议 API。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

学习笔记是后续 AI 助教的重要上下文。

| 现在 | 后续升级 |
| --- | --- |
| `GET /notes` | LangChain 工具读取学习笔记 |
| `POST /notes` | 对话中保存新的学习记录 |
| `notes: list[str]` | RAG 的轻量资料来源 |
| `note_count` | 学习进度摘要 |
| `NoteCreate` | 后续扩展成更完整的笔记输入模型 |
| `NotesResponse` | Agent 可解析的结构化上下文 |

到了 LangChain 阶段，Agent 可以把“查询学习笔记”包装成工具。

到了 RAG 阶段，笔记可以成为可检索资料的一部分。

到了 LangGraph 阶段，学习流程节点可以根据笔记数量和内容决定下一步教学。

到了 Deep Agents 阶段，长期任务可以把阶段性总结写回学习记录。

所以本课不是简单加两个接口。

它是在给后续 AI 能力准备可读取、可追加、可测试的学习上下文。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-3/03-04-notes-api.md`

修改文件：

- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_api.py`
- `ai-learning-assistant/README.md`
- `docs/tutorial/README.md`
- `README.md`

新增模型：

```python
NoteCreate
NotesResponse
```

新增接口：

```http
GET /notes
POST /notes
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/__init__.py tests/test_storage.py tests/test_api.py
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

- `GET /notes` 可以读取当前学习笔记。
- `POST /notes` 可以追加学习笔记。
- 添加笔记后会保存到 `data/student.json`。
- 添加笔记时不会修改学员资料。
- 空笔记会被 Pydantic 拒绝。
- pytest 测试全部通过。
- Python 文件可以编译通过。

下一步：

- 第 3.5 课：学习建议 API，新增 `GET /suggestion`。
