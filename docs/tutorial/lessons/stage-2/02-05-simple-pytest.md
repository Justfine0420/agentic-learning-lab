# 第 2.5 课：简单 pytest

## 1. 本课目标

第 2.4 课已经用 `TypedDict` 把 `Student` 数据结构表达清楚。

现在我们要给 `storage.py` 写最小单元测试。

本课目标不是一次讲完整测试体系，而是先让你掌握：

- 什么是单元测试。
- 如何安装 pytest。
- pytest 如何发现测试文件。
- 如何用普通 `assert` 写断言。
- 如何用临时目录测试文件读写。
- 为什么测试不能污染真实 `data/student.json`。

## 2. 你会新增什么项目能力

本课之后，项目会新增一个测试文件：

```text
ai-learning-assistant/tests/test_storage.py
```

它会验证：

- 文件不存在时返回默认学生资料。
- 保存后可以再读取回来。
- JSON 损坏时会备份坏文件。
- 字段缺失时会归一化。
- 带 UTF-8 BOM 的 JSON 可以读取。

从这节开始，项目不再只靠手动运行验证。

它有了第一批可重复执行的自动化测试。

## 3. 前置知识

开始前确认你已经理解：

- `storage.py` 负责 `load_student()` 和 `save_student()`。
- `data/student.json` 是运行时数据，不应该被提交。
- `Student` 是 `TypedDict`。
- `assert` 可以判断一个条件是否为真。
- `Path` 可以表示文件路径。

本课会第一次引入第三方开发依赖：`pytest`。

## 4. 核心概念

### 什么是单元测试

单元测试就是针对一个很小的功能写验证。

比如 `load_student()`：

- 输入：没有文件。
- 期望：返回默认学生资料。

再比如 `save_student()`：

- 输入：一个 `Student` 字典。
- 期望：写入 JSON 文件，并能读取回来。

### pytest 如何发现测试

pytest 默认会发现这样的测试文件：

```text
test_*.py
*_test.py
```

所以本课文件命名为：

```text
tests/test_storage.py
```

测试函数也用 `test_` 开头：

```python
def test_save_and_load_student_round_trip(tmp_path: Path) -> None:
```

### 普通 `assert`

pytest 可以直接使用 Python 的 `assert`：

```python
assert storage.load_student() == storage.create_default_student()
```

如果断言失败，pytest 会告诉你实际值和期望值哪里不同。

### 为什么测试用临时目录

不能让测试直接操作真实文件：

```text
data/student.json
```

否则测试会覆盖学习者自己的资料。

pytest 提供 `tmp_path`，每个测试都会得到一个临时目录。

本课用它来改写：

```python
storage.DATA_FILE = tmp_path / "student.json"
storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"
```

这样测试只操作临时文件。

## 5. 代码实现

### 第一步：更新 `requirements.txt`

打开：

```text
ai-learning-assistant/requirements.txt
```

写入：

```text
pytest>=8.0.0

# 后续课程会逐步加入 FastAPI、LangChain、LangGraph、Deep Agents 等依赖。
```

然后安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

### 第二步：新增 `tests/test_storage.py`

新增文件：

```text
ai-learning-assistant/tests/test_storage.py
```

写入：

```python
import json
from pathlib import Path

from app import storage
from app.models import Student


def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"


def test_load_student_returns_default_when_file_missing(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)

    assert storage.load_student() == storage.create_default_student()


def test_save_and_load_student_round_trip(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    student: Student = {
        "name": "Alice",
        "goal": "Learn pytest",
        "python_level": "beginner",
        "notes": ["Write storage tests"],
    }

    storage.save_student(student)

    assert storage.DATA_FILE.exists()
    assert storage.load_student() == student


def test_load_student_backs_up_broken_json(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.DATA_FILE.write_text("{ bad json", encoding="utf-8")

    assert storage.load_student() == storage.create_default_student()
    assert not storage.DATA_FILE.exists()
    assert storage.BROKEN_DATA_FILE.exists()
    assert storage.BROKEN_DATA_FILE.read_text(encoding="utf-8") == "{ bad json"


def test_load_student_normalizes_partial_data(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.DATA_FILE.write_text(
        json.dumps(
            {
                "name": "Carol",
                "notes": ["Only partial data", 123],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert storage.load_student() == {
        "name": "Carol",
        "goal": "",
        "python_level": "",
        "notes": ["Only partial data"],
    }


def test_load_student_accepts_utf8_bom(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.DATA_FILE.write_text(
        json.dumps(
            {
                "name": "Dora",
                "goal": "Read BOM",
                "python_level": "basic",
                "notes": ["UTF-8 with BOM"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8-sig",
    )

    assert storage.load_student()["name"] == "Dora"
```

### 第三步：运行测试

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
```

你应该看到类似输出：

```text
5 passed
```

### 第四步：语法检查

继续运行：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/__init__.py tests/test_storage.py
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

运行 CLI，确认真实项目仍可用：

```powershell
"2`n4" | py -3.13 -m app.main
```

## 7. 常见错误

### pytest 没安装

如果看到：

```text
No module named pytest
```

先运行：

```powershell
py -3.13 -m pip install -r requirements.txt
```

### 测试文件命名不对

pytest 默认会发现 `test_*.py`。

不要写成：

```text
storage_test_demo.py
```

本课使用：

```text
tests/test_storage.py
```

### 测试污染真实数据

不要在测试里直接写：

```python
Path("data/student.json").write_text(...)
```

本课用 `tmp_path` 创建临时文件，避免覆盖真实学习资料。

### 忘记断言

测试不是运行一下就算。

必须写出期望：

```python
assert storage.load_student() == student
```

## 8. 练习

练习 1：新增一个测试，验证 `notes` 为空列表时可以正常保存和读取。

练习 2：新增一个测试，验证 `load_student()` 遇到 JSON 数组时会返回默认学生资料。

练习 3：故意把 `storage.py` 里的 `ensure_ascii=False` 去掉，观察测试是否能发现问题。思考为什么。

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `requirements.txt` 包含 `pytest>=8.0.0`。
- `tests/test_storage.py` 存在。
- 至少覆盖文件不存在、保存读取、损坏 JSON、缺字段、UTF-8 BOM。
- 测试使用 `tmp_path`，不污染真实 `data/student.json`。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。
- CLI 仍能正常运行。
- 没有创建课程代码快照目录。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

测试会在后续变得更重要。

| 现在 | 后续升级 |
| --- | --- |
| `test_storage.py` | 测 API / RAG / Graph |
| `assert` | 验证结构化输出 |
| `tmp_path` | 隔离文件系统副作用 |
| 损坏 JSON 测试 | Agent 输出解析失败测试 |
| 存储 round trip | checkpoint 恢复测试 |

后面 LangGraph 会有节点、边、状态流转。

如果没有测试，你很难判断某个节点改动有没有破坏整个流程。

本课先从最稳定、最容易测试的存储模块开始。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-2/02-05-simple-pytest.md`
- `ai-learning-assistant/tests/test_storage.py`

修改文件：

- `.gitignore`
- `ai-learning-assistant/requirements.txt`
- `docs/tutorial/README.md`
- `README.md`
- `ai-learning-assistant/README.md`

新增依赖：

- `pytest>=8.0.0`

新增命令：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/__init__.py tests/test_storage.py
"2`n4" | py -3.13 -m app.main
```

验证结果：

- pytest 测试全部通过。
- Python 文件可以编译通过。
- CLI 仍能加载并展示当前学习档案。

下一步：

- Stage 2 的课程正文已经完成，但阶段复盘和 `stage-2` 归档暂缓。
