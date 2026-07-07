# 第 1.6 课：循环菜单

## 1. 本课目标

上一课你已经能根据 Python 水平生成学习建议。

这一课要把程序升级成一个可以反复操作的 CLI 学习助手。核心语法是 `while True`、`break` 和菜单分支。

你要掌握：

- 什么是循环。
- 如何用 `while True` 保持程序运行。
- 如何用 `break` 退出循环。
- 如何用菜单选项组织多个功能。
- 如何处理无效选项。
- 为什么 CLI 菜单是后续 FastAPI 路由和 LangGraph 流程的前置理解。

## 2. 你会新增什么项目能力

本课之后，`AI 学习助教` 不再是输入一次、输出一次就结束。

它会启动一个菜单：

```text
请选择操作：
1. 添加学习笔记
2. 查看学习信息
3. 生成今日学习建议
4. 退出
```

你可以：

- 多次添加学习笔记。
- 随时查看学习档案和笔记。
- 随时生成今日学习建议。
- 输入 `4` 退出程序。
- 输入其它内容时看到无效选项提示。

本课完成后，Stage 1 的 CLI 学习助手就成型了。

## 3. 前置知识

开始前确认你已经理解：

- `student` 字典保存学员资料。
- `student["notes"]` 列表保存学习笔记。
- `add_note()` 添加笔记。
- `show_profile()` 查看资料。
- `suggest_next_step()` 生成建议。
- `if/elif/else` 可以根据选项走不同分支。

本课仍不保存文件，不安装第三方依赖，不调用 AI。

## 4. 核心概念

### 为什么需要循环

第 1.5 课的程序只能按固定顺序运行：

1. 收集资料。
2. 添加一条笔记。
3. 展示资料。
4. 生成建议。
5. 程序结束。

真实工具不能这么僵硬。

用户应该可以自己选择：

- 现在添加笔记。
- 现在查看资料。
- 现在生成建议。
- 现在退出。

这就需要循环菜单。

### `while True`

`while True` 表示一直循环：

```python
while True:
    print("请选择操作")
```

如果没有退出条件，程序会一直运行。

所以必须配合 `break`。

### `break`

`break` 用来跳出循环：

```python
elif choice == "4":
    print("下次继续学习。")
    break
```

当用户选择 `4`，程序打印退出提示，然后跳出 `while True`。

### 菜单选项也是条件判断

菜单本质上还是 `if/elif/else`：

```python
if choice == "1":
    add_note()
elif choice == "2":
    show_profile()
elif choice == "3":
    suggest_next_step()
elif choice == "4":
    break
else:
    print("无效选项，请重新输入。")
```

它和上一课判断 `python_level` 的结构一样，只是判断对象从学习水平换成了菜单选项。

### 为什么资料仍然不会永久保存

本课新增的是循环菜单，不是文件读写。

你可以在一次运行里添加多条笔记，但程序退出后，内存里的 `student` 会消失。

Stage 2 会专门学习 JSON 文件保存，让数据在重启后仍然存在。

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


def main() -> None:
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


if __name__ == "__main__":
    main()
```

本课最重要的新增代码是：

```python
while True:
    print()
    print("请选择操作：")
    print("1. 添加学习笔记")
    print("2. 查看学习信息")
    print("3. 生成今日学习建议")
    print("4. 退出")

    choice = input("输入选项：")
```

以及：

```python
elif choice == "4":
    print(f"{student['name']}，下次继续学习。")
    break
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

可以按这个顺序输入：

```text
请输入你的名字：小明
请输入你的学习目标：学习 Python CLI
请输入你的 Python 水平 beginner / basic / intermediate：beginner
输入选项：2
输入选项：1
请输入一条学习笔记：今天完成了 Stage 1
输入选项：2
输入选项：3
输入选项：9
输入选项：4
```

你应该看到这些关键输出：

```text
暂无笔记
已保存。
1. 今天完成了 Stage 1
建议：今天学习变量、函数、字典。
无效选项，请重新输入。
小明，下次继续学习。
```

## 7. 常见错误

### 忘记 `break`

错误写法：

```python
elif choice == "4":
    print("下次继续学习。")
```

没有 `break`，程序不会退出菜单。

正确写法：

```python
elif choice == "4":
    print("下次继续学习。")
    break
```

### 把 `while True` 写在函数外面

菜单循环应该放在 `main()` 里。

如果把循环写在文件最外层，后续拆模块、测试、导入时会更难控制。

### 菜单选项用数字而不是字符串比较

`input()` 返回的是字符串。

所以要这样判断：

```python
if choice == "1":
```

不是：

```python
if choice == 1:
```

### 忘记处理无效选项

如果没有 `else`，用户输入 `9` 时程序什么也不提示。

保留这个分支：

```python
else:
    print("无效选项，请重新输入。")
```

## 8. 练习

练习 1：把菜单里的 `3. 生成今日学习建议` 改成 `3. 查看今日学习建议`，观察输出是否变化。

练习 2：新增一个菜单项：

```text
5. 查看笔记数量
```

输出：

```python
print(f"当前共有 {len(student['notes'])} 条笔记。")
```

练习 3：把退出选项从 `4` 改成 `0`，并同步修改菜单文案和判断条件。

练习完成后，建议把代码恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `main()` 中存在 `while True`。
- 菜单包含添加学习笔记、查看学习信息、生成今日学习建议、退出。
- 输入 `1` 可以添加笔记。
- 输入 `2` 可以查看学习档案和笔记。
- 输入 `3` 可以生成学习建议。
- 输入 `4` 可以退出程序。
- 输入其它内容会提示无效选项。
- 程序没有新增第三方依赖。
- 程序仍然不保存文件。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

循环菜单是后续系统入口的前身。

| 现在 | 后续升级 |
| --- | --- |
| 菜单选项 | FastAPI 路由 |
| `choice == "1"` | `POST /notes` |
| `choice == "2"` | `GET /profile` |
| `choice == "3"` | `GET /suggestion` |
| `while True` | 服务持续运行 |
| 菜单流程 | LangGraph 流程编排 |

Stage 1 到这里结束。你已经具备了后续需要的最小基础：

- 状态：`student` 字典。
- 列表：`student["notes"]`。
- 函数：`add_note()`、`show_profile()`、`suggest_next_step()`。
- 条件：`if/elif/else`。
- 循环：`while True`。

后续 Stage 2 会把这份 CLI 助手拆成模块，并把内存数据保存到 JSON 文件。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-1/01-06-loop-menu.md`

修改文件：

- `ai-learning-assistant/app/main.py`
- `docs/tutorial/README.md`
- `docs/tutorial/reviews/stage-1-review.md`
- `README.md`
- `ai-learning-assistant/README.md`

新增依赖：

- 无

新增命令：

- 无

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
"Alice`nLearn Python CLI`nbeginner`n2`n1`nFinish Stage 1`n2`n3`n9`n4" | py -3.13 app/main.py
```

验证结果：

- 首次查看资料时输出 `暂无笔记`。
- 添加笔记后输出 `已保存。`。
- 再次查看资料时输出 `1. Finish Stage 1`。
- 生成建议时输出 `建议：今天学习变量、函数、字典。`。
- 输入 `9` 时输出 `无效选项，请重新输入。`。
- 输入 `4` 时程序退出。

下一课依赖：

- 第 2.1 课会进入 Python 工程化，把当前 `main.py` 拆分成 `cli.py`、`storage.py` 等模块。
