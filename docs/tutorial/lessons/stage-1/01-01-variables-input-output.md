# 第 1.1 课：变量与输入输出

## 1. 本课目标

这一课开始进入 Stage 1：Python 基础。

本课只做一件事：让 `AI 学习助教` 在命令行里收集你的名字和学习目标，然后打印一份最小学习档案。

你要掌握：

- 用变量保存文本。
- 用 `print()` 输出内容。
- 用 `input()` 接收用户输入。
- 用 f-string 把变量放进字符串。
- 在命令行运行一个需要输入的 Python 程序。

## 2. 你会新增什么项目能力

上一阶段的 `app/main.py` 只是健康检查脚本，只会输出环境状态。

本课之后，项目会变成一个最小 CLI 程序：

```text
请输入你的名字：小明
请输入你的学习目标：学习 Python 和 LangChain

=== 学习档案 ===
名字：小明
目标：学习 Python 和 LangChain
小明，欢迎开始你的 AI 学习助教项目。
```

现在它还不能保存资料，也不能添加笔记。那些会在后续小节逐步加入。

## 3. 前置知识

开始前确认你已经完成 Stage 0：

- 能进入 `ai-learning-assistant/` 目录。
- 能运行 `py -3.13 app/main.py`。
- 知道 `app/main.py` 是当前项目入口。

本课不需要安装任何第三方依赖。

## 4. 核心概念

### 变量

变量是给一个值起名字。

例如：

```python
PROJECT_NAME = "AI Learning Assistant"
```

这里的意思是：把字符串 `"AI Learning Assistant"` 保存到变量 `PROJECT_NAME` 里。

后面要使用项目名时，就不用反复写完整文本，可以直接使用：

```python
print(PROJECT_NAME)
```

### 字符串

字符串就是文本，通常用引号包起来：

```python
"AI Learning Assistant"
"请输入你的名字："
"学习 Python 和 LangChain"
```

中文、英文、空格都可以放进字符串里。

### `print()`

`print()` 用来把内容输出到命令行：

```python
print("你好")
```

运行后会显示：

```text
你好
```

### `input()`

`input()` 用来等待用户输入。

```python
student_name = input("请输入你的名字：")
```

这行代码做了两件事：

- 在命令行显示提示文字。
- 等你输入内容后，把输入结果保存到 `student_name`。

注意：`input()` 得到的结果默认是字符串。

### f-string

f-string 用来把变量插入到字符串里：

```python
print(f"名字：{student_name}")
```

如果 `student_name` 是 `小明`，输出就是：

```text
名字：小明
```

## 5. 代码实现

打开：

```text
ai-learning-assistant/app/main.py
```

把内容改成：

```python
PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 1"


def main() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")

    student_name = input("请输入你的名字：")
    learning_goal = input("请输入你的学习目标：")

    print()
    print("=== 学习档案 ===")
    print(f"名字：{student_name}")
    print(f"目标：{learning_goal}")
    print(f"{student_name}，欢迎开始你的 AI 学习助教项目。")


if __name__ == "__main__":
    main()
```

这段代码里，先保留了项目名和阶段名两个变量：

```python
PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 1"
```

然后用 `input()` 收集两个输入：

```python
student_name = input("请输入你的名字：")
learning_goal = input("请输入你的学习目标：")
```

最后把输入内容打印出来。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

运行：

```powershell
py -3.13 app/main.py
```

按提示输入，例如：

```text
请输入你的名字：小明
请输入你的学习目标：学习 Python 和 LangChain
```

你应该看到类似输出：

```text
Project: AI Learning Assistant
Current stage: Stage 1
请输入你的名字：小明
请输入你的学习目标：学习 Python 和 LangChain

=== 学习档案 ===
名字：小明
目标：学习 Python 和 LangChain
小明，欢迎开始你的 AI 学习助教项目。
```

## 7. 常见错误

### 忘记进入项目目录

如果你在仓库根目录运行：

```powershell
py -3.13 app/main.py
```

可能会看到找不到文件的错误。

应该先进入：

```powershell
cd ai-learning-assistant
```

### 把变量名写进引号里

错误写法：

```python
print("名字：student_name")
```

这会原样输出：

```text
名字：student_name
```

正确写法：

```python
print(f"名字：{student_name}")
```

### `input()` 后面没有保存变量

错误写法：

```python
input("请输入你的名字：")
print(student_name)
```

这里没有把输入结果保存到 `student_name`，所以后面无法使用。

正确写法：

```python
student_name = input("请输入你的名字：")
print(student_name)
```

### 中文符号不是问题

本项目可以输出中文提示文字。只要文件保存为 UTF-8，Python 3.13 可以正常运行。

## 8. 练习

练习 1：新增一个输入项，收集你的 Python 水平。

提示：

```python
python_level = input("请输入你的 Python 水平 beginner / basic / intermediate：")
```

然后在学习档案里打印出来：

```python
print(f"Python 水平：{python_level}")
```

练习 2：新增一个变量：

```python
TODAY_TOPIC = "变量、输入和输出"
```

然后输出：

```text
今日主题：变量、输入和输出
```

练习 3：故意把 f-string 前面的 `f` 去掉，观察输出有什么变化。

## 9. 验收标准

本课完成时，应满足：

- 能运行 `py -3.13 app/main.py`。
- 程序会提示输入名字。
- 程序会提示输入学习目标。
- 程序会打印学习档案。
- 输出里能看到你输入的名字和学习目标。
- 没有新增第三方依赖。
- 没有引入字典、列表、循环或文件读写。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课的 `student_name` 和 `learning_goal` 只是两个普通变量。

后续会这样升级：

| 现在 | 后续升级 |
| --- | --- |
| `student_name` | 学员资料字段 |
| `learning_goal` | 学习目标字段 |
| 多个零散变量 | `student` 字典 |
| 命令行输入 | FastAPI 请求体 |
| 学习档案输出 | LLM / Agent 的上下文 |
| 普通变量状态 | LangGraph 的 `State` |

也就是说，本课不是只学语法。你现在写下的名字和目标，会在后面逐步变成 AI 助教理解用户、生成学习计划、驱动学习流程的基础状态。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-1/01-01-variables-input-output.md`

修改文件：

- `ai-learning-assistant/app/main.py`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`

新增依赖：

- 无

新增命令：

- `py -3.13 app/main.py`

验证命令：

- 在 `ai-learning-assistant/` 下运行：`"Alice`nLearn Python and LangChain" | py -3.13 app/main.py`

验证结果：

- 程序成功读取两行输入。
- 输出包含 `名字：Alice`。
- 输出包含 `目标：Learn Python and LangChain`。

下一课依赖：

- 第 1.2 课会把 `student_name`、`learning_goal` 等零散变量升级为 `student` 字典。
