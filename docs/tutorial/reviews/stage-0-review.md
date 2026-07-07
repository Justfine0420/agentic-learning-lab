# 阶段 0 复盘：环境与项目初始化

## 1. 阶段目标

阶段 0 的目标是让 Agentic Learning Lab 从教程规划进入可运行项目状态。

本阶段只做环境和项目初始化，不进入 Python CLI 学习助手，不安装 FastAPI、LangChain、LangGraph 或 Deep Agents。

## 2. 已生成课程

| 小节 | 标题 | 文档 | 状态 |
| --- | --- | --- | --- |
| 0.1 | 开发环境准备 | `docs/tutorial/lessons/stage-0/00-01-dev-environment.md` | 已生成 / 已验证 |
| 0.2 | 项目目录设计 | `docs/tutorial/lessons/stage-0/00-02-project-structure.md` | 已生成 / 已验证 |
| 0.3 | 第一个健康检查脚本 | `docs/tutorial/lessons/stage-0/00-03-health-check.md` | 已生成 / 已验证 |

## 3. 已创建文件

教程文件：

- `docs/tutorial/lessons/stage-0/00-01-dev-environment.md`
- `docs/tutorial/lessons/stage-0/00-02-project-structure.md`
- `docs/tutorial/lessons/stage-0/00-03-health-check.md`
- `docs/tutorial/reviews/stage-0-review.md`

项目文件：

- `ai-learning-assistant/README.md`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`
- `ai-learning-assistant/app/main.py`
- `ai-learning-assistant/data/.gitkeep`
- `ai-learning-assistant/materials/.gitkeep`
- `ai-learning-assistant/outputs/.gitkeep`
- `ai-learning-assistant/tests/.gitkeep`

## 4. 当前项目结构

```text
ai-learning-assistant/
├── app/
│   └── main.py
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

## 5. 验证命令与结果

### Python 环境

```powershell
python --version
```

结果：

```text
Python 3.11.6
```

```powershell
py --version
```

结果：

```text
Python 3.13.3
```

```powershell
py -0p
```

结果：

```text
 -V:3.13 *        C:\Users\吴溢彬\AppData\Local\Programs\Python\Python313\python.exe
 -V:3.11          D:\python\python.exe
```

### 项目骨架

```powershell
Test-Path ai-learning-assistant
Test-Path ai-learning-assistant/app/main.py
Test-Path ai-learning-assistant/README.md
Test-Path ai-learning-assistant/requirements.txt
Test-Path ai-learning-assistant/.env.example
```

结果：

```text
True
True
True
True
True
```

### 健康检查脚本

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 app/main.py
```

结果：

```text
Project: AI Learning Assistant
Python executable: C:\Users\吴溢彬\AppData\Local\Programs\Python\Python313\python.exe
Python version: 3.13.3
Recommended baseline: Python 3.13
Status: environment ready
```

## 6. 已知限制

- 尚未创建 `.venv/`，阶段 0 只确认系统 Python 3.13 可用。
- 尚未安装任何第三方依赖。
- 尚未实现 Stage 1 的 CLI 学习助手。
- 尚未接入 FastAPI、LangChain、RAG、LangGraph 或 Deep Agents。

这些限制符合阶段 0 范围。

## 7. Stage 1 学习准备

进入 Stage 1 前，先确认：

- 只维护 `ai-learning-assistant/` 一份真实代码项目。
- 优先使用 `py -3.13`。
- 不把 `.venv/`、本地 agent 工作流文件或密钥文件提交进公开仓库。
- 能在 `ai-learning-assistant/` 下运行 `py -3.13 app/main.py`。

## 8. 下一步建议

下一课：第 1.1 课：变量与输入输出。

Stage 1 的第一步应从最小 CLI 输入输出开始，不要提前引入 FastAPI 或 LangChain。
