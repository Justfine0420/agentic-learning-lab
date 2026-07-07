# 第 2.3 课：异常处理

## 1. 本课目标

第 2.2 课已经能把学员资料保存到 `data/student.json`。

但文件读写不是永远成功的。

真实程序至少会遇到这些情况：

- 文件不存在。
- JSON 文件内容损坏。
- JSON 能读取，但字段不完整。
- 字段类型不对，比如 `notes` 不是列表。
- 系统暂时无法读取文件。

本课目标是让存储逻辑更稳：

- 没有文件时使用默认空资料。
- JSON 损坏时不让程序崩溃。
- 损坏文件会备份成 `data/student.broken.json`。
- 字段缺失时补默认值。
- 字段类型不对时尽量恢复成安全结构。

你要掌握：

- 什么是异常。
- 如何用 `try/except` 捕获异常。
- 为什么要捕获具体异常，而不是乱写一个大 `except`。
- 如何做最小可用的数据校验。
- 为什么错误恢复要保护原始数据。

## 2. 你会新增什么项目能力

本课之后，`AI 学习助教` 的本地存储会更稳定。

它可以处理这些情况：

| 情况 | 程序行为 |
| --- | --- |
| `data/student.json` 不存在 | 使用默认空资料 |
| JSON 文件格式损坏 | 备份损坏文件，使用默认空资料 |
| JSON 缺少字段 | 补默认字段 |
| `notes` 中混入非字符串 | 只保留字符串笔记 |
| 文件读取出现系统错误 | 使用默认空资料 |

这不是完整的数据治理。

但对当前阶段已经足够：程序不应该因为一个坏 JSON 文件直接启动失败。

## 3. 前置知识

开始前确认你已经理解：

- `json.load()` 会读取 JSON 文件。
- `json.dump()` 会写入 JSON 文件。
- `student` 应该包含 `name`、`goal`、`python_level`、`notes`。
- `notes` 应该是字符串列表。
- `Path("data/student.json")` 指向本地数据文件。

本课仍不安装第三方依赖，不引入 pytest，不做数据库。

## 4. 核心概念

### 什么是异常

异常就是程序运行时发生的错误状态。

例如 JSON 文件损坏：

```json
{ bad json
```

这时运行：

```python
json.load(file)
```

会抛出 `json.JSONDecodeError`。

如果不处理，程序会直接退出并显示报错。

### `try/except`

`try/except` 用来捕获异常：

```python
try:
    data = json.load(file)
except json.JSONDecodeError:
    return create_default_student()
```

含义是：

- 先尝试执行 `try` 里的代码。
- 如果发生 `JSONDecodeError`，就执行 `except` 里的恢复逻辑。

### 不要乱捕获所有异常

不建议一开始就写：

```python
except Exception:
    return create_default_student()
```

这会把很多真正需要排查的问题也吞掉。

本课先处理两个明确场景：

- `json.JSONDecodeError`：JSON 格式损坏。
- `OSError`：文件读取层面的系统错误。

### 数据校验

JSON 能读取，不代表内容一定符合程序需要。

例如：

```json
{
  "name": "Alice",
  "notes": "not a list"
}
```

这不是坏 JSON，但它不是有效的学员资料。

所以本课会增加：

```python
def is_valid_student(data: object) -> bool:
    ...
```

用来判断数据结构是否完整。

### 数据归一化

如果数据只是缺几个字段，直接丢弃有点粗暴。

例如：

```json
{
  "name": "Alice",
  "notes": ["JSON saves dictionaries"]
}
```

这种文件还能恢复出一部分信息。

本课会增加：

```python
def normalize_student(data: object) -> dict:
    ...
```

它会用默认资料打底，再把合法字段补进去。

## 5. 代码实现

打开：

```text
ai-learning-assistant/app/storage.py
```

改成：

```python
import json
from pathlib import Path


DATA_FILE = Path("data/student.json")
BROKEN_DATA_FILE = Path("data/student.broken.json")
DEFAULT_STUDENT = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}


def create_default_student() -> dict:
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


def normalize_student(data: object) -> dict:
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


def load_student() -> dict:
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


def save_student(student: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(student, file, ensure_ascii=False, indent=2)
```

### 新增了什么

新增损坏文件备份路径：

```python
BROKEN_DATA_FILE = Path("data/student.broken.json")
```

新增结构校验：

```python
def is_valid_student(data: object) -> bool:
```

新增数据归一化：

```python
def normalize_student(data: object) -> dict:
```

新增损坏文件备份：

```python
def backup_broken_data() -> None:
```

增强了加载逻辑：

```python
try:
    with DATA_FILE.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
except json.JSONDecodeError:
    backup_broken_data()
    return create_default_student()
except OSError:
    return create_default_student()
```

### 为什么损坏文件要备份

如果 JSON 损坏后直接覆盖，学习者可能失去排查机会。

备份成：

```text
data/student.broken.json
```

至少还能打开看看原文件坏在哪里。

`data/student.broken.json` 也是本地运行数据，和 `data/student.json` 一样不提交到仓库。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

### 为什么读取时使用 `utf-8-sig`

PowerShell 的 `Set-Content -Encoding UTF8` 在一些环境里会写入 UTF-8 BOM。

如果用普通 `utf-8` 读取，`json.load()` 可能把 BOM 当成多余字符，导致解析失败。

所以本课把读取编码改成：

```python
encoding="utf-8-sig"
```

它既能读取普通 UTF-8，也能兼容带 BOM 的 UTF-8 文件。

