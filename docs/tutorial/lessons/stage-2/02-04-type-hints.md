# 第 2.4 课：类型标注

## 1. 本课目标

前面几课已经让项目具备了模块拆分、JSON 持久化和基础异常处理。

但代码里还有一个问题：`student` 这个字典到底应该长什么样，主要靠人脑记忆。

本课要把这个结构用类型标注明确写出来：

```python
class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]
```

你要掌握：

- 什么是类型标注。
- 什么是 `TypedDict`。
- 为什么 `dict` 太宽泛。
- 如何给函数参数和返回值补类型。
- 类型标注和 Pydantic / LangGraph State 的关系。

## 2. 你会新增什么项目能力

本课不会增加新的用户功能。

菜单、保存、加载、异常恢复都保持不变。

真正新增的是代码表达能力：

- `student` 的字段结构更清楚。
- `storage.py` 的函数返回值更明确。
- `student_state.py` 不再只是一个无类型字典。
- 后续迁移到 Pydantic Model 更顺。
- 后续定义 LangGraph State 更容易理解。

这一步是从“能跑”走向“能维护”的过渡。

## 3. 前置知识

开始前确认你已经理解：

- 字典可以保存多个字段。
- `student` 当前包含 `name`、`goal`、`python_level`、`notes`。
- `notes` 是字符串列表。
- 函数可以写返回值类型，比如 `-> None`。
- `storage.py` 负责读写学员数据。

本课不安装第三方依赖，不引入 Pydantic，不引入 mypy。

## 4. 核心概念

### 什么是类型标注

类型标注就是给变量、参数、返回值写清楚类型。

例如：

```python
name: str = "Alice"
notes: list[str] = ["JSON works"]
```

它不会把 Python 变成强制编译语言。

但它能帮助你和编辑器理解代码应该接收什么、返回什么。

### 为什么普通 `dict` 太宽泛

下面这个类型太模糊：

```python
def save_student(student: dict) -> None:
```

`dict` 只能说明它是一个字典。

它没有说明：

- 有没有 `name`。
- 有没有 `goal`。
- `notes` 是不是列表。
- 列表里是不是字符串。

所以本课会把它改成：

```python
def save_student(student: Student) -> None:
```

### 什么是 `TypedDict`

`TypedDict` 用来描述字典的固定结构。

本课新增：

```python
from typing import TypedDict


class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]
```

这不是类实例模型。

它仍然是普通字典，只是多了类型说明。

### 为什么现在不用 Pydantic

Pydantic 会在 FastAPI 阶段正式进入。

当前阶段先用标准库里的 `TypedDict`，因为它轻、简单、不需要安装依赖。

后面你会看到：

| 现在 | 后续 |
| --- | --- |
| `TypedDict` | Pydantic Model |
| `Student` | `StudentProfile` |
| `Student` | LangGraph `LearningState` |

## 5. 代码实现

### 第一步：新增 `app/models.py`

新增文件：

```text
ai-learning-assistant/app/models.py
```

写入：

```python
from typing import TypedDict


class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]
```

这个文件现在只放数据结构类型。

后面学习 FastAPI 时，这里会继续演进。

### 第二步：修改 `app/storage.py`

打开：

```text
ai-learning-assistant/app/storage.py
```

先导入类型：

```python
from app.models import Student
```

然后把默认数据和函数签名改清楚：

```python
DEFAULT_STUDENT: Student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}
```

```python
def create_default_student() -> Student:
```

```python
def normalize_student(data: object) -> Student:
```

```python
def load_student() -> Student:
```

```python
def save_student(student: Student) -> None:
```

完整文件应是：

```python
import json
from pathlib import Path

from app.models import Student


DATA_FILE = Path("data/student.json")
BROKEN_DATA_FILE = Path("data/student.broken.json")
DEFAULT_STUDENT: Student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}


def create_default_student() -> Student:
    return {
        "name": DEFAULT_STUDENT["name"],
        "goal": DEFAULT_STUDENT["goal"],
        "python_level": DEFAULT_STUDENT["python_level"],
        "notes": list(DEFAULT_STUDENT["notes"]),
    }


def is_valid_student(data: object) -> bool:
    if not isinstance(data, dict):
        return False

    required_keys = ("name", "goal", "python_level", "notes")
    if not all(key in data for key in required_keys):
        return False

    return (
        isinstance(data["name"], str)
        and isinstance(data["goal"], str)
        and isinstance(data["python_level"], str)
        and isinstance(data["notes"], list)
        and all(isinstance(note, str) for note in data["notes"])
    )


def normalize_student(data: object) -> Student:
    if not isinstance(data, dict):
        return create_default_student()

    student = create_default_student()

    if isinstance(data.get("name"), str):
        student["name"] = data["name"]
    if isinstance(data.get("goal"), str):
        student["goal"] = data["goal"]
    if isinstance(data.get("python_level"), str):
        student["python_level"] = data["python_level"]
    if isinstance(data.get("notes"), list):
        student["notes"] = [note for note in data["notes"] if isinstance(note, str)]

    return student


def backup_broken_data() -> None:
    if DATA_FILE.exists():
        DATA_FILE.replace(BROKEN_DATA_FILE)


def load_student() -> Student:
    if not DATA_FILE.exists():
        return create_default_student()

    try:
        with DATA_FILE.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        backup_broken_data()
        return create_default_student()
    except OSError:
        return create_default_student()

    if is_valid_student(data):
        return data

    return normalize_student(data)


def save_student(student: Student) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(student, file, ensure_ascii=False, indent=2)
```

