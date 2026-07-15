# 教程索引

这里是 `AI 学习助教` 项目驱动课程的学习入口。

课程主线：从 Python 基础开始，逐步进入 FastAPI、LLM 调用、LangChain、RAG、LangGraph 和 Deep Agents。

## 1. 推荐阅读顺序

如果你是第一次进入仓库，建议按这个顺序阅读：

1. [课程总纲](./ai-learning-assistant-course-plan.md)
2. 从第 0 阶段开始逐课学习
3. 每完成一个阶段，阅读对应阶段复盘
4. 需要回看代码时，使用对应 Git tag

当前最新复盘：

- [阶段 6 复盘：本地资料 RAG、向量检索与资料问答 API](./reviews/stage-6-review.md)

下一课：

- 第 7.1 课：LangGraph 核心模型（待生成）

## 2. 当前学习位置

- 当前阶段：阶段 6，RAG，已复盘
- 当前课程：阶段 6 复盘，已生成并验证
- 真实代码项目：`ai-learning-assistant/`
- 下一步建议：进入第 7.1 课 LangGraph 核心模型

## 3. 课程索引

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
| 5 | 5.2 | 创建第一个 LangChain Agent | `docs/tutorial/lessons/stage-5/05-02-first-langchain-agent.md` | 已生成 | 已验证 |
| 5 | 5.3 | Python 函数变成 LangChain 工具 | `docs/tutorial/lessons/stage-5/05-03-python-functions-as-tools.md` | 已生成 | 已验证 |
| 5 | 5.4 | 多工具调用 | `docs/tutorial/lessons/stage-5/05-04-multiple-tools.md` | 已生成 | 已验证 |
| 5 | 5.5 | 结构化 Agent 输出 | `docs/tutorial/lessons/stage-5/05-05-structured-agent-output.md` | 已生成 | 已验证 |
| 5 | 5.6 | CLI 接入 LangChain Agent | `docs/tutorial/lessons/stage-5/05-06-cli-agent-integration.md` | 已生成 | 已验证 |
| 5 | 5.7 | FastAPI 接入 LangChain Agent | `docs/tutorial/lessons/stage-5/05-07-fastapi-agent-integration.md` | 已生成 | 已验证 |
| 6 | 6.1 | RAG 是什么 | `docs/tutorial/lessons/stage-6/06-01-rag-concepts.md` | 已生成 | 已验证 |
| 6 | 6.2 | 本地资料加载 | `docs/tutorial/lessons/stage-6/06-02-local-material-loading.md` | 已生成 | 已验证 |
| 6 | 6.3 | 文档切分 | `docs/tutorial/lessons/stage-6/06-03-document-splitting.md` | 已生成 | 已验证 |
| 6 | 6.4 | 向量检索 | `docs/tutorial/lessons/stage-6/06-04-vector-retrieval.md` | 已生成 | 已验证 |
| 6 | 6.5 | 基于资料回答 | `docs/tutorial/lessons/stage-6/06-05-grounded-material-answer.md` | 已生成 | 已验证 |
| 6 | 6.6 | RAG API | `docs/tutorial/lessons/stage-6/06-06-rag-api.md` | 已生成 | 已验证 |
| 7 | 7.1 | LangGraph 核心模型 | `docs/tutorial/lessons/stage-7/07-01-langgraph-core-model.md` | 待生成 | 待验证 |

## 4. 阶段复盘

| 阶段 | 文档 |
| --- | --- |
| 0 | [阶段 0 复盘：环境与项目初始化](./reviews/stage-0-review.md) |
| 1 | [阶段 1 复盘：Python 基础与 CLI 学习助手](./reviews/stage-1-review.md) |
| 2 | [阶段 2 复盘：Python 工程化与文件持久化](./reviews/stage-2-review.md) |
| 3 | [阶段 3 复盘：FastAPI 基础与学习助手 API](./reviews/stage-3-review.md) |
| 4 | [阶段 4 复盘：LLM 基础、结构化输出与 AI 建议入口](./reviews/stage-4-review.md) |
| 5 | [阶段 5 复盘：LangChain Agent、工具调用与双入口](./reviews/stage-5-review.md) |
| 6 | [阶段 6 复盘：本地资料 RAG、向量检索与资料问答 API](./reviews/stage-6-review.md) |

## 5. 补充学习资料

| 阶段 | 资料 | 路径 | 用途 |
| --- | --- | --- | --- |
| 2 | Stage 2 补充学习资料：模块导入与 JSON 文件保存 | `ai-learning-assistant/materials/stage-2.md` | 回顾模块导入、`Path`、JSON、异常处理、pytest 基础和当前数据流 |
| 3 | Stage 3 补充学习资料：FastAPI、Pydantic 与接口测试 | `ai-learning-assistant/materials/stage-3.md` | 回顾 FastAPI route、Pydantic 模型、状态码、`TestClient`、虚拟环境和 API 数据流 |
| 4 | Stage 4 补充学习资料：LLM 调用、结构化输出与 AI 建议入口 | `ai-learning-assistant/materials/stage-4.md` | 回顾 provider 配置、模型调用、JSON Schema、结构化校验、CLI/API AI 建议入口和当前数据流 |
| 5 | Stage 5 补充学习资料：LangChain Agent、注解式工具与双入口 | `ai-learning-assistant/materials/stage-5.md` | 回顾 `@tool`、`@dynamic_prompt`、`@wrap_tool_call`、结构化输出、provider 兼容、CLI/API 复用和错误边界 |
| 6 | Stage 6 补充学习资料：基础 RAG 检索、回答与 API | `ai-learning-assistant/materials/stage-6.md` | 回顾 Document、chunk、embedding、内存向量检索、`MaterialAnswer`、`POST /ask-materials` 和当前 RAG 边界 |

## 6. 目录说明

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
│   ├── stage-6/
│   └── ...
└── reviews/
    ├── stage-0-review.md
    ├── stage-1-review.md
    ├── stage-2-review.md
    ├── stage-3-review.md
    ├── stage-4-review.md
    ├── stage-5-review.md
    ├── stage-6-review.md
    └── ...
```

真实代码项目：

```text
ai-learning-assistant/
```

每一课都围绕这份真实代码继续迭代，不维护按小节复制出来的代码目录。
