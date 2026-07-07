# 第 1.3 课：列表与笔记

## 1. 本课目标

上一课你已经用 `student` 字典保存学员资料。

这一课要给 `student` 增加一个 `notes` 列表，用来保存学习笔记。

你要掌握：

- 什么是列表。
- 如何创建空列表。
- 如何用 `append()` 往列表里添加内容。
- 如何用 `for` 遍历列表。
- 如何用 `enumerate()` 给输出加序号。

## 2. 你会新增什么项目能力

本课之后，`AI 学习助教` 可以收集一条学习笔记，并把它放进 `student["notes"]`。

`student` 会变成：

```python
student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}
```

运行时会多一个输入：

```text
请输入一条学习笔记：
```

输出里也会多一段：

```text
=== 学习笔记 ===
1. 今天学习了 Python 字典
```

## 3. 前置知识

开始前确认你已经理解第 1.2 课：

- `student` 是字典。
- `student["name"]` 可以读取名字。
- `student["goal"]` 可以读取学习目标。
- `student["python_level"]` 可以读取 Python 水平。

本课会出现 `for`，但它只用于遍历笔记列表。真正的循环菜单会放到第 1.6 课。

本课仍不安装第三方依赖，不保存文件，不做函数拆分。

## 4. 核心概念

### 列表是什么

列表用来保存一组有顺序的数据。

例如：

```python
notes = ["学习变量", "学习字典", "学习列表"]
```

列表里的每一项都有顺序：

```text
第 1 项：学习变量
第 2 项：学习字典
第 3 项：学习列表
```

### 空列表

一开始没有笔记，所以可以先创建空列表：

```python
"notes": []
```

这表示 `notes` 这个字段现在是一个空列表。

### `append()`

`append()` 用来把新内容加到列表末尾。

```python
student["notes"].append(note)
```

如果 `note` 是：

```text
今天学习了 Python 字典
```

那么 `student["notes"]` 就会变成：

```python
["今天学习了 Python 字典"]
```

### 遍历列表

要把列表里的每一条笔记都打印出来，可以用：

```python
for saved_note in student["notes"]:
    print(saved_note)
```

这里的意思是：从 `student["notes"]` 里逐条取出笔记，每次放到 `saved_note` 里。

### `enumerate()`

如果想给笔记加序号，可以用：

```python
for index, saved_note in enumerate(student["notes"], start=1):
    print(f"{index}. {saved_note}")
```

`start=1` 表示序号从 1 开始。

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


def main() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")

    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")
    note = input("请输入一条学习笔记：")
    student["notes"].append(note)

    print()
    print("=== 学习档案 ===")
    print(f"名字：{student['name']}")
    print(f"目标：{student['goal']}")
    print(f"Python 水平：{student['python_level']}")

    print()
    print("=== 学习笔记 ===")
    for index, saved_note in enumerate(student["notes"], start=1):
        print(f"{index}. {saved_note}")

    print(f"{student['name']}，欢迎开始你的 AI 学习助教项目。")


if __name__ == "__main__":
    main()
```

本课最重要的新增代码是：

```python
"notes": [],
```

以及：

```python
note = input("请输入一条学习笔记：")
student["notes"].append(note)
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
请输入你的学习目标：学习 Python 和 LangChain
请输入你的 Python 水平 beginner / basic / intermediate：beginner
请输入一条学习笔记：今天学习了 Python 列表
```

你应该看到类似输出：

```text
Project: AI Learning Assistant
Current stage: Stage 1
请输入你的名字：小明
请输入你的学习目标：学习 Python 和 LangChain
请输入你的 Python 水平 beginner / basic / intermediate：beginner
请输入一条学习笔记：今天学习了 Python 列表

=== 学习档案 ===
名字：小明
目标：学习 Python 和 LangChain
Python 水平：beginner

=== 学习笔记 ===
1. 今天学习了 Python 列表
小明，欢迎开始你的 AI 学习助教项目。
```

## 7. 常见错误

### 把 `notes` 写成字符串

错误写法：

```python
"notes": ""
```

这样 `notes` 是字符串，不是列表。

后面调用：

```python
student["notes"].append(note)
```

会失败，因为字符串没有用于追加列表项的 `append()`。

正确写法：

```python
"notes": []
```

### 忘记调用 `append()`

错误写法：

```python
note = input("请输入一条学习笔记：")
```

这只把笔记保存到了 `note` 变量里，没有加入 `student["notes"]`。

正确写法：

```python
note = input("请输入一条学习笔记：")
student["notes"].append(note)
```

### 遍历时缩进错误

错误写法：

```python
for index, saved_note in enumerate(student["notes"], start=1):
print(f"{index}. {saved_note}")
```

`print()` 必须缩进到 `for` 下面：

```python
for index, saved_note in enumerate(student["notes"], start=1):
    print(f"{index}. {saved_note}")
```

### 期待笔记能永久保存

本课的笔记只保存在程序运行内存里。

程序退出后，笔记会消失。文件保存会在 Stage 2 的 JSON 文件读写里学习。

## 8. 练习

练习 1：在代码里临时添加第二条笔记：

```python
student["notes"].append("这是第二条练习笔记")
```

观察输出是否变成两条。

练习 2：把 `start=1` 改成 `start=0`，观察序号变化。

练习 3：把 `student["notes"]` 初始值改成：

```python
["复习变量", "复习字典"]
```

再运行程序，观察新输入的笔记会追加到哪里。

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `student` 字典中存在 `notes` 字段。
- `student["notes"]` 的初始值是列表。
- 程序能接收一条学习笔记。
- 程序会用 `append()` 把笔记加入 `student["notes"]`。
- 程序会打印 `=== 学习笔记 ===`。
- 程序会用序号打印笔记。
- 没有新增第三方依赖。
- 没有引入循环菜单、函数拆分或文件保存。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

笔记列表会在后续继续升级：

| 现在 | 后续升级 |
| --- | --- |
| `student["notes"]` | 学习笔记数据 |
| `append()` | 添加笔记 API |
| 遍历笔记 | 展示历史记录 |
| 本地笔记列表 | RAG 可读取资料的一部分 |
| 笔记上下文 | LangChain Agent 工具查询结果 |
| notes 字段 | LangGraph `State` 中的列表字段 |

现在的列表只是内存里的数据。

后续到 Stage 2，会把数据保存到 JSON 文件里；到 RAG 阶段，会让 AI 基于资料和笔记回答问题。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-1/01-03-lists-and-notes.md`

修改文件：

- `ai-learning-assistant/app/main.py`
- `docs/tutorial/README.md`
- `README.md`
- `ai-learning-assistant/README.md`

新增依赖：

- 无

新增命令：

- `py -3.13 app/main.py`

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
"Alice`nLearn Python and LangChain`nbeginner`nUse list append" | py -3.13 app/main.py
```

验证结果：

- 程序成功读取四行输入。
- 输出包含 `名字：Alice`。
- 输出包含 `Python 水平：beginner`。
- 输出包含 `1. Use list append`。

下一课依赖：

- 第 1.4 课会把当前代码拆分成 `ask_profile()`、`add_note()` 等函数。
