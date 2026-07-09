# AI 学习助教教程索引

## 0. 使用方式

本目录用于沉淀“从 Python 到 LangChain / LangGraph / Deep Agents”的项目驱动教程。

开源仓库名：`agentic-learning-lab`

根目录 README：[../../README.md](../../README.md)

先读：

- [课程总纲](./ai-learning-assistant-course-plan.md)
- [阶段 0 复盘](./reviews/stage-0-review.md)
- [阶段 1 复盘](./reviews/stage-1-review.md)
- [阶段 2 复盘](./reviews/stage-2-review.md)
- [阶段 3 复盘](./reviews/stage-3-review.md)
- [阶段 4 复盘](./reviews/stage-4-review.md)
- [第 5.1 课：LangChain 定位](./lessons/stage-5/05-01-langchain-positioning.md)
- [阶段 2 补充学习资料](../../ai-learning-assistant/materials/stage-2.md)
- [阶段 3 补充学习资料](../../ai-learning-assistant/materials/stage-3.md)
- [阶段 4 补充学习资料](../../ai-learning-assistant/materials/stage-4.md)

学习方式：

- 按下方课程索引逐课阅读。
- 每课都在 `ai-learning-assistant/` 中运行对应命令。
- 阶段结束后阅读阶段复盘。
- 需要回看阶段代码时，使用仓库 tag。

## 1. 目录结构

```text
docs/tutorial/
├── ai-learning-assistant-course-plan.md
├── README.md
├── lessons/
│   ├── stage-0/
│   ├── stage-1/
│   ├── stage-2/
│   ├── stage-3/
│   ├── stage-4/
│   ├── stage-5/
│   └── ...
└── reviews/
    ├── stage-0-review.md
    ├── stage-1-review.md
    ├── stage-2-review.md
    └── ...
```

真实代码项目结构：