写文件仍然使用：

```python
encoding="utf-8"
```

### 场景 1：正常 JSON 仍然可加载

先写入一份正常 JSON：

```powershell
@'
{
  "name": "Alice",
  "goal": "Learn Exceptions",
  "python_level": "beginner",
  "notes": [
    "JSON works"
  ]
}
'@ | Set-Content -Encoding UTF8 data/student.json
```

运行：

```powershell
"2`n4" | py -3.13 -m app.main
```

应该看到：

```text
已加载学习档案：Alice
1. JSON works
```

### 场景 2：JSON 损坏时不崩溃

写入坏 JSON：

```powershell
"{ bad json" | Set-Content -Encoding UTF8 data/student.json
```

运行：

```powershell
"Bob`nRecover JSON`nbeginner`n4" | py -3.13 -m app.main
```

程序应该不会崩溃，而是要求重新输入资料。

然后检查备份文件：

```powershell
Test-Path data/student.broken.json
```

应该输出：

```text
True
```

### 场景 3：字段缺失时补默认值

写入缺字段 JSON：

```powershell
@'
{
  "name": "Carol",
  "notes": [
    "Only partial data",
    123
  ]
}
'@ | Set-Content -Encoding UTF8 data/student.json
```

运行：

```powershell
"2`n4" | py -3.13 -m app.main
```

应该看到：

```text
已加载学习档案：Carol
目标：
Python 水平：
1. Only partial data
```

数字 `123` 不会作为笔记显示，因为笔记应该是字符串。

### 语法检查

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/__init__.py
```

## 7. 常见错误

### 只处理文件不存在

文件不存在不是唯一问题。

文件存在但内容损坏，才是 JSON 文件读写里更常见的坑。

### 捕获异常后什么都不做

错误写法：

```python
except json.JSONDecodeError:
    pass
```

这会让后续代码进入不确定状态。

至少要返回默认数据，或者备份损坏文件。

### 把所有异常都吞掉

不要一上来就写：

```python
except Exception:
    return create_default_student()
```

这样会隐藏很多真正的 bug。

### 不校验字段类型

只判断有没有 `notes` 不够。

还要判断它是不是列表，列表里是不是字符串。

### 恢复时直接清空原文件

坏文件也可能包含有价值的信息。

先备份，再恢复默认状态，更稳。

## 8. 练习

练习 1：手动把 `data/student.json` 改成一个 JSON 列表：

```json
["not", "a", "student"]
```

运行程序，观察是否回到默认空资料。

练习 2：把 `notes` 改成：

```json
["valid note", 123, true]
```

观察程序是否只保留字符串笔记。

练习 3：尝试删掉 `goal` 和 `python_level`，观察展示结果。

练习 4：思考一个问题：为什么 `normalize_student()` 不直接修改原始 `data`？

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `load_student()` 能处理文件不存在。
- `load_student()` 能处理损坏 JSON。
- 损坏 JSON 会备份到 `data/student.broken.json`。
- `data/student.broken.json` 和 `data/student.json` 一样是本地运行数据，不提交到仓库。
- JSON 字段缺失时能补默认值。
- `notes` 只保留字符串。
- 正常 JSON 仍然能正确加载。
- 程序没有新增第三方依赖。
- 没有引入 pytest。
- 没有创建课程代码快照目录。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

异常处理不是补丁，而是 Agent 系统的基础能力。

| 现在 | 后续升级 |
| --- | --- |
| `try/except` | 工具调用失败兜底 |
| `JSONDecodeError` | 外部响应解析失败 |
| `normalize_student()` | 结构化输出校验 |
| 备份损坏文件 | 保留失败现场 |
| 默认状态恢复 | LangGraph 节点失败恢复 |

后面接入 LLM 后，模型输出不一定总是符合预期。

后面接入 LangGraph 后，某个节点也可能失败。

本课先用最小的文件读写场景，让你理解一件事：系统要能承认失败，并把失败变成可恢复状态。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-2/02-03-exception-handling.md`

修改文件：

- `ai-learning-assistant/app/storage.py`
- `.gitignore`
- `docs/tutorial/README.md`
- `README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`

新增依赖：

- 无

新增命令：

```powershell
Set-Content -Encoding UTF8 data/student.json
Test-Path data/student.broken.json
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
@'
{
  "name": "Alice",
  "goal": "Learn Exceptions",
  "python_level": "beginner",
  "notes": [
    "JSON works"
  ]
}
'@ | Set-Content -Encoding UTF8 data/student.json
"2`n4" | py -3.13 -m app.main

"{ bad json" | Set-Content -Encoding UTF8 data/student.json
"Bob`nRecover JSON`nbeginner`n4" | py -3.13 -m app.main
Test-Path data/student.broken.json

@'
{
  "name": "Carol",
  "notes": [
    "Only partial data",
    123
  ]
}
'@ | Set-Content -Encoding UTF8 data/student.json
"2`n4" | py -3.13 -m app.main

py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/__init__.py
```

验证结果：

- 正常 JSON 能加载 `Alice` 和 `JSON works`。
- 损坏 JSON 不会导致程序崩溃。
- 损坏 JSON 会生成 `data/student.broken.json`。
- 缺字段 JSON 能加载 `Carol`。
- 非字符串笔记 `123` 不会显示。

下一课依赖：

- 第 2.4 课会学习类型标注，把当前字典结构表达得更清楚，为 Pydantic 和 LangGraph State 铺路。
