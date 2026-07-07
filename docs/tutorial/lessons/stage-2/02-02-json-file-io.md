# 第 2.2 课：JSON 文件读写

## 1. 本课目标

第 2.1 课已经把 CLI、入口和状态拆成了不同模块。

但程序还有一个明显问题：退出后，学员资料和学习笔记会丢失。

本课要把内存里的 `student` 字典保存到本地 JSON 文件：

```text
ai-learning-assistant/data/student.json
```

你要掌握：

- 什么是 JSON。
- 为什么字典和 JSON 很适合互相转换。
- 如何用 `json.load()` 读取文件。
- 如何用 `json.dump()` 写入文件。
- 如何用 `Path` 管理文件路径。
- 为什么运行生成的数据文件不提交到 Git。

## 2. 你会新增什么项目能力

本课之后，`AI 学习助教` 会具备最小持久化能力：

- 第一次运行时输入学员资料。
- 添加学习笔记后自动保存。
- 退出程序前保存当前状态。
- 第二次运行时自动加载上次保存的学习档案。
- 查看学习信息时能看到上次保存的笔记。

这一步很关键。

从现在开始，项目不再只是“运行时临时状态”，而是有了本地数据。

## 3. 前置知识

开始前确认你已经理解：

- `student` 是一个字典。
- `student["notes"]` 是一个列表。
- 模块之间可以用 `from app.xxx import yyy` 导入函数或变量。
- `data/` 目录用于保存本地数据。
- 当前推荐运行命令是 `py -3.13 -m app.main`。

本课仍不安装第三方依赖，不调用 AI，不做完整异常处理。

完整的文件不存在、JSON 损坏等异常处理会放到第 2.3 课。

## 4. 核心概念

### 什么是 JSON

JSON 是一种常见的数据文本格式。

Python 字典：

```python
student = {
    "name": "Alice",
    "goal": "Learn Python",
    "python_level": "beginner",
    "notes": ["Split modules"],
}
```

保存成 JSON 后大概长这样：

```json
{
  "name": "Alice",
  "goal": "Learn Python",
  "python_level": "beginner",
  "notes": [
    "Split modules"
  ]
}
```

它适合用来保存课程早期的小规模结构化数据。

### `json.dump()`

`json.dump()` 把 Python 对象写进文件：

```python
json.dump(student, file, ensure_ascii=False, indent=2)
```

这里有两个参数很重要：

- `ensure_ascii=False`：让中文直接写成中文，而不是转义编码。
- `indent=2`：让 JSON 文件有缩进，方便阅读。

### `json.load()`

`json.load()` 从文件里读出 Python 对象：

```python
student = json.load(file)
```

读出来的数据会重新变成字典和列表。

### 为什么用 `Path`

本课会使用：

```python
from pathlib import Path

DATA_FILE = Path("data/student.json")
```

`Path` 比直接拼字符串更适合处理文件路径。

后面项目变复杂时，`Path` 会比手写 `"data/student.json"` 更容易扩展。

### 为什么不提交 `student.json`

`data/student.json` 是运行程序时生成的个人学习数据。

每个学习者输入的名字、目标、笔记都不同。

所以它应该留在本地，不提交进仓库。

本课会把它写进 `.gitignore`：

```text
ai-learning-assistant/data/student.json
```

仓库里继续保留 `data/.gitkeep`，用来保留空目录结构。

## 5. 代码实现

### 第一步：新增 `app/storage.py`

新增文件：

```text
ai-learning-assistant/app/storage.py
```

写入：

```python
import json
from pathlib import Path


DATA_FILE = Path("data/student.json")
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


def load_student() -> dict:
    if not DATA_FILE.exists():
        return create_default_student()

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_student(student: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(student, file, ensure_ascii=False, indent=2)
```

这个文件只负责存储。

它不应该出现 `input()`、`print()`、菜单循环。

### 第二步：修改 `app/student_state.py`

打开：

```text
ai-learning-assistant/app/student_state.py
```

改成：

```python
from app.storage import create_default_student


student = create_default_student()


def replace_student(new_student: dict) -> None:
    student.clear()
    student.update(new_student)
```

这里的重点是 `replace_student()`。

它不是直接写：

```python
student = new_student
```

而是：

```python
student.clear()
student.update(new_student)
```

这样做的原因是：其它模块已经导入了同一个 `student` 字典。清空再更新，可以让大家继续使用同一个字典对象。

### 第三步：修改 `app/cli.py`

打开：

```text
ai-learning-assistant/app/cli.py
```

先修改导入：

```python
from app.storage import load_student, save_student
from app.student_state import replace_student, student
```

然后在 `ask_profile()` 保存资料：

```python
def ask_profile() -> None:
    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")
    save_student(student)
```

在 `add_note()` 保存笔记：

```python
def add_note() -> None:
    note = input("请输入一条学习笔记：")
    student["notes"].append(note)
    save_student(student)
    print("已保存。")
```

最后修改 `run_cli()`：

```python
def run_cli() -> None:
    show_header()
    replace_student(load_student())

    if student["name"] == "":
        ask_profile()
    else:
        print(f"已加载学习档案：{student['name']}")

    while True:
        print()
        print("请选择操作：")
        print("1. 添加学习笔记")
        print("2. 查看学习信息")
        print("3. 生成今日学习建议")
        print("4. 退出")

        choice = input("输入选项：")

        if choice == "1":
            add_note()
        elif choice == "2":
            show_profile()
        elif choice == "3":
            suggest_next_step()
        elif choice == "4":
            save_student(student)
            print(f"{student['name']}，下次继续学习。")
            break
        else:
            print("无效选项，请重新输入。")
```