```text
ai-learning-assistant/
├── app/
├── data/
├── materials/
│   ├── stage-2.md
│   ├── stage-3.md
│   └── stage-4.md
├── outputs/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

## 2. 课程索引

| 阶段 | 小节 | 标题 | 文档路径 | 状态 | 验收 |
| --- | --- | --- | --- | --- | --- |
| 0 | 0.1 | 开发环境准备 | `docs/tutorial/lessons/stage-0/00-01-dev-environment.md` | 已生成 | 已验证 |
| 0 | 0.2 | 项目目录设计 | `docs/tutorial/lessons/stage-0/00-02-project-structure.md` | 已生成 | 已验证 |
| 0 | 0.3 | 第一个健康检查脚本 | `docs/tutorial/lessons/stage-0/00-03-health-check.md` | 已生成 | 已验证 |
| 1 | 1.1 | 变量与输入输出 | `docs/tutorial/lessons/stage-1/01-01-variables-input-output.md` | 已生成 | 已验证 |
| 1 | 1.2 | 字典保存状态 | `docs/tutorial/lessons/stage-1/01-02-dictionary-state.md` | 已生成 | 已验证 |
| 1 | 1.3 | 列表与笔记 | `docs/tutorial/lessons/stage-1/01-03-lists-and-notes.md` | 已生成 | 已验证 |
| 1 | 1.4 | 函数拆分 | `docs/tutorial/lessons/stage-1/01-04-function-extraction.md` | 已生成 | 已验证 |
| 1 | 1.5 | 条件判断 | `docs/tutorial/lessons/stage-1/01-05-conditional-suggestion.md` | 已生成 | 已验证 |
| 1 | 1.6 | 循环菜单 | `docs/tutorial/lessons/stage-1/01-06-loop-menu.md` | 已生成 | 已验证 |
| 2 | 2.1 | 模块拆分 | `docs/tutorial/lessons/stage-2/02-01-module-split.md` | 已生成 | 已验证 |
| 2 | 2.2 | JSON 文件读写 | `docs/tutorial/lessons/stage-2/02-02-json-file-io.md` | 已生成 | 已验证 |
| 2 | 2.3 | 异常处理 | `docs/tutorial/lessons/stage-2/02-03-exception-handling.md` | 已生成 | 已验证 |
| 2 | 2.4 | 类型标注 | `docs/tutorial/lessons/stage-2/02-04-type-hints.md` | 已生成 | 已验证 |
| 2 | 2.5 | 简单 pytest | `docs/tutorial/lessons/stage-2/02-05-simple-pytest.md` | 已生成 | 已验证 |
| 3 | 3.1 | FastAPI 入门 | `docs/tutorial/lessons/stage-3/03-01-fastapi-first-api.md` | 已生成 | 已验证 |
| 3 | 3.2 | Pydantic 模型 | `docs/tutorial/lessons/stage-3/03-02-pydantic-models.md` | 已生成 | 已验证 |
| 3 | 3.3 | 学员资料 API | `docs/tutorial/lessons/stage-3/03-03-profile-api.md` | 已生成 | 已验证 |
| 3 | 3.4 | 学习笔记 API | `docs/tutorial/lessons/stage-3/03-04-notes-api.md` | 已生成 | 已验证 |
| 3 | 3.5 | 学习建议 API | `docs/tutorial/lessons/stage-3/03-05-suggestion-api.md` | 已生成 | 已验证 |
| 3 | 3.6 | API 错误处理 | `docs/tutorial/lessons/stage-3/03-06-api-error-handling.md` | 已生成 | 已验证 |
| 3 | 3.7 | 存储边界与数据库迁移预告 | `docs/tutorial/lessons/stage-3/03-07-storage-boundary-database-preview.md` | 已生成 | 已验证 |
| 4 | 4.1 | LLM 基础概念 | `docs/tutorial/lessons/stage-4/04-01-llm-basic-concepts.md` | 已生成 | 已验证 |
| 4 | 4.2 | 配置 LLM Provider 和 API Key | `docs/tutorial/lessons/stage-4/04-02-configure-api-key.md` | 已生成 | 已验证 |
| 4 | 4.3 | 第一次模型调用 | `docs/tutorial/lessons/stage-4/04-03-first-llm-call.md` | 已生成 | 已验证 |
| 4 | 4.4 | 结构化输出 | `docs/tutorial/lessons/stage-4/04-04-structured-output.md` | 已生成 | 已验证 |
| 4 | 4.5 | AI 建议 API、CLI 入口与降级边界 | `docs/tutorial/lessons/stage-4/04-05-ai-suggestion-api.md` | 已生成 | 已验证 |
| 5 | 5.1 | LangChain 定位 | `docs/tutorial/lessons/stage-5/05-01-langchain-positioning.md` | 已生成 | 已验证 |

## 3. 补充学习资料

| 阶段 | 资料 | 路径 | 用途 |
| --- | --- | --- | --- |
| 2 | Stage 2 补充学习资料：模块导入与 JSON 文件保存 | `ai-learning-assistant/materials/stage-2.md` | 回顾模块导入、`Path`、JSON、异常处理、pytest 基础和当前数据流 |
| 3 | Stage 3 补充学习资料：FastAPI、Pydantic 与接口测试 | `ai-learning-assistant/materials/stage-3.md` | 回顾 FastAPI route、Pydantic 模型、状态码、`TestClient`、虚拟环境和 API 数据流 |
| 4 | Stage 4 补充学习资料：LLM 调用、结构化输出与 AI 建议入口 | `ai-learning-assistant/materials/stage-4.md` | 回顾 provider 配置、模型调用、JSON Schema、结构化校验、CLI/API AI 建议入口和当前数据流 |

## 4. 阶段复盘

| 阶段 | 文档 |
| --- | --- |
| 0 | [阶段 0 复盘：环境与项目初始化](./reviews/stage-0-review.md) |
| 1 | [阶段 1 复盘：Python 基础与 CLI 学习助手](./reviews/stage-1-review.md) |
| 2 | [阶段 2 复盘：Python 工程化与文件持久化](./reviews/stage-2-review.md) |
| 3 | [阶段 3 复盘：FastAPI 基础与学习助手 API](./reviews/stage-3-review.md) |
| 4 | [阶段 4 复盘：LLM 基础、结构化输出与 AI 建议入口](./reviews/stage-4-review.md) |

## 5. 当前学习位置

- 当前阶段：阶段 5 进行中
- 当前课程：第 5.1 课已生成并验证
- 开源仓库名：`agentic-learning-lab`
- 真实代码项目：`ai-learning-assistant/` 已创建
- 阶段复盘：`docs/tutorial/reviews/stage-0-review.md`、`docs/tutorial/reviews/stage-1-review.md`、`docs/tutorial/reviews/stage-2-review.md`、`docs/tutorial/reviews/stage-3-review.md`、`docs/tutorial/reviews/stage-4-review.md`
- 补充资料：`ai-learning-assistant/materials/stage-2.md`、`ai-learning-assistant/materials/stage-3.md`、`ai-learning-assistant/materials/stage-4.md`
- 下一步建议：生成第 5.2 课，创建第一个 LangChain Agent
