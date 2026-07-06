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

当前治理文档结构：

```text
docs/tutorial/
├── ai-learning-assistant-course-plan.md
├── README.md
├── project-state.md
└── code-consistency-checklist.md
```

正式开始第 0 阶段后，会创建真实代码项目：

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

教程小节会按阶段单独归档：

```text
docs/tutorial/lessons/
├── stage-0/
├── stage-1/
└── ...
```

阶段复盘会放在：

```text
docs/tutorial/reviews/
```

## 6. 教程生成规则

本仓库强调可持续学习和可回顾，不靠聊天上下文硬撑。

核心规则：

- 每个小节单独归档。
- 每个阶段单独复盘。
- 代码只维护一份真实主线项目：`ai-learning-assistant/`。
- 不创建 `lesson-01-code/`、`lesson-02-code/` 这类课程代码副本。
- 每课如果涉及代码，必须同步更新真实项目代码、教程小节、教程索引、项目状态快照和一致性检查结果。
- 每课必须有“本课变更清单”。
- 不强制每个小节 commit 或打 tag；代码里程碑和阶段完成时再建议归档。
- 当前已授权后续自归档，但仅限 `developer` 分支；禁止往 `master` 分支提交、打 tag 或推送。未明确要求 push 时，只本地 commit，不推送远端。

治理文档：

- [教程索引](docs/tutorial/README.md)
- [项目状态快照](docs/tutorial/project-state.md)
- [代码一致性检查清单](docs/tutorial/code-consistency-checklist.md)

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
- 真实代码项目：尚未创建
- 教程正文：尚未开始生成
- 当前阶段：规划和治理文档已落盘

下一步建议：生成第 0.1 课：开发环境准备。

## 9. 开源治理说明

当前仓库仍处于教程规划阶段。正式开源前建议补齐：

- License
- 贡献指南
- Issue 模板
- 代码风格说明
- 安全说明，尤其是 API Key 和 `.env` 使用规则

这些内容不在当前规划阶段强行创建，避免把开源治理模板写成空壳。