### 第三步：修改 `app/student_state.py`

打开：

```text
ai-learning-assistant/app/student_state.py
```

改成：

```python
from app.models import Student
from app.storage import create_default_student


student: Student = create_default_student()


def replace_student(new_student: Student) -> None:
    student.clear()
    student.update(new_student)
```

现在 `student` 不再是一个模糊字典。

它是一个符合 `Student` 结构的字典。

### 第四步：确认 `app/cli.py`

`cli.py` 中多数函数已经有返回值标注：

```python
def show_header() -> None:
def ask_profile() -> None:
def add_note() -> None:
def show_profile() -> None:
def suggest_next_step() -> None:
def run_cli() -> None:
```

本课不需要重写 CLI 逻辑。

`student` 的类型来自：

```python
from app.student_state import replace_student, student
```

因为 `student_state.py` 已经写了：

```python
student: Student = create_default_student()
```

所以编辑器能推断出 `student` 的结构。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/__init__.py
```

运行 CLI：

```powershell
"2`n4" | py -3.13 -m app.main
```

你应该仍然能看到当前保存的学习档案。

如果本地没有数据文件，可以输入新的资料：

```powershell
"Alice`nLearn Type Hints`nbeginner`n4" | py -3.13 -m app.main
```

## 7. 常见错误

### 以为类型标注会自动校验运行时数据

`TypedDict` 主要给编辑器和静态检查工具看。

运行时仍然需要第 2.3 课里的 `is_valid_student()` 和 `normalize_student()`。

### 把 `Student` 写成普通类

本课不是这样写：

```python
class Student:
    ...
```

而是：

```python
class Student(TypedDict):
    ...
```

因为当前数据仍然是字典。

### 忘记导入 `TypedDict`

需要：

```python
from typing import TypedDict
```

### 继续使用 `dict`

能写：

```python
def save_student(student: dict) -> None:
```

但信息太少。

本课目标是写清楚：

```python
def save_student(student: Student) -> None:
```

### 误以为现在就要安装 mypy

本课不安装 mypy。

后续如果要做更严格的静态类型检查，可以再引入工具。

## 8. 练习

练习 1：在 `Student` 中临时新增一个字段：

```python
current_step: str
```

思考：`DEFAULT_STUDENT` 和 `create_default_student()` 需要同步改哪里？

练习 2：把 `save_student(student: Student)` 暂时改回 `dict`，观察代码可读性有什么变化。

练习 3：思考一个问题：为什么 `TypedDict` 很适合作为 LangGraph `State` 的前置理解？

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `app/models.py` 存在。
- `models.py` 中定义了 `Student(TypedDict)`。
- `Student` 包含 `name`、`goal`、`python_level`、`notes`。
- `notes` 的类型是 `list[str]`。
- `storage.py` 使用 `Student` 标注默认数据、返回值和参数。
- `student_state.py` 使用 `Student` 标注全局状态和替换函数。
- CLI 行为保持不变。
- 程序没有新增第三方依赖。
- 没有引入 mypy。
- 没有创建课程代码快照目录。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

类型标注会直接连接到后续框架。

| 现在 | 后续升级 |
| --- | --- |
| `Student(TypedDict)` | LangGraph `LearningState(TypedDict)` |
| `notes: list[str]` | RAG / Agent 可查询笔记 |
| `save_student(student: Student)` | 类型明确的工具函数 |
| `load_student() -> Student` | API / Graph / Agent 共享状态入口 |
| `TypedDict` | Pydantic Model 的前置理解 |

LangGraph 里最核心的概念之一就是 `State`。

它通常也会长这样：

```python
class LearningState(TypedDict):
    name: str
    python_level: str
    goal: str
    notes: list[str]
    current_step: str
```

也就是说，本课的 `Student` 就是未来 `LearningState` 的早期版本。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-2/02-04-type-hints.md`
- `ai-learning-assistant/app/models.py`

修改文件：

- `ai-learning-assistant/app/storage.py`
- `ai-learning-assistant/app/student_state.py`
- `docs/tutorial/README.md`
- `README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`

新增依赖：

- 无

新增命令：

- 无

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/__init__.py
"2`n4" | py -3.13 -m app.main
```

验证结果：

- Python 文件可以编译通过。
- CLI 仍能加载并展示当前学习档案。

下一课依赖：

- 第 2.5 课会进入简单 pytest，为 `storage.py` 写最小单元测试。