现在程序启动时会先读文件。

如果没有保存过资料，才会要求输入学员资料。

### 第四步：修改 `.gitignore`

打开根目录：

```text
.gitignore
```

加入：

```text
ai-learning-assistant/data/student.json
```

这样运行生成的学习数据不会被提交。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

为了验证持久化，先删除本地旧数据：

```powershell
if (Test-Path data/student.json) { Remove-Item data/student.json }
```

第一次运行：

```powershell
py -3.13 -m app.main
```

输入示例：

```text
请输入你的名字：Alice
请输入你的学习目标：Learn JSON
请输入你的 Python 水平 beginner / basic / intermediate：beginner
输入选项：1
请输入一条学习笔记：JSON saves dictionaries
输入选项：4
```

检查文件内容：

```powershell
Get-Content -Raw data/student.json
```

你应该能看到 `Alice`、`Learn JSON` 和 `JSON saves dictionaries`。

第二次运行：

```powershell
py -3.13 -m app.main
```

这次不应该再要求输入名字，而是输出：

```text
已加载学习档案：Alice
```

选择 `2` 查看学习信息，应能看到上次保存的笔记。

## 7. 常见错误

### 忘记 `encoding="utf-8"`

读写中文内容时，建议明确写：

```python
DATA_FILE.open("w", encoding="utf-8")
```

不要依赖系统默认编码。

### 忘记 `ensure_ascii=False`

如果没有这个参数，中文可能会保存成转义形式。

正确写法：

```python
json.dump(student, file, ensure_ascii=False, indent=2)
```

### 直接替换 `student` 变量

不要在 `student_state.py` 里写：

```python
student = new_student
```

这样可能让其它模块还拿着旧字典。

本课使用：

```python
student.clear()
student.update(new_student)
```

### 把 `data/student.json` 提交到仓库

`student.json` 是本地运行数据，不是课程代码。

它应该被 `.gitignore` 忽略。

### 把异常处理写得太复杂

本课只讲 JSON 文件读写。

文件损坏、JSON 格式错误、字段缺失等情况，会在第 2.3 课集中处理。

## 8. 练习

练习 1：打开 `data/student.json`，观察 `notes` 列表是如何保存的。

练习 2：手动把 `notes` 里的内容改成两条，再运行程序查看学习信息。

练习 3：在 `save_student()` 里暂时去掉 `indent=2`，比较保存后的 JSON 可读性。

练习 4：思考一个问题：为什么 `storage.py` 不应该直接调用 `input()`？

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `app/storage.py` 存在。
- `storage.py` 中包含 `load_student()` 和 `save_student()`。
- `data/student.json` 不存在时，程序能使用默认空资料启动。
- 输入学员资料后会生成 `data/student.json`。
- 添加学习笔记后会写入 JSON 文件。
- 第二次运行程序时会加载上次保存的资料。
- `data/student.json` 被 `.gitignore` 忽略。
- 程序没有新增第三方依赖。
- 没有创建课程代码快照目录。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

JSON 持久化是后续很多能力的前置理解。

| 现在 | 后续升级 |
| --- | --- |
| `data/student.json` | 数据库 / checkpoint / 文件系统 |
| `load_student()` | API 查询资料 / Agent 工具查询资料 |
| `save_student()` | API 更新资料 / Deep Agents 写文件 |
| JSON 文件 | LangGraph checkpoint 的前置理解 |
| 本地状态恢复 | 可恢复学习会话 |

后面学习 LangGraph checkpoint 时，你会发现它解决的问题和本课类似：

- 当前状态是什么。
- 状态保存在哪里。
- 下次运行时如何恢复。

只是 LangGraph 会把这个问题放到更复杂的流程状态里。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-2/02-02-json-file-io.md`
- `ai-learning-assistant/app/storage.py`

修改文件：

- `.gitignore`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`
- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/app/student_state.py`
- `docs/tutorial/lessons/stage-1/01-06-loop-menu.md`
- `docs/tutorial/reviews/stage-1-review.md`
- `docs/tutorial/README.md`
- `README.md`
- `ai-learning-assistant/README.md`

新增依赖：

- 无

新增命令：

```powershell
if (Test-Path data/student.json) { Remove-Item data/student.json }
Get-Content -Raw data/student.json
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
if (Test-Path data/student.json) { Remove-Item data/student.json }
"Alice`nLearn JSON`nbeginner`n1`nJSON saves dictionaries`n4" | py -3.13 -m app.main
Get-Content -Raw data/student.json
"2`n4" | py -3.13 -m app.main
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/__init__.py
```

验证结果：

- 第一次运行会生成 `data/student.json`。
- JSON 文件包含 `Alice`、`Learn JSON` 和 `JSON saves dictionaries`。
- 第二次运行会输出 `已加载学习档案：Alice`。
- 第二次选择 `2` 能看到上次保存的笔记。

下一课依赖：

- 第 2.3 课会处理文件不存在、JSON 损坏、字段缺失等异常情况，让存储逻辑更稳。
