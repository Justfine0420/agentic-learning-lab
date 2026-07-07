# 第 2.1 课：模块拆分

## 1. 本课目标

Stage 1 结束时，你已经做出了一个可用的 CLI 学习助手。

但所有代码都堆在 `app/main.py` 里。这个阶段刚开始还没问题，后面要加入 JSON 文件读写、FastAPI、LangChain、LangGraph 和测试时，一个文件会越来越难维护。

本课目标是把代码拆成多个模块：

- `main.py` 只负责启动程序。
- `cli.py` 负责命令行交互。
- `student_state.py` 负责保存当前学习状态。
- `__init__.py` 让 `app/` 成为一个可导入的 Python 包。

你要掌握：

- 什么是 Python 模块。
- 什么是 Python 包。
- 为什么入口文件不应该塞满业务逻辑。
- 如何用 `from app.cli import run_cli` 导入函数。
- 为什么从本课开始推荐使用 `py -3.13 -m app.main` 运行项目。

## 2. 你会新增什么项目能力

本课不会增加新的用户功能。

菜单能力仍然是：

```text
1. 添加学习笔记
2. 查看学习信息
3. 生成今日学习建议
4. 退出
```

真正新增的是工程能力：

- 代码结构更清楚。
- CLI 逻辑可以独立维护。
- 状态对象有了独立位置。
- 后续 JSON 保存可以接到 `student_state.py` 或新的存储模块。
- 后续 FastAPI 可以复用状态和业务函数，而不是复制 CLI 代码。
- 后续测试可以按模块导入函数。

这就是 Python 工程化的第一步：不是写更多代码，而是把已经存在的代码放到更合适的位置。

## 3. 前置知识

开始前确认你已经理解：

- `student` 字典保存学员状态。
- 函数可以把一段行为封装起来。
- `main()` 是上一阶段的程序入口。
- `while True` 菜单会持续运行程序。
- `if __name__ == "__main__"` 可以让文件被直接运行时才启动主逻辑。

本课仍不安装第三方依赖，不读写文件，不调用 AI。

## 4. 核心概念

### 什么是模块

一个 `.py` 文件就是一个模块。

比如：

```text
cli.py
student_state.py
main.py
```

每个文件都应该有清楚职责。

如果一个文件什么都管，就会很快变成“谁也不敢动”的文件。

### 什么是包

带有 `__init__.py` 的目录可以作为 Python 包使用。

本课会新增：

```text
app/__init__.py
```

这样后续就可以写：

```python
from app.cli import run_cli
from app.student_state import student
```

这种写法比在文件之间临时互相找路径更稳定。

### 入口文件应该很薄

上一课的 `main.py` 既保存状态，又定义函数，又运行菜单。

本课之后，`main.py` 只剩：

```python
from app.cli import run_cli


if __name__ == "__main__":
    run_cli()
```

这叫入口文件变薄。

入口文件只负责启动，具体功能交给其它模块。

### 为什么运行命令要改

上一阶段推荐：

```powershell
py -3.13 app/main.py
```

从本课开始推荐：

```powershell
py -3.13 -m app.main
```

`-m app.main` 表示按模块运行 `app.main`。

这样 Python 会从项目根目录识别 `app` 包，`from app.cli import run_cli` 这类导入更稳定。

### 本课为什么不提前写 `storage.py`

课程总纲里提到 Stage 2 会有 `storage.py`。

但本课只做模块拆分，数据还没有保存到文件。提前创建空的 `storage.py` 只会让学习者困惑。

第 2.2 课学习 JSON 文件读写时，再创建真正有用的存储模块。

## 5. 代码实现

### 第一步：新增 `app/__init__.py`

新增文件：

```text
ai-learning-assistant/app/__init__.py
```

写入：

```python
"""AI learning assistant application package."""
```

这个文件现在没有业务逻辑。它的作用是告诉 Python：`app/` 是一个包。

### 第二步：新增 `app/student_state.py`

新增文件：

```text
ai-learning-assistant/app/student_state.py
```

写入：

```python
student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}
```

这部分就是上一阶段 `main.py` 里的状态字典。

现在它被单独放到一个模块里，后续会继续升级。

### 第三步：新增 `app/cli.py`

新增文件：

```text
ai-learning-assistant/app/cli.py
```

写入：

```python
from app.student_state import student


PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 2"


def show_header() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")


def ask_profile() -> None:
    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")


def add_note() -> None:
    note = input("请输入一条学习笔记：")
    student["notes"].append(note)
    print("已保存。")


def show_profile() -> None:
    print()
    print("=== 学习档案 ===")
    print(f"名字：{student['name']}")
    print(f"目标：{student['goal']}")
    print(f"Python 水平：{student['python_level']}")

    print()
    print("=== 学习笔记 ===")
    if len(student["notes"]) == 0:
        print("暂无笔记")
    else:
        for index, saved_note in enumerate(student["notes"], start=1):
            print(f"{index}. {saved_note}")


def suggest_next_step() -> None:
    print()
    print("=== 今日学习建议 ===")

    if student["python_level"] == "beginner":
        print("建议：今天学习变量、函数、字典。")
    elif student["python_level"] == "basic":
        print("建议：今天学习类、文件读写、异常处理。")
    else:
        print("建议：今天开始学习 LangChain 的 agent。")


def run_cli() -> None:
    show_header()
    ask_profile()

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
            print(f"{student['name']}，下次继续学习。")
            break
        else:
            print("无效选项，请重新输入。")
```

