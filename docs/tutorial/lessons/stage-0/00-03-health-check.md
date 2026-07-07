# 第 0.3 课：第一个健康检查脚本

## 本课目标

本课让 `ai-learning-assistant/` 从“目录存在”升级为“可以运行”。

你会创建第一个 Python 文件：

```text
ai-learning-assistant/app/main.py
```

它不做业务功能，只做健康检查：输出项目名、Python 解释器路径、Python 版本和环境状态。

## 你会新增什么项目能力

新增能力：

- 项目可以通过命令运行。
- 可以确认当前运行的是 Python 3.13。
- 可以确认后续课程会使用同一个项目入口。
- 可以为 FastAPI、LangChain、LangGraph 的接入打基础。

本课仍不进入 Stage 1，不写学习助手 CLI。

## 前置知识

你需要完成：

- 第 0.1 课：知道 `py -3.13` 可用。
- 第 0.2 课：已经创建 `ai-learning-assistant/` 项目骨架。

当前项目目录应包含：

```text
ai-learning-assistant/
├── app/
├── data/
├── materials/
├── outputs/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## 核心概念

### 入口文件

入口文件是你运行项目时最先执行的文件。

本课使用：

```text
app/main.py
```

后续 FastAPI 阶段也会从这个文件演进，不会另起一套入口。

### `sys.executable`

`sys.executable` 会显示当前执行脚本的 Python 解释器路径。

这能帮助你确认：

- 运行脚本的是不是预期 Python。
- 终端和编辑器是不是使用同一个环境。
- 后续虚拟环境是否生效。

### `platform.python_version()`

`platform.python_version()` 会输出当前 Python 版本。

本教程当前基线是 Python 3.13，因此运行结果应该接近：

```text
Python version: 3.13.3
```

## 代码实现

创建文件：

```text
ai-learning-assistant/app/main.py
```

代码：

```python
import platform
import sys


PROJECT_NAME = "AI Learning Assistant"
RECOMMENDED_PYTHON = "3.13"


def main() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {platform.python_version()}")
    print(f"Recommended baseline: Python {RECOMMENDED_PYTHON}")
    print("Status: environment ready")


if __name__ == "__main__":
    main()
```

这段代码只使用 Python 标准库，不需要安装第三方依赖。

## 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行健康检查：

```powershell
py -3.13 app/main.py
```

预期输出类似：

```text
Project: AI Learning Assistant
Python executable: C:\Users\...\Python313\python.exe
Python version: 3.13.3
Recommended baseline: Python 3.13
Status: environment ready
```

运行后回到仓库根目录：

```powershell
cd ..
```

## 常见错误

### 在错误目录运行命令

如果你在仓库根目录运行：

```powershell
py -3.13 app/main.py
```

会失败，因为 `app/main.py` 在 `ai-learning-assistant/` 里面。

正确方式：

```powershell
cd ai-learning-assistant
py -3.13 app/main.py
```

### 用了 `python app/main.py`

你的机器上 `python` 当前指向 Python 3.11.6。

为了避免版本漂移，本教程阶段 0 使用：

```powershell
py -3.13 app/main.py
```

### 输出的 Python 版本不是 3.13

说明你没有使用 `py -3.13`，或者本机 Python Launcher 配置不一致。

先运行：

```powershell
py -0p
```

确认 Python 3.13 的路径存在。

## 练习

1. 运行健康检查脚本。
2. 观察 `Python executable` 的输出。
3. 回答：

```text
当前脚本实际使用的 Python 路径是什么？
当前脚本实际使用的 Python 版本是什么？
```

扩展练习：

把 `PROJECT_NAME` 改成：

```python
PROJECT_NAME = "AI 学习助教"
```

运行后观察输出变化。练习完成后再改回英文名，保持项目输出和教程一致。

## 验收标准

本课完成时，应满足：

- `ai-learning-assistant/app/main.py` 存在。
- 能在 `ai-learning-assistant/` 目录下运行 `py -3.13 app/main.py`。
- 输出包含 `Project: AI Learning Assistant`。
- 输出包含 `Python version: 3.13.3` 或同一 3.13 系列版本。
- 输出包含 `Status: environment ready`。
- 没有安装第三方依赖。
- 没有进入 Stage 1 的 CLI 功能。

本机验证记录：

```text
Project: AI Learning Assistant
Python executable: C:\Users\吴溢彬\AppData\Local\Programs\Python\Python313\python.exe
Python version: 3.13.3
Recommended baseline: Python 3.13
Status: environment ready
```

## 和后续 LangChain / LangGraph / Deep Agents 的关系

后续所有框架能力都会从这个项目入口逐步演进：

- FastAPI 阶段会把 `app/main.py` 改造成 API 服务入口。
- LangChain 阶段会新增 agent 模块，再由 API 或脚本调用。
- LangGraph 阶段会新增流程编排模块。
- Deep Agents 阶段会新增长期任务能力。

现在这个健康检查脚本很小，但它证明了一件关键事：项目能用预期 Python 运行。

## 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-0/00-03-health-check.md`
- `ai-learning-assistant/app/main.py`

修改文件：

- `docs/tutorial/README.md`

新增依赖：

- 无

新增命令：

- `py -3.13 app/main.py`

验证命令：

- 在 `ai-learning-assistant/` 下运行：`py -3.13 app/main.py`

验证结果：

- 健康检查脚本成功输出项目名、Python 路径、Python 版本和环境状态。

下一课依赖：

- Stage 1 可以基于 `ai-learning-assistant/app/main.py` 和当前项目骨架继续扩展。
