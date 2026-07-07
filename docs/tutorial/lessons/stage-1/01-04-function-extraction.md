# 第 1.4 课：函数拆分

## 1. 本课目标

上一课你已经能用字典和列表保存学员资料与学习笔记。

这一课不新增业务功能，而是把 `main()` 里堆在一起的代码拆成多个函数，让程序开始变得可维护。

你要掌握：

- 什么是函数。
- 如何用 `def` 定义函数。
- 如何调用函数。
- 为什么一个函数最好只负责一件事。
- 为什么后续 LangChain Tool、FastAPI route、LangGraph node 都可以从函数开始理解。

## 2. 你会新增什么项目能力

本课之后，`AI 学习助教` 的功能会被拆成几个清晰的小块：

```python
show_header()
ask_profile()
add_note()
show_profile()
```

程序的用户体验和上一课保持一致：

- 仍然输入名字、学习目标、Python 水平。
- 仍然输入一条学习笔记。
- 仍然打印学习档案和学习笔记。

变化在代码内部：`main()` 不再塞满细节，而是像一个流程目录。

## 3. 前置知识

开始前确认你已经理解：

- 第 1.2 课的 `student` 字典。
- 第 1.3 课的 `student["notes"]` 列表。
- `input()` 会返回用户输入的字符串。
- `print()` 会把内容输出到命令行。
- `for` 可以遍历 `student["notes"]`。

本课暂不引入参数、返回值、类、文件保存、循环菜单或条件建议。

## 4. 核心概念

### 函数是什么

函数是一段被命名的代码。

例如：

```python
def show_header() -> None:
    print("Project: AI Learning Assistant")
```

这段代码定义了一个叫 `show_header` 的函数。

定义函数不会立刻执行函数里的代码。要执行它，需要调用：

```python
show_header()
```

### `def`

`def` 用来定义函数：

```python
def ask_profile() -> None:
    student["name"] = input("请输入你的名字：")
```

这一行包含几个部分：

- `def`：告诉 Python 这里要定义函数。
- `ask_profile`：函数名。
- `()`：暂时没有参数。
- `-> None`：表示这个函数不返回结果。
- `:`：函数体开始。
- 缩进代码：属于这个函数。

### 为什么要拆函数

第 1.3 课里，`main()` 同时负责：

- 打印项目标题。
- 收集学员资料。
- 添加学习笔记。
- 展示学习档案。
- 展示学习笔记。

代码短的时候还能看。后面加入菜单、条件建议、文件保存、API 和 AI 调用之后，如果所有代码都堆在 `main()`，你会很难知道哪段代码负责什么。

拆函数的目的不是炫技，而是让职责清楚。

### 函数名要表达职责

好的函数名应该能直接说明它做什么：

```python
ask_profile()
add_note()
show_profile()
```

不好的函数名：

```python
do_stuff()
handle()
run_task()
```

这类名字太泛，读代码时还要进去猜。

### 调用顺序

函数定义好以后，`main()` 负责组织调用顺序：

```python
def main() -> None:
    show_header()
    ask_profile()
    add_note()
    show_profile()
```

这像一个流程表：

1. 显示标题。
2. 收集资料。
3. 添加笔记。
4. 展示结果。

## 5. 代码实现

打开：

```text
ai-learning-assistant/app/main.py
```

改成：

```python
PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 1"

student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}


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


def show_profile() -> None:
    print()
    print("=== 学习档案 ===")
    print(f"名字：{student['name']}")
    print(f"目标：{student['goal']}")
    print(f"Python 水平：{student['python_level']}")

    print()
    print("=== 学习笔记 ===")
    for index, saved_note in enumerate(student["notes"], start=1):
        print(f"{index}. {saved_note}")


def main() -> None:
    show_header()
    ask_profile()
    add_note()
    show_profile()
    print(f"{student['name']}，欢迎开始你的 AI 学习助教项目。")


if __name__ == "__main__":
    main()
```

本课最重要的变化是：

```python
def ask_profile() -> None:
    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")
```

以及：

```python
def main() -> None:
    show_header()
    ask_profile()
    add_note()
    show_profile()
```

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

