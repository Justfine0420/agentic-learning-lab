# Agentic Learning Lab

一个项目驱动的开源教程仓库：从 Python 基础出发，逐步学习 FastAPI、LangChain、RAG、LangGraph 和 Deep Agents，最后完成一个可运行的 `AI 学习助教`。

## 1. 仓库定位

本仓库不是零散代码片段合集，也不是只讲概念的框架笔记。

它的目标是用一个贯穿项目，把 AI Agent 应用开发需要的基础能力串起来：

- Python 基础语法和工程化组织。
- FastAPI 后端接口开发。
- LLM 调用、结构化输出和工具调用。
- LangChain agent harness。
- 基于本地资料的 RAG。
- LangGraph 有状态流程编排。
- Deep Agents 的规划、文件系统、子 Agent 和长期任务能力。
- 测试、验收、教程回顾和开源仓库治理。

贯穿项目名：`AI 学习助教`

真实代码项目目录：`ai-learning-assistant/`

## 2. 为什么叫 Agentic Learning Lab

仓库名采用 `agentic-learning-lab`，而不是直接叫 `ai-learning-assistant`。

原因：

- `AI 学习助教` 是贯穿课程的教学项目。
- `Agentic Learning Lab` 是完整学习实验室，包含教程、治理文档、阶段复盘、代码主线和后续扩展示例。
- 后续如果增加前端、数据库、多用户、部署或其它 Agent 示例，不需要改仓库定位。

## 3. 最终要做出的东西

最终项目会具备：

```text
AI 学习助教
- CLI 可用
- FastAPI 可调用
- 能保存学员信息和学习笔记
- 能读取本地学习资料
- 能用 LangChain 调用模型和工具
- 能用 RAG 基于资料答疑
- 能用 LangGraph 管理学习流程
- 能用 Deep Agents 拆任务、写计划、生成总结文件
- 有基础测试、运行说明和交付文档
```

## 4. 学习路线

| 阶段 | 主题 | 项目升级 |
| --- | --- | --- |
| 0 | 环境与项目初始化 | 空项目可运行 |
| 1 | Python 基础 | CLI 学习助手 |
| 2 | Python 工程化 | 数据持久化、模块拆分 |
| 3 | FastAPI 基础 | 学习助手 API |
| 4 | LLM 基础 | 能调用大模型 |
| 5 | LangChain | 能调用工具的 AI 助手 |
| 6 | RAG | 能读取本地资料答疑 |
| 7 | LangGraph 基础 | 学习流程状态机 |
| 8 | LangGraph 进阶 | 可恢复、可分支、可追踪 |
| 9 | Deep Agents | 能规划、写文件、拆任务 |
| 10 | 综合系统 | 完整 AI 学习助教 |
| 11 | 测试与交付 | 可复现、可验收、可继续扩展 |

完整课程规划见：[docs/tutorial/ai-learning-assistant-course-plan.md](docs/tutorial/ai-learning-assistant-course-plan.md)

## 5. 仓库结构

当前教程文档结构：

```text
docs/tutorial/
├── ai-learning-assistant-course-plan.md
├── README.md
├── lessons/
│   ├── stage-0/
│   │   ├── 00-01-dev-environment.md
│   │   ├── 00-02-project-structure.md
│   │   └── 00-03-health-check.md
│   ├── stage-1/
│   │   ├── 01-01-variables-input-output.md
│   │   ├── 01-02-dictionary-state.md
│   │   ├── 01-03-lists-and-notes.md
│   │   ├── 01-04-function-extraction.md
│   │   ├── 01-05-conditional-suggestion.md
│   │   └── 01-06-loop-menu.md
│   └── stage-2/
│       ├── 02-01-module-split.md
│       ├── 02-02-json-file-io.md
│       ├── 02-03-exception-handling.md
│       ├── 02-04-type-hints.md
│       └── 02-05-simple-pytest.md
│   └── stage-3/
│       ├── 03-01-fastapi-first-api.md
│       └── 03-02-pydantic-models.md
└── reviews/
    ├── stage-0-review.md
    ├── stage-1-review.md
    └── stage-2-review.md
```

真实代码项目：

```text
ai-learning-assistant/
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── cli.py
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   └── student_state.py
├── data/
│   └── .gitkeep
├── materials/
│   ├── .gitkeep
│   └── stage-2.md
├── outputs/
│   └── .gitkeep
├── tests/
│   ├── .gitkeep
│   ├── test_api.py
│   └── test_storage.py
├── requirements.txt
├── .env.example
└── README.md
```

教程小节会按阶段单独归档：

```text
docs/tutorial/lessons/
├── stage-0/
├── stage-1/
├── stage-2/
└── ...
```

阶段复盘会放在：

```text
docs/tutorial/reviews/
```

## 6. 如何使用本教程

本仓库强调可持续学习和可回顾。学习者不需要理解教程生成流程，只需要沿着课程索引、真实代码和 Git checkpoint 学习。

建议方式：

- 先阅读 [课程总纲](docs/tutorial/ai-learning-assistant-course-plan.md)，理解完整路线。
- 再按 [教程索引](docs/tutorial/README.md) 从第 0 阶段开始逐课学习。
- 每个小节都有独立文档，阶段结束后有阶段复盘。
- 代码只维护一份真实主线项目：`ai-learning-assistant/`。
- 需要回看某个阶段时，优先使用 Git tag，例如 `stage-0`。
- 本地 `.venv/`、`.env`、IDE 配置和密钥文件不要提交。

核心入口：

- [教程索引](docs/tutorial/README.md)
- [课程总纲](docs/tutorial/ai-learning-assistant-course-plan.md)
- [阶段 0 复盘](docs/tutorial/reviews/stage-0-review.md)
- [阶段 1 复盘](docs/tutorial/reviews/stage-1-review.md)
- [阶段 2 复盘](docs/tutorial/reviews/stage-2-review.md)
- [阶段 2 补充学习资料](ai-learning-assistant/materials/stage-2.md)

## 7. 每课固定格式

后续每一课都按固定结构输出：

```text
1. 本课目标
2. 你会新增什么项目能力
3. 前置知识
4. 核心概念
5. 代码实现
6. 运行方式
7. 常见错误
8. 练习
9. 验收标准
10. 和后续 LangChain / LangGraph / Deep Agents 的关系
11. 本课变更清单
```

## 8. 当前状态

- 仓库名：`agentic-learning-lab`
- 贯穿项目：`AI 学习助教`
- 真实代码项目：`ai-learning-assistant/` 已创建
- 教程正文：阶段 0、阶段 1 和阶段 2 已完成，阶段 3 已开始
- 当前阶段：阶段 3 进行中
- 当前课程：第 3.2 课已生成并验证

下一步建议：继续阶段 3，第 3.3 课学员资料 API。

## 9. 开源治理说明

当前仓库仍处于教程早期阶段。正式开源前建议补齐：

- License
- 贡献指南
- Issue 模板
- 代码风格说明
- 安全说明，尤其是 API Key 和 `.env` 使用规则

这些内容不在当前阶段强行创建，避免把开源治理模板写成空壳。
