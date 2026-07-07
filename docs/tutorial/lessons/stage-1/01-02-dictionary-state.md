# 第 1.2 课：字典保存状态

## 1. 本课目标

上一课你已经用变量保存了名字和学习目标。

这一课要把多个零散变量合并成一个字典 `student`，让程序开始具备“状态”的雏形。

你要掌握：

- 什么是字典。
- 如何创建字典。
- 如何用 key 读取字典里的值。
- 如何更新字典里的值。
- 为什么后续 LangGraph 的 `State` 可以从字典思路理解。

## 2. 你会新增什么项目能力

本课之后，`AI 学习助教` 不再用多个零散变量保存学员信息，而是用一个 `student` 字典保存：

```python
student = {
    "name": "",
    "goal": "",
    "python_level": "",
}
```

程序会收集三项信息：

- 名字
- 学习目标
- Python 水平

然后统一从 `student` 字典里读取并打印。

## 3. 前置知识

开始前确认你已经理解第 1.1 课：

- 变量可以保存字符串。
- `input()` 可以接收命令行输入。
- `print()` 可以输出内容。
- f-string 可以把变量插入到字符串里。

本课不安装第三方依赖，不引入列表、函数拆分、循环菜单或文件保存。

你仍然会在代码里看到 `def main()`。它是前面课程已经保留的程序入口包装，本课不会展开函数语法；真正的函数拆分会放到第 1.4 课。

## 4. 核心概念

### 字典是什么

字典是一组 key-value 数据。

你可以把它理解成一张资料表：

```python
student = {
    "name": "Alice",
    "goal": "Learn Python",
    "python_level": "beginner",
}
```

左边的 `"name"`、`"goal"`、`"python_level"` 是 key。

右边的 `"Alice"`、`"Learn Python"`、`"beginner"` 是 value。

### 为什么要用字典

第 1.1 课里，我们用了两个零散变量：

```python
student_name = input("请输入你的名字：")
learning_goal = input("请输入你的学习目标：")
```

变量少的时候没问题。

但学习助教后面会保存更多信息：

- 名字
- 学习目标
- Python 水平
- 学习笔记
- 当前学习步骤
- 最近一次练习结果

如果全部用零散变量，代码会越来越散。

所以从本课开始，我们把学员相关状态收拢到一个字典里。

### 创建字典

创建空资料字典：

```python
student = {
    "name": "",
    "goal": "",
    "python_level": "",
}
```

这里先给每个字段一个空字符串，表示还没有填写。

### 更新字典

给字典里的字段赋值：

```python
student["name"] = input("请输入你的名字：")
```

这行代码的意思是：

- 等用户输入名字。
- 把输入结果保存到 `student` 字典的 `"name"` 字段。

### 读取字典

读取字典里的值：

```python
print(f"名字：{student['name']}")
```

注意这里有两层引号：

- 外层 f-string 使用双引号。
- 字典 key 使用单引号。

这样写可以避免引号冲突。

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
}


def main() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")

    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")

    print()
    print("=== 学习档案 ===")
    print(f"名字：{student['name']}")
    print(f"目标：{student['goal']}")
    print(f"Python 水平：{student['python_level']}")
    print(f"{student['name']}，欢迎开始你的 AI 学习助教项目。")


if __name__ == "__main__":
    main()
```

本课最重要的变化是这段：

```python
student = {
    "name": "",
    "goal": "",
    "python_level": "",
}
```

这就是后续所有“状态管理”的起点。

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
```

你应该看到类似输出：

```text
Project: AI Learning Assistant
Current stage: Stage 1
请输入你的名字：小明
请输入你的学习目标：学习 Python 和 LangChain
请输入你的 Python 水平 beginner / basic / intermediate：beginner

=== 学习档案 ===
名字：小明
目标：学习 Python 和 LangChain
Python 水平：beginner
小明，欢迎开始你的 AI 学习助教项目。
```

## 7. 常见错误

### key 写错

错误写法：

```python
student["python_lavel"] = input("请输入你的 Python 水平：")
print(student["python_level"])
```

`python_lavel` 和 `python_level` 不是同一个 key。

字典不会自动帮你纠正拼写。key 要保持一致。

### 忘记引号

错误写法：

```python
print(student[name])
```

这里 Python 会把 `name` 当作变量，而不是字符串 key。

正确写法：

```python
print(student["name"])
```

### f-string 引号冲突

容易写错：

```python
print(f"名字：{student["name"]}")
```

外层和内层都用双引号，会导致语法错误。

推荐写法：

```python
print(f"名字：{student['name']}")
```

## 8. 练习

练习 1：给 `student` 新增一个字段：

```python
"favorite_topic": ""
```

然后用 `input()` 收集：

```python
student["favorite_topic"] = input("你最感兴趣的主题：")
```

最后打印：

```python
print(f"感兴趣主题：{student['favorite_topic']}")
```

练习 2：把 `student` 的初始值改成你自己的默认信息，然后观察运行后会不会被 `input()` 覆盖。

练习 3：故意把某个 key 拼错，观察 Python 报错或输出有什么变化。

## 9. 验收标准

本课完成时，应满足：

- `app/main.py` 中存在 `student` 字典。
- `student` 至少包含 `name`、`goal`、`python_level` 三个 key。
- 程序能接收三行输入。
- 输出能显示名字、学习目标和 Python 水平。
- 没有新增第三方依赖。
- 没有引入列表、循环菜单、函数拆分或文件保存。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

字典是理解后续框架状态的第一步。

后续会这样升级：

| 现在 | 后续升级 |
| --- | --- |
| `student` 字典 | Pydantic 模型 |
| `student["name"]` | API 请求字段 |
| `student["goal"]` | LLM prompt 上下文 |
| `student["python_level"]` | 学习建议条件 |
| 字典里的字段 | LangGraph `State` 字段 |

等学到 LangGraph 时，你会看到类似结构：

```python
class LearningState(TypedDict):
    name: str
    goal: str
    python_level: str
```

它看起来比字典正式，但核心思想一样：把流程运行所需的信息集中保存在一个状态对象里。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-1/01-02-dictionary-state.md`

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
"Alice`nLearn Python and LangChain`nbeginner" | py -3.13 app/main.py
```

验证结果：

- 程序成功读取三行输入。
- 输出包含 `名字：Alice`。
- 输出包含 `目标：Learn Python and LangChain`。
- 输出包含 `Python 水平：beginner`。

下一课依赖：

- 第 1.3 课会在 `student` 中加入 `notes` 列表，用来保存学习笔记。
