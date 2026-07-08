# 第 3.3 课：学员资料 API

## 1. 本课目标

第 3.2 课已经用 Pydantic 模型做了一个预览接口：

```http
POST /profile/preview
```

它能校验请求体，也能返回响应模型，但不会保存数据。

现在要进入真正的业务接口：

```http
GET /profile
POST /profile
```

本课目标是把阶段 2 的本地 JSON 存储能力接到 FastAPI：

```text
GET /profile   从 data/student.json 读取学员资料
POST /profile  更新学员资料并保存到 data/student.json
```

本课仍然不处理学习笔记 API。

笔记接口会放到第 3.4 课。

## 2. 你会新增什么项目能力

本课之后，项目会新增两个正式 API：

```http
GET /profile
POST /profile
```

`GET /profile` 返回当前保存的学员资料：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner",
  "note_count": 2
}
```

`POST /profile` 接收请求体：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner"
}
```

并把资料保存到：

```text
data/student.json
```

如果原来已有学习笔记，本课会保留它们。

也就是说，更新资料不会清空：

```text
student["notes"]
```

## 3. 前置知识

开始前确认你已经理解：

- `storage.load_student()` 会读取当前学员资料。
- `storage.save_student(student)` 会保存资料到 JSON。
- `StudentProfile` 是请求体模型。
- `StudentProfileResponse` 是响应模型。
- `response_model` 会声明接口返回结构。
- pytest 可以用临时目录隔离文件读写。

本课会把阶段 2 和阶段 3 第一次真正串起来：

```text
FastAPI route
-> Pydantic 模型校验
-> storage.py 读写 JSON
-> response_model 返回结构化响应
```

## 4. 核心概念

### API route 可以调用普通 Python 函数

FastAPI route 本质上还是 Python 函数。

所以它可以调用阶段 2 写过的函数：

```python
load_student()
save_student(student)
```

这就是项目驱动教程的价值：

```text
前面写的 storage.py 不是废代码。
它会继续成为 API 的底层能力。
```

### `GET /profile` 只读取，不修改

`GET /profile` 的职责是：

```text
读取当前学员资料。
返回给调用方。
```

它不应该调用 `save_student()`。

### `POST /profile` 会保存资料

`POST /profile` 的职责是：

```text
接收新的 name / goal / python_level。
通过 Pydantic 校验。
保留已有 notes。
保存新的 student。
返回更新后的资料摘要。
```

为什么要保留 notes？

因为本课只更新学员资料，不是笔记接口。

如果更新资料时把 `notes` 清空，会造成数据丢失。

### 响应模型可以比请求模型更宽松

第 3.2 课中 `StudentProfileResponse` 继承了 `StudentProfile`。

本课会把它改成独立模型：

```python
class StudentProfileResponse(BaseModel):
    name: str = ""
    goal: str = ""
    python_level: str = ""
    note_count: int = 0
```

原因是历史数据可能来自 CLI 阶段。

比如旧的 `data/student.json` 里可能有：

```json
{
  "name": "Carol",
  "goal": "",
  "python_level": "",
  "notes": ["Only partial data"]
}
```

如果响应模型强制 `goal` 和 `python_level` 都不能为空，`GET /profile` 就会因为旧数据失败。

所以：

```text
POST 请求模型要严格。
GET 响应模型要能展示历史数据。
```

## 5. 代码实现

### 第一步：调整 `app/models.py`

打开：

```text
ai-learning-assistant/app/models.py
```

把 `StudentProfileResponse` 改成独立模型：

```python
class StudentProfileResponse(BaseModel):
    name: str = ""
    goal: str = ""
    python_level: str = ""
    note_count: int = 0
```

完整相关代码：

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
```

### 第二步：更新 `app/api.py`

打开：

```text
ai-learning-assistant/app/api.py
```

新增导入：

```python
from app.models import Student, StudentProfile, StudentProfileResponse
from app.storage import load_student, save_student
```

新增 `GET /profile`：

```python
@app.get("/profile", response_model=StudentProfileResponse)
def get_profile() -> StudentProfileResponse:
    student = load_student()

    return StudentProfileResponse(
        name=student["name"],
        goal=student["goal"],
        python_level=student["python_level"],
        note_count=len(student["notes"]),
    )
```

新增 `POST /profile`：

```python
@app.post("/profile", response_model=StudentProfileResponse)
def update_profile(profile: StudentProfile) -> StudentProfileResponse:
    current_student = load_student()
    updated_student: Student = {
        "name": profile.name,
        "goal": profile.goal,
        "python_level": profile.python_level,
        "notes": current_student["notes"],
    }
    save_student(updated_student)

    return StudentProfileResponse(
        name=updated_student["name"],
        goal=updated_student["goal"],
        python_level=updated_student["python_level"],
        note_count=len(updated_student["notes"]),
    )
