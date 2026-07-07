# 第 1.5 课：条件判断

## 1. 本课目标

上一课你已经把程序拆成多个函数。

这一课要让学习助教根据学员的 Python 水平输出不同建议。核心语法是 `if/elif/else`。

你要掌握：

- 什么是条件判断。
- 如何使用 `if`。
- 如何使用 `elif`。
- 如何使用 `else`。
- 如何用条件判断读取 `student["python_level"]`。
- 为什么条件判断是后续 LangGraph 条件分支的前置知识。

## 2. 你会新增什么项目能力

本课之后，`AI 学习助教` 会多一个函数：

```python
def suggest_next_step() -> None:
    ...
```

它会根据 `student["python_level"]` 输出不同建议：

| 输入 | 输出建议 |
| --- | --- |
| `beginner` | 今天学习变量、函数、字典 |
| `basic` | 今天学习类、文件读写、异常处理 |
| 其它值 | 今天开始学习 LangChain 的 agent |

本课仍然不引入循环菜单。程序还是运行一次，输入一次，输出一次。

## 3. 前置知识

开始前确认你已经理解：

- `student` 是保存状态的字典。
- `student["python_level"]` 保存用户输入的 Python 水平。
- 函数可以把一段逻辑封装起来。
- `main()` 可以按顺序调用多个函数。

本课暂不做输入校验，不做菜单循环，不保存文件，不调用 AI。

## 4. 核心概念

### 条件判断是什么

条件判断就是：如果某个条件成立，就执行某段代码。

例如：

```python
if student["python_level"] == "beginner":
    print("建议：今天学习变量、函数、字典。")
```

这行代码的意思是：

如果 `student["python_level"]` 等于 `"beginner"`，就打印 beginner 对应建议。

### `==` 不是 `=`

判断两个值是否相等，要用 `==`：

```python
student["python_level"] == "beginner"
```

给变量或字典字段赋值，用 `=`：

```python
student["python_level"] = input("请输入你的 Python 水平：")
```

这两个不能混用。

### `elif`

`elif` 表示“否则如果”。

```python
elif student["python_level"] == "basic":
    print("建议：今天学习类、文件读写、异常处理。")
```

只有前面的 `if` 不成立时，Python 才会继续检查 `elif`。

### `else`

`else` 表示其它所有情况。

```python
else:
    print("建议：今天开始学习 LangChain 的 agent。")
```

本课里，如果用户输入的不是 `beginner`，也不是 `basic`，都会走 `else`。

所以输入 `intermediate` 会走 `else`；输入 `abc` 也会走 `else`。

### 为什么先不做输入校验

你可能会觉得：用户输错了怎么办？

这个问题对，但不是本课重点。

本课只学习条件分支。输入校验、循环重试、无效选项处理会在第 1.6 课的循环菜单里继续补。

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


def suggest_next_step() -> None:
    print()
    print("=== 今日学习建议 ===")

    if student["python_level"] == "beginner":
        print("建议：今天学习变量、函数、字典。")
    elif student["python_level"] == "basic":
        print("建议：今天学习类、文件读写、异常处理。")
    else:
        print("建议：今天开始学习 LangChain 的 agent。")


def main() -> None:
    show_header()
    ask_profile()
    add_note()
    show_profile()
    suggest_next_step()
    print(f"{student['name']}，欢迎开始你的 AI 学习助教项目。")


if __name__ == "__main__":
    main()
```

本课最重要的新增代码是：

```python
def suggest_next_step() -> None:
    print()
    print("=== 今日学习建议 ===")

    if student["python_level"] == "beginner":
        print("建议：今天学习变量、函数、字典。")
    elif student["python_level"] == "basic":
        print("建议：今天学习类、文件读写、异常处理。")
    else:
        print("建议：今天开始学习 LangChain 的 agent。")
```

以及在 `main()` 中调用：

```python
suggest_next_step()
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

输入 beginner：

```text
请输入你的名字：小明
请输入你的学习目标：学习 Python 条件判断
请输入你的 Python 水平 beginner / basic / intermediate：beginner
请输入一条学习笔记：if 可以让程序根据条件走不同分支
```

你应该看到：

```text
=== 今日学习建议 ===
建议：今天学习变量、函数、字典。
```

再运行一次，把 Python 水平改成：

```text
basic
```

你应该看到：

```text
=== 今日学习建议 ===
建议：今天学习类、文件读写、异常处理。
```

再运行一次，把 Python 水平改成：

```text
intermediate
```

你应该看到：

```text
=== 今日学习建议 ===
建议：今天开始学习 LangChain 的 agent。
```

## 7. 常见错误

### 把 `==` 写成 `=`

错误写法：

```python
if student["python_level"] = "beginner":
```

判断相等要用 `==`：

```python
if student["python_level"] == "beginner":
```

### 忘记冒号

错误写法：

```python
if student["python_level"] == "beginner"
    print("建议：今天学习变量、函数、字典。")
```

正确写法：

```python
if student["python_level"] == "beginner":
    print("建议：今天学习变量、函数、字典。")
```

### 缩进错误

错误写法：

```python
if student["python_level"] == "beginner":
print("建议：今天学习变量、函数、字典。")
```

`print()` 必须缩进到 `if` 下面：

```python
if student["python_level"] == "beginner":
    print("建议：今天学习变量、函数、字典。")
```

### 输入大小写不匹配

本课代码只判断小写：

```python
beginner
basic
intermediate
```

如果输入 `Beginner`，不会进入 beginner 分支，而会走 `else`。

这个问题后面可以通过输入标准化解决，比如 `.lower()`，但本课先不加。

## 8. 练习

练习 1：给 `intermediate` 单独加一个分支：

```python
elif student["python_level"] == "intermediate":
    print("建议：今天学习 LangChain 的工具调用。")
```

然后把 `else` 改成：

```python
else:
    print("建议：请输入 beginner / basic / intermediate 之一。")
```

练习 2：把 beginner 的建议换成你自己的学习计划。

练习 3：故意输入 `Beginner`，观察输出为什么不是 beginner 建议。

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `app/main.py` 中存在 `suggest_next_step()`。
- `suggest_next_step()` 使用 `if/elif/else`。
- `main()` 会调用 `suggest_next_step()`。
- 输入 `beginner` 时输出变量、函数、字典建议。
- 输入 `basic` 时输出类、文件读写、异常处理建议。
- 输入其它值时输出 LangChain agent 建议。
- 没有新增第三方依赖。
- 没有引入循环菜单、文件保存或 AI 调用。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

条件判断会在后续继续升级：

| 现在 | 后续升级 |
| --- | --- |
| `if/elif/else` | LangGraph conditional edge |
| `python_level` | 学习流程分支依据 |
| `suggest_next_step()` | 学习建议节点 |
| 写死规则建议 | LLM 生成个性化建议 |
| `else` 兜底 | API 错误处理和默认分支 |

到了 LangGraph 阶段，你会看到类似问题：

```text
如果学员答对，进入下一题；
如果学员答错，进入讲解；
如果需要人工确认，暂停流程。
```

这些流程分支，本质上都先从今天的 `if/elif/else` 开始理解。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-1/01-05-conditional-suggestion.md`

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
"Alice`nLearn Python Conditions`nbeginner`nConditions choose branches" | py -3.13 app/main.py
```

验证结果：

- 程序成功读取四行输入。
- 输出包含 `名字：Alice`。
- 输出包含 `1. Conditions choose branches`。
- 输出包含 `建议：今天学习变量、函数、字典。`。

下一课依赖：

- 第 1.6 课会加入 `while True` 循环菜单，让学习助教可以反复添加笔记、查看资料和退出。
