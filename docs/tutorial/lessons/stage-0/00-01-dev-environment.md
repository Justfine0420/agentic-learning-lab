# 第 0.1 课：开发环境准备

## 本课目标

本课只解决一件事：确认你能在本机稳定运行 Python，并知道后续教程应该用哪个命令启动项目。

学完本课后，你应该能回答：

- 我的电脑上有哪些 Python 命令可用？
- `python` 和 `py` 指向的是不是同一个版本？
- 后续创建虚拟环境时应该用哪个命令？
- 为什么 AI Agent 项目必须先把环境钉住？

## 你会新增什么项目能力

本课不创建真实代码项目，也不安装依赖。

新增能力是环境认知：

- 能检查 Python 版本。
- 能识别 Windows 上 `python` 与 `py` 的差异。
- 能判断后续课程应该用哪个 Python 命令。
- 能理解虚拟环境为什么是后续 FastAPI、LangChain、LangGraph、Deep Agents 的基础。

真实代码项目 `ai-learning-assistant/` 会在第 0.2 课创建。

## 前置知识

你只需要会打开终端。

Windows 推荐使用 PowerShell。后续命令默认从仓库根目录运行：

```powershell
E:\Code\study
```

## 核心概念

### Python 版本

Python 是后续所有课程的运行时。

教程后续会用到：

- 类型标注，例如 `list[str]`、`dict[str, str]`。
- FastAPI 和 Pydantic。
- LangChain、LangGraph、Deep Agents。
- pytest 测试。

因此不要用太老的 Python。建议使用 Python 3.13 或 Python 3.14。实际项目开始安装依赖时，要以依赖库支持范围为准。

版本来源：

- Python 官网下载页显示当前可下载的 Python 3.14.6。
- Python 官网源码发布页仍列出 Python 3.13.x 稳定维护版本。
- 本教程先使用本机已安装的 Python 3.13.3 作为项目虚拟环境基线，避免用 `python` 命令误入 Python 3.11.6。

当前本机检查结果：

```text
python --version -> Python 3.11.6
py --version     -> Python 3.13.3
```

这说明你的机器上至少有两个入口：

- `python` 当前指向 Python 3.11.6。
- `py` 当前指向 Python 3.13.3。

后续教程优先使用 `py` 创建虚拟环境，避免不小心落到旧版本。

### 虚拟环境

虚拟环境是一个项目自己的 Python 依赖空间。

没有虚拟环境时，你安装的包会混在全局 Python 里。教程推进到 FastAPI、LangChain、LangGraph 后，依赖会越来越多，不隔离会很快乱掉。

后续第 0.2 课创建项目目录后，会在 `ai-learning-assistant/` 内创建：

```text
.venv/
```

这个目录不会提交到仓库。

### 包管理

本教程先使用最基础、最通用的组合：

```text
venv + pip + requirements.txt
```

原因很简单：先把 Python、FastAPI 和 Agent 框架主线学明白，不一开始就引入额外包管理器。等项目稳定后，再讨论是否升级到 `uv`、Poetry 或其它工具。

## 代码实现

本课不写项目代码。

只需要在 PowerShell 运行以下命令，确认 Python 可用。

检查默认 Python：

```powershell
python --version
```

检查 Windows Python Launcher：

```powershell
py --version
```

检查可用版本列表：

```powershell
py -0p
```

如果后续要明确使用 Python 3.13 创建虚拟环境，命令会是：

```powershell
py -3.13 -m venv .venv
```

这条命令本课先不要执行。虚拟环境创建放到第 0.2 课，因为那时才会创建真实项目目录。

## 运行方式

在仓库根目录运行：

```powershell
python --version
py --version
py -0p
```

如果 `py -0p` 不可用，但 `python --version` 可用，也可以继续学习。只是后续创建虚拟环境时要确认 `python` 指向的版本是否满足要求。

## 常见错误

### `python` 和 `py` 版本不同

这是 Windows 上很常见的情况，不是坏事。

处理方式：

- 不要猜测。
- 每次创建虚拟环境时显式指定版本。
- 本教程后续优先使用 `py -3.13`。

### 终端提示找不到 Python

可能原因：

- Python 没安装。
- 安装时没有加入 PATH。
- PowerShell 还没重启。

处理方式：

1. 重新打开 PowerShell。
2. 运行 `py --version`。
3. 如果仍失败，重新安装 Python，并勾选加入 PATH。

### 一上来就安装 LangChain

别急。现在还没创建项目目录和虚拟环境。

如果现在全局安装依赖，后面排查问题会很烦。第 0.2 课再创建项目，第 0.3 课先跑健康检查，之后再逐步引入依赖。

## 练习

完成以下检查，并把结果记下来：

```powershell
python --version
py --version
py -0p
```

回答三个问题：

1. `python` 指向哪个版本？
2. `py` 指向哪个版本？
3. 后续你准备用哪个命令创建虚拟环境？

建议答案：

```text
后续使用 py -3.13 创建虚拟环境。
```

## 验收标准

本课完成时，应满足：

- 能在 PowerShell 运行 `python --version`。
- 能在 PowerShell 运行 `py --version`。
- 知道本机 `python` 与 `py` 是否指向同一版本。
- 知道后续优先使用 `py -3.13` 创建虚拟环境。
- 没有在全局环境里安装任何新依赖。
- 没有创建真实代码项目目录。

本机验证记录：

```text
python --version -> Python 3.11.6
py --version     -> Python 3.13.3
```

`py -0p` 需要学习者在本机自行运行并记录完整输出。

## 和后续 LangChain / LangGraph / Deep Agents 的关系

后续 LangChain、LangGraph、Deep Agents 都运行在同一个 Python 项目里。

如果第 0 阶段没有把 Python 版本、虚拟环境和运行命令弄清楚，后面会出现这些问题：

- FastAPI 能装，但 LangChain 装不上。
- 终端运行的是一个 Python，编辑器使用的是另一个 Python。
- 代码能写，但测试找不到依赖。
- LangGraph 或 Deep Agents 示例在错误环境里运行失败。

本课就是为了提前堵住这些低级坑。先把环境钉住，后面学框架才有意义。

## 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-0/00-01-dev-environment.md`

修改文件：

- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`

新增依赖：

- 无

新增命令：

- `python --version`
- `py --version`
- `py -0p`

验证命令：

- `python --version`
- `py --version`

验证结果：

- `python --version` 返回 `Python 3.11.6`
- `py --version` 返回 `Python 3.13.3`

下一课依赖：

- 第 0.2 课将创建 `ai-learning-assistant/` 项目目录。
- 第 0.2 课将使用 `py -3.13` 创建虚拟环境。

参考来源：

- Python 下载页：<https://www.python.org/downloads/>
- Python 源码发布列表：<https://www.python.org/downloads/source/>
