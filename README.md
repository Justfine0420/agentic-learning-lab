# LangChain / LangGraph / Deep Agents 项目实战教程

从 Python 与 FastAPI 基础出发，逐步学习 LLM 调用、LangChain、RAG、LangGraph 和 Deep Agents，最终构建一个可运行、可测试、可持续扩展的 `AI 学习助教`。

## 1. 项目简介

本仓库是一套项目驱动的 AI Agent 工程课程。

课程不把框架概念拆成孤立笔记，而是围绕同一个贯穿项目逐步升级：

```text
AI 学习助教
```

你会从一个普通命令行程序开始，逐步把它升级成具备 API、模型调用、工具调用、资料问答、学习流程编排和长期任务能力的 AI 应用。

真实代码项目位于：

```text
ai-learning-assistant/
```

## 2. 适合谁学习

这套课程适合：

- 想系统学习 LangChain、LangGraph、Deep Agents 的开发者。
- 想从 Python 基础过渡到 AI Agent 应用开发的学习者。
- 已经看过一些框架概念，但缺少完整项目主线的人。
- 想了解 FastAPI、LLM 调用、RAG、Agent 工具调用和状态编排如何串起来的人。

不适合只想复制一个现成聊天机器人模板的人。

## 3. 你会学到什么

课程覆盖的核心能力：

- Python 基础语法、函数拆分、模块化和文件持久化。
- FastAPI 接口开发、Pydantic 模型、API 测试和错误处理。
- LLM provider 配置、模型调用、结构化输出和降级边界。
- LangChain `create_agent`、工具定义、工具调用和 agent harness。
- 基于本地资料的 RAG 问答。
- LangGraph 的 `State`、node、edge、条件分支、checkpoint 和人机协作。
- Deep Agents 的规划、文件系统、子 Agent 和长任务执行。
- 测试、验收、阶段复盘和可回顾的 Git checkpoint。

## 4. 最终会构建什么

最终项目会具备：

```text
AI 学习助教
- CLI 可用
- FastAPI 可调用
- 能保存学员信息和学习笔记
- 能读取本地学习资料
- 能调用大模型生成学习建议
- 能用 LangChain Agent 调用工具
- 能用 RAG 基于学习资料答疑
- 能用 LangGraph 管理学习流程
- 能用 Deep Agents 拆任务、写计划、生成总结文件
- 有测试、运行说明和交付文档
```

## 5. 当前进度

- 当前阶段：阶段 7，LangGraph 基础，进行中。
- 当前课程：第 7.5 课，条件分支。
- 下一步：进入第 7.6 课，FastAPI 调 Graph。
- 已完成阶段复盘：阶段 0、阶段 1、阶段 2、阶段 3、阶段 4、阶段 5、阶段 6。

课程索引见：[docs/tutorial/README.md](docs/tutorial/README.md)

## 6. 快速开始

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行测试：

```powershell
py -3.13 -m pytest
```

运行 CLI：

```powershell
py -3.13 -m app.main
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

API 文档地址：

```text
http://127.0.0.1:8000/docs
```

## 7. 学习路线

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

## 8. 主要入口

- [教程索引](docs/tutorial/README.md)
- [课程总纲](docs/tutorial/ai-learning-assistant-course-plan.md)
- [真实项目代码](ai-learning-assistant/)
- [阶段 0 复盘](docs/tutorial/reviews/stage-0-review.md)
- [阶段 1 复盘](docs/tutorial/reviews/stage-1-review.md)
- [阶段 2 复盘](docs/tutorial/reviews/stage-2-review.md)
- [阶段 3 复盘](docs/tutorial/reviews/stage-3-review.md)
- [阶段 4 复盘](docs/tutorial/reviews/stage-4-review.md)
- [阶段 5 复盘](docs/tutorial/reviews/stage-5-review.md)
- [阶段 6 复盘](docs/tutorial/reviews/stage-6-review.md)
- [第 5.4 课：多工具调用](docs/tutorial/lessons/stage-5/05-04-multiple-tools.md)
- [第 5.5 课：结构化 Agent 输出](docs/tutorial/lessons/stage-5/05-05-structured-agent-output.md)
- [第 5.6 课：CLI 接入 LangChain Agent](docs/tutorial/lessons/stage-5/05-06-cli-agent-integration.md)
- [第 5.7 课：FastAPI 接入 LangChain Agent](docs/tutorial/lessons/stage-5/05-07-fastapi-agent-integration.md)
- [第 6.1 课：RAG 是什么](docs/tutorial/lessons/stage-6/06-01-rag-concepts.md)
- [第 6.2 课：本地资料加载](docs/tutorial/lessons/stage-6/06-02-local-material-loading.md)
- [第 6.3 课：文档切分](docs/tutorial/lessons/stage-6/06-03-document-splitting.md)
- [第 6.4 课：向量检索](docs/tutorial/lessons/stage-6/06-04-vector-retrieval.md)
- [第 6.5 课：基于资料回答](docs/tutorial/lessons/stage-6/06-05-grounded-material-answer.md)
- [第 6.6 课：RAG API](docs/tutorial/lessons/stage-6/06-06-rag-api.md)
- [第 7.1 课：LangGraph 核心模型](docs/tutorial/lessons/stage-7/07-01-langgraph-core-model.md)
- [第 7.2 课：定义 LearningState](docs/tutorial/lessons/stage-7/07-02-learning-state.md)
- [第 7.3 课：第一个节点](docs/tutorial/lessons/stage-7/07-03-first-node.md)
- [第 7.4 课：多节点流程](docs/tutorial/lessons/stage-7/07-04-multi-node-flow.md)
- [第 7.5 课：条件分支](docs/tutorial/lessons/stage-7/07-05-conditional-branch.md)

## 9. 仓库结构

```text
docs/tutorial/                 课程总纲、教程索引、逐课文档和阶段复盘
ai-learning-assistant/app/      贯穿项目的应用代码
ai-learning-assistant/tests/    测试代码
ai-learning-assistant/materials/补充学习资料
ai-learning-assistant/data/     本地学习数据，真实数据不提交
ai-learning-assistant/outputs/  后续生成的计划和总结文件
```

## 10. 如何回顾旧版本

每个重要学习节点会通过 Git tag 保留 checkpoint。

常见 tag 形式：

```text
lesson-X.Y
stage-X
```

例如：

```powershell
git checkout lesson-3.4
```

可以回到第 3.4 课完成后的代码状态。