注意这里的入口函数叫 `run_cli()`，不再叫 `main()`。

原因很简单：这个模块负责 CLI，所以函数名应该说明它在运行 CLI。

### 第四步：改造 `app/main.py`

打开：

```text
ai-learning-assistant/app/main.py
```

把它改成：

```python
from app.cli import run_cli


if __name__ == "__main__":
    run_cli()
```

现在 `main.py` 不再关心学员字典、菜单、建议规则。

它只负责启动 CLI。

### 最终目录结构

本课结束后，`app/` 目录应变成：

```text
app/
├── __init__.py
├── cli.py
├── main.py
└── student_state.py
```

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

从本课开始，推荐使用模块方式运行：

```powershell
py -3.13 -m app.main
```

可以按这个顺序输入：

```text
请输入你的名字：Alice
请输入你的学习目标：Learn Python Modules
请输入你的 Python 水平 beginner / basic / intermediate：beginner
输入选项：2
输入选项：1
请输入一条学习笔记：Split modules
输入选项：2
输入选项：3
输入选项：9
输入选项：4
```

你应该看到这些关键输出：

```text
Current stage: Stage 2
暂无笔记
已保存。
1. Split modules
建议：今天学习变量、函数、字典。
无效选项，请重新输入。
Alice，下次继续学习。
```

还可以做一次语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/__init__.py
```

## 7. 常见错误

### 仍然用旧命令运行

从本课开始不要优先使用：

```powershell
py -3.13 app/main.py
```

推荐使用：

```powershell
py -3.13 -m app.main
```

这样导入路径会按包结构工作。

### 忘记新增 `__init__.py`

如果没有 `app/__init__.py`，某些运行环境里 `app` 包的行为会不够明确。

本课直接加上它，避免后面测试和服务启动时踩坑。

### 把 `student` 又复制了一份

不要在 `cli.py` 里重新写一遍：

```python
student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}
```

应该从 `student_state.py` 导入：

```python
from app.student_state import student
```

复制状态会导致后面出现“这个模块改了，另一个模块没变”的问题。

### 在 `student_state.py` 里写输入输出逻辑

`student_state.py` 只保存状态。

不要把 `input()`、`print()`、菜单循环写进去。

输入输出逻辑属于 `cli.py`。

## 8. 练习

练习 1：新增一个文件：

```text
app/suggestion.py
```

把 `suggest_next_step()` 移进去。

然后在 `cli.py` 中导入它：

```python
from app.suggestion import suggest_next_step
```

练习 2：把 `PROJECT_NAME` 和 `COURSE_STAGE` 移到一个新文件：

```text
app/config.py
```

然后在 `cli.py` 中导入。

练习 3：思考一个问题：如果以后 FastAPI 也要生成学习建议，它应该直接调用 `cli.py` 里的函数吗？为什么？

练习完成后，建议把代码恢复到课程版本。后续课程会按当前结构继续推进。

## 9. 验收标准

本课完成时，应满足：

- `app/__init__.py` 存在。
- `app/student_state.py` 中保存 `student` 字典。
- `app/cli.py` 中包含 CLI 输入输出、菜单循环和学习建议规则。
- `app/main.py` 只导入并调用 `run_cli()`。
- 使用 `py -3.13 -m app.main` 可以正常运行。
- 添加笔记、查看资料、生成建议、无效选项、退出都仍然正常。
- 程序没有新增第三方依赖。
- 程序仍然不保存 JSON 文件。
- 没有创建课程代码快照目录。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

模块拆分会影响后面所有框架学习。

| 现在 | 后续升级 |
| --- | --- |
| `student_state.py` | Pydantic Model / LangGraph State |
| `cli.py` | FastAPI 路由之外的命令行入口 |
| `run_cli()` | CLI 启动器 |
| `main.py` | 项目入口 |
| `from app... import ...` | 测试、API、Agent、Graph 复用同一套代码 |

LangChain、LangGraph 和 Deep Agents 都会要求你把功能拆成可复用的小块。

如果所有逻辑都写在一个文件里，后面会变成：

- 工具函数不好导入。
- API 路由容易复制代码。
- LangGraph 节点不好测试。
- Deep Agents 生成文件时难以复用已有能力。

本课就是提前把工程地基打好。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-2/02-01-module-split.md`
- `ai-learning-assistant/app/__init__.py`
- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/app/student_state.py`

修改文件：

- `ai-learning-assistant/app/main.py`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`
- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `docs/tutorial/README.md`
- `README.md`
- `ai-learning-assistant/README.md`

新增依赖：

- 无

新增命令：

```powershell
py -3.13 -m app.main
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/__init__.py
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
"Alice`nLearn Python Modules`nbeginner`n2`n1`nSplit modules`n2`n3`n9`n4" | py -3.13 -m app.main
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/__init__.py
```

验证结果：

- CLI 输出 `Current stage: Stage 2`。
- 首次查看资料时输出 `暂无笔记`。
- 添加笔记后输出 `已保存。`。
- 再次查看资料时输出 `1. Split modules`。
- 生成建议时输出 `建议：今天学习变量、函数、字典。`。
- 输入 `9` 时输出 `无效选项，请重新输入。`。
- 输入 `4` 时程序退出。

下一课依赖：

- 第 2.2 课会学习 JSON 文件读写，把当前内存里的 `student` 保存到本地文件。