```

注意：

```python
"notes": current_student["notes"]
```

这一行是本课的关键。

它保证更新学员资料时不清空学习笔记。

### 第三步：更新 `tests/test_api.py`

测试 API 读写文件时，不能污染真实：

```text
data/student.json
```

所以新增一个测试辅助函数：

```python
from pathlib import Path


def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"
```

测试 `GET /profile`：

```python
def test_get_profile_returns_saved_student(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Bob",
            "goal": "Build APIs",
            "python_level": "basic",
            "notes": ["Keep existing notes"],
        }
    )

    response = client.get("/profile")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Bob",
        "goal": "Build APIs",
        "python_level": "basic",
        "note_count": 1,
    }
```

测试 `POST /profile`：

```python
def test_post_profile_saves_student_and_keeps_notes(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Old",
            "goal": "Old goal",
            "python_level": "beginner",
            "notes": ["Do not remove"],
        }
    )

    response = client.post(
        "/profile",
        json={
            "name": "Carol",
            "goal": "Use profile API",
            "python_level": "intermediate",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "name": "Carol",
        "goal": "Use profile API",
        "python_level": "intermediate",
        "note_count": 1,
    }
    assert storage.load_student() == {
        "name": "Carol",
        "goal": "Use profile API",
        "python_level": "intermediate",
        "notes": ["Do not remove"],
    }
```

测试非法水平：

```python
def test_post_profile_rejects_invalid_level(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)

    response = client.post(
        "/profile",
        json={
            "name": "Carol",
            "goal": "Use profile API",
            "python_level": "advanced",
        },
    )

    assert response.status_code == 422
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
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/__init__.py tests/test_storage.py tests/test_api.py
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

访问：

```text
http://127.0.0.1:8000/docs
```

你应该能看到：

```text
GET /profile
POST /profile
```

也可以手动调用：

```http
GET http://127.0.0.1:8000/profile
```

以及：

```http
POST http://127.0.0.1:8000/profile
```

请求体：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI profile API",
  "python_level": "basic"
}
```

## 7. 常见错误

### 更新资料时清空了笔记

错误写法：

```python
updated_student = {
    "name": profile.name,
    "goal": profile.goal,
    "python_level": profile.python_level,
    "notes": [],
}
```

这会清空已有笔记。

正确写法：

```python
"notes": current_student["notes"]
```

### `GET /profile` 因旧数据失败

如果响应模型继续继承严格的 `StudentProfile`，旧数据中的空字段可能导致响应校验失败。

所以本课把 `StudentProfileResponse` 改成更适合展示的模型。

### 测试污染真实数据

API 测试里不要直接使用真实：

```text
data/student.json
```

本课继续用 `tmp_path` 切换 `storage.DATA_FILE`。

### 把 notes API 偷偷做了

第 3.3 只做学员资料。

不要顺手加：

```http
GET /notes
POST /notes
```

这些放到第 3.4 课。

## 8. 练习

练习 1：调用 `POST /profile` 后，再调用 `GET /profile`，确认返回的是更新后的资料。

练习 2：先手动在 `data/student.json` 里加入两条 notes，再调用 `POST /profile`，确认响应里的 `note_count` 仍然是 2。

练习 3：把 `python_level` 改成 `advanced`，观察接口返回状态码。

练习完成后，建议恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `GET /profile` 存在。
- `POST /profile` 存在。
- `GET /profile` 使用 `load_student()`。
- `POST /profile` 使用 `save_student()`。
- `POST /profile` 更新 `name`、`goal`、`python_level`。
- `POST /profile` 保留已有 `notes`。
- 合法 `POST /profile` 返回 `200`。
- 非法 `python_level` 返回 `422`。
- API 测试使用临时文件，不污染真实 `data/student.json`。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。
- 没有提前实现学习笔记 API。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

`GET /profile` 和 `POST /profile` 是后续 AI 助手最基础的数据入口。

| 现在 | 后续升级 |
| --- | --- |
| `GET /profile` | LangChain 工具查询学员资料 |
| `POST /profile` | API 更新学习画像 |
| `load_student()` | 工具函数 / Graph 节点输入 |
| `save_student()` | API 写入 / 状态持久化 |
| `note_count` | 后续笔记 API 和 RAG 资料数量 |
| 保留 notes | 避免跨接口数据丢失 |

后面 LangChain Agent 查询学员情况时，不应该直接读用户输入。

它会通过工具或 API 获取结构化资料。

本课就是把“学习档案”变成 API 能管理的数据。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-3/03-03-profile-api.md`

修改文件：

- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_api.py`
- `ai-learning-assistant/README.md`
- `docs/tutorial/README.md`
- `README.md`

新增接口：

```http
GET /profile
POST /profile
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

- `GET /profile` 可以读取当前学员资料。
- `POST /profile` 可以保存学员资料。
- 更新资料时不会清空已有学习笔记。
- pytest 测试全部通过。
- Python 文件可以编译通过。

下一步：

- 第 3.4 课：学习笔记 API，新增 `GET /notes` 和 `POST /notes`。