运行：

```powershell
py -3.13 app/main.py
```

按提示输入：

```text
请输入你的名字：小明
请输入你的学习目标：学习 Python 函数
请输入你的 Python 水平 beginner / basic / intermediate：beginner
请输入一条学习笔记：函数可以让代码职责更清楚
```

你应该看到类似输出：

```text
Project: AI Learning Assistant
Current stage: Stage 1
请输入你的名字：小明
请输入你的学习目标：学习 Python 函数
请输入你的 Python 水平 beginner / basic / intermediate：beginner
请输入一条学习笔记：函数可以让代码职责更清楚

=== 学习档案 ===
名字：小明
目标：学习 Python 函数
Python 水平：beginner

=== 学习笔记 ===
1. 函数可以让代码职责更清楚
小明，欢迎开始你的 AI 学习助教项目。
```

## 7. 常见错误

### 只定义函数，忘记调用

错误写法：

```python
def ask_profile() -> None:
    student["name"] = input("请输入你的名字：")
```

如果后面没有调用：

```python
ask_profile()
```

函数里的代码不会执行。

### 缩进错误

错误写法：

```python
def add_note() -> None:
note = input("请输入一条学习笔记：")
student["notes"].append(note)
```

函数体必须缩进：

```python
def add_note() -> None:
    note = input("请输入一条学习笔记：")
    student["notes"].append(note)
```

### 在函数名后面漏掉括号

错误写法：

```python
ask_profile
```

这只是拿到函数本身，没有执行函数。

正确写法：

```python
ask_profile()
```

### 把所有代码都拆得太碎

拆函数不是越多越好。

本课只按明确职责拆：

- 显示标题。
- 收集资料。
- 添加笔记。
- 展示资料。

如果每一行都拆成一个函数，代码反而更难读。

## 8. 练习

练习 1：新增一个函数：

```python
def show_goodbye() -> None:
    print("下次继续学习。")
```

然后在 `main()` 的最后调用它。

练习 2：把 `show_profile()` 里的学习笔记展示部分拆成：

```python
def show_notes() -> None:
    ...
```

再让 `show_profile()` 调用 `show_notes()`。

练习 3：故意把 `add_note()` 的调用删掉，观察程序是否还会询问学习笔记。

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `app/main.py` 中存在 `show_header()`。
- `app/main.py` 中存在 `ask_profile()`。
- `app/main.py` 中存在 `add_note()`。
- `app/main.py` 中存在 `show_profile()`。
- `main()` 会按顺序调用这些函数。
- 程序仍能接收四行输入。
- 程序仍能打印学习档案和学习笔记。
- 没有新增第三方依赖。
- 没有引入循环菜单、条件建议、文件保存或参数返回值。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

函数是后续框架能力的基础。

| 现在 | 后续升级 |
| --- | --- |
| `ask_profile()` | FastAPI 的资料提交接口 |
| `add_note()` | FastAPI 的笔记新增接口 |
| `show_profile()` | 查询资料的工具函数 |
| 普通 Python 函数 | LangChain Tool |
| 一个函数负责一个步骤 | LangGraph node |
| `main()` 调用多个函数 | LangGraph edge 组织流程 |

后续学 LangChain 时，你会看到“工具”本质上也可以从普通函数开始理解。

后续学 LangGraph 时，一个 node 通常也是一个可调用的函数，只是它会接收和返回更正式的 `State`。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-1/01-04-function-extraction.md`

修改文件：

- `ai-learning-assistant/app/main.py`
- `docs/tutorial/README.md`
- `README.md`
- `ai-learning-assistant/README.md`

新增依赖：

- 无

新增命令：

- 无

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
"Alice`nLearn Python Functions`nbeginner`nFunctions group behavior" | py -3.13 app/main.py
```

验证结果：

- 程序成功读取四行输入。
- 输出包含 `名字：Alice`。
- 输出包含 `目标：Learn Python Functions`。
- 输出包含 `1. Functions group behavior`。

下一课依赖：

- 第 1.5 课会加入 `if/elif/else`，根据 `student["python_level"]` 生成学习建议。
