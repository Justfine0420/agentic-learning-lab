# 第 0.2 课：项目目录设计

## 本课目标

本课把教程从“环境准备”推进到“真实项目骨架”。

你要完成两件事：

- 创建唯一的真实代码项目：`ai-learning-assistant/`。
- 理解每个目录为什么存在、后续会承载什么能力。

本课不写业务代码。健康检查脚本会在第 0.3 课创建。

## 你会新增什么项目能力

新增能力是项目组织能力：

- 知道真实代码只放在 `ai-learning-assistant/`。
- 知道教程文档和项目代码的边界。
- 知道 `.venv/` 为什么不能提交。
- 知道 `requirements.txt`、`.env.example`、项目 README 的职责。

完成本课后，仓库里会出现真实主线项目目录：

```text
ai-learning-assistant/
```

## 前置知识

你需要完成第 0.1 课，并确认：

```powershell
python --version
py --version
py -0p
```

本机当前结论：

```text
python -> Python 3.11.6
py     -> Python 3.13.3
```

所以后续项目命令优先使用：

```powershell
py -3.13
```

## 核心概念

### 只维护一份真实代码项目

本教程不会创建这些目录：

```text
lesson-01-code/
lesson-02-code/
stage-0-code/
```

这些副本看起来方便，但很快会造成三个问题：

- 同一个文件在多个目录里出现，不知道哪个才是真的。
- 后续课程 import 路径混乱。
- 修一个 bug 要同步多份代码。

所以本仓库只维护一份真实项目：

```text
ai-learning-assistant/
```

每一课只在这份主线代码上继续推进。

### 教程文档和代码项目的边界

教程文档放在：

```text
docs/tutorial/
```

真实项目代码放在：

```text
ai-learning-assistant/
```

这两个目录职责不同：

| 目录 | 职责 |
| --- | --- |
| `docs/tutorial/` | 解释学习路线、课程内容、复盘和检查记录 |
| `ai-learning-assistant/` | 存放真实可运行代码和项目资源 |

教程可以讲很多东西，但代码只能有一条主线。

### `.venv/` 不提交

`.venv/` 是本机虚拟环境目录。它通常很大，而且和操作系统、Python 安装路径有关。

它应该存在于你的电脑上，但不应该进仓库。

本仓库会在 `.gitignore` 中忽略：

```text
ai-learning-assistant/.venv/
```

### `requirements.txt`

`requirements.txt` 用来记录项目依赖。

阶段 0 暂时没有第三方依赖，所以文件里只保留说明。

后续会逐步加入：

- FastAPI
- pytest
- LangChain
- LangGraph
- Deep Agents 相关依赖

### `.env.example`

`.env.example` 只放示例配置，不放真实密钥。

后续接入模型 API 时，会在这里写：

```text
OPENAI_API_KEY=
```

真实 `.env` 不应提交。

### 项目 README

`ai-learning-assistant/README.md` 面向真实项目本身，说明怎么运行、当前阶段有什么能力。

根目录 `README.md` 面向整个开源教程仓库，说明课程路线和治理规则。

## 代码实现

本课创建目录和基础文件：

```text
ai-learning-assistant/
├── app/
├── data/
│   └── .gitkeep
├── materials/
│   └── .gitkeep
├── outputs/
│   └── .gitkeep
├── tests/
│   └── .gitkeep
├── requirements.txt
├── .env.example
└── README.md
```

目录职责：

| 路径 | 作用 |
| --- | --- |
| `app/` | Python 应用代码 |
| `data/` | 本地学习数据，例如后续的 `student.json` |
| `materials/` | 本地学习资料，例如 Markdown 笔记 |
| `outputs/` | AI 生成的学习计划、总结和报告 |
| `tests/` | pytest 测试 |
| `requirements.txt` | Python 第三方依赖清单 |
| `.env.example` | 环境变量示例 |
| `README.md` | 真实项目说明 |

`.gitkeep` 只是为了让空目录能被 Git 记录。它没有业务含义。

## 运行方式

本课没有 Python 脚本要运行。

只需要在仓库根目录检查目录是否存在：

```powershell
Test-Path ai-learning-assistant
Test-Path ai-learning-assistant/app
Test-Path ai-learning-assistant/requirements.txt
Test-Path ai-learning-assistant/.env.example
```

如果全部返回 `True`，项目骨架创建成功。

## 常见错误

### 把教程文档写进项目代码目录

不要把课程正文放到 `ai-learning-assistant/`。

课程正文应放在：

```text
docs/tutorial/lessons/
```

### 创建多个代码副本

不要为了保存每课代码创建多个项目副本。需要回顾时，用课程文档、commit 和 tag。

### 提交 `.venv/`

`.venv/` 是本机环境，不是项目源代码。它必须被忽略。

### 一开始就安装依赖

阶段 0 的目标是初始化项目，不是安装框架。FastAPI 和 Agent 框架从后续阶段再引入。

## 练习

1. 用 PowerShell 检查项目目录：

```powershell
Test-Path ai-learning-assistant
Test-Path ai-learning-assistant/app
Test-Path ai-learning-assistant/data
Test-Path ai-learning-assistant/materials
Test-Path ai-learning-assistant/outputs
Test-Path ai-learning-assistant/tests
```

2. 打开 `ai-learning-assistant/README.md`，确认它描述的是项目本身，而不是整个教程仓库。

3. 打开根目录 `.gitignore`，确认包含：

```text
ai-learning-assistant/.venv/
```

## 验收标准

本课完成时，应满足：

- `ai-learning-assistant/` 存在。
- `app/`、`data/`、`materials/`、`outputs/`、`tests/` 存在。
- `requirements.txt` 存在。
- `.env.example` 存在。
- `ai-learning-assistant/README.md` 存在。
- `.gitignore` 忽略 `ai-learning-assistant/.venv/`。
- 没有创建 `lesson-xx-code/` 代码副本。
- 没有安装第三方依赖。

## 和后续 LangChain / LangGraph / Deep Agents 的关系

后续每个框架都会落到这份真实项目里：

- FastAPI 会从 `app/main.py` 开始。
- LangChain agent 会进入 `app/langchain_agent.py`。
- RAG 会使用 `materials/` 和 `app/rag.py`。
- LangGraph 会使用 `app/graph.py`。
- Deep Agents 会使用 `app/deep_agent.py`，并把生成结果写到 `outputs/`。

如果现在目录职责不清，后面框架代码会很快混在一起。

## 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-0/00-02-project-structure.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`
- `ai-learning-assistant/data/.gitkeep`
- `ai-learning-assistant/materials/.gitkeep`
- `ai-learning-assistant/outputs/.gitkeep`
- `ai-learning-assistant/tests/.gitkeep`

修改文件：

- `.gitignore`
- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`

新增依赖：

- 无

新增命令：

- `Test-Path ai-learning-assistant`
- `Test-Path ai-learning-assistant/app`
- `Test-Path ai-learning-assistant/requirements.txt`
- `Test-Path ai-learning-assistant/.env.example`

验证命令：

- `Test-Path ai-learning-assistant`
- `Test-Path ai-learning-assistant/app`
- `Test-Path ai-learning-assistant/requirements.txt`
- `Test-Path ai-learning-assistant/.env.example`

验证结果：

- 以上路径检查应返回 `True`。

下一课依赖：

- 第 0.3 课将在 `ai-learning-assistant/app/main.py` 中创建第一个健康检查脚本。
