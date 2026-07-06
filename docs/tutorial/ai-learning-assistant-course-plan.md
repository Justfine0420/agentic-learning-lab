# AI 学习助教项目驱动教程规划

## 0. 文档状态

- 版本：v0.1
- 最近更新：2026-07-06
- 用途：作为“从 Python 到 LangChain / LangGraph / Deep Agents”的系统学习路线总纲。
- 范围：只规划课程链路、项目结构、阶段产物和验收标准；不包含每一课的完整正文。

## 1. 课程定位

这套教程采用项目驱动方式，不把 Python、FastAPI、LangChain、LangGraph、Deep Agents 拆成孤立概念讲解。所有内容围绕同一个贯穿项目逐步升级。

贯穿项目：`AI 学习助教`

最终系统能力：

- CLI 可用。
- FastAPI 可调用。
- 能保存学员信息和学习笔记。
- 能读取本地学习资料。
- 能用 LangChain 调用模型和工具。
- 能用 RAG 基于资料答疑。
- 能用 LangGraph 管理学习流程。
- 能用 Deep Agents 拆任务、写计划、生成总结文件。
- 有基础测试、运行说明和交付文档。

## 2. 框架边界

- LangChain：模型调用、工具、消息、`create_agent`、结构化输出和 agent harness。
- LangGraph：有状态流程编排，核心是 `State`、node、edge、条件分支、checkpoint、streaming 和 human-in-the-loop。
- Deep Agents：更高层的 agent harness，内置规划、文件系统、子 Agent、上下文管理和长期任务能力。

本教程不把三者讲成并列框架。它们是分层体系：LangChain 解决模型与工具调用，LangGraph 解决可控流程，Deep Agents 解决更复杂的长期任务执行。

## 3. 推荐项目结构

```text
ai-learning-assistant/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── storage.py
│   ├── cli.py
│   ├── llm.py
│   ├── langchain_agent.py
│   ├── rag.py
│   ├── graph.py
│   ├── deep_agent.py
│   └── config.py
├── data/
│   └── student.json
├── materials/
│   └── python_basics.md
├── outputs/
│   ├── study_plan.md
│   └── study_summary.md
├── tests/
│   ├── test_storage.py
│   ├── test_api.py
│   ├── test_rag.py
│   └── test_graph.py
├── requirements.txt
├── .env.example
└── README.md
```

## 4. 总路线

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

## 5. 完整课程规划

| 课 | 标题 | 核心内容 | 产物 |
| --- | --- | --- | --- |
| 0.1 | 开发环境准备 | Python、虚拟环境、包管理、编辑器 | 可运行 Python 项目 |
| 0.2 | 项目目录设计 | `app/`、`data/`、`tests/`、`materials/` | 初始化目录 |
| 0.3 | 第一个健康检查脚本 | `main.py`、运行命令、错误排查 | `python app/main.py` 可运行 |
| 1.1 | 变量与输入输出 | `input`、`print`、字符串 | 收集学员姓名 |
| 1.2 | 字典保存状态 | `student` 字典 | 保存学员资料 |
| 1.3 | 列表与笔记 | `list`、`append`、遍历 | 添加学习笔记 |
| 1.4 | 函数拆分 | `ask_profile()`、`add_note()` | CLI 功能模块化 |
| 1.5 | 条件判断 | `if/elif/else` | 生成学习建议 |
| 1.6 | 循环菜单 | `while True`、退出条件 | 完整 CLI 助手 |
| 2.1 | 模块拆分 | `cli.py`、`storage.py` | 代码不再堆一个文件 |
| 2.2 | JSON 文件读写 | `json.load`、`json.dump` | 数据重启不丢 |
| 2.3 | 异常处理 | 文件不存在、JSON 错误 | 程序更稳 |
| 2.4 | 类型标注 | `dict[str, str]`、`list[str]` | 为 Pydantic 和 State 铺路 |
| 2.5 | 简单 pytest | 单元测试、断言 | `test_storage.py` |
| 3.1 | FastAPI 入门 | app、route、uvicorn | `/health` |
| 3.2 | Pydantic 模型 | 请求体、响应模型 | `StudentProfile` |
| 3.3 | 学员资料 API | `GET/POST /profile` | API 管理资料 |
| 3.4 | 学习笔记 API | `GET/POST /notes` | API 管理笔记 |
| 3.5 | 学习建议 API | `GET /suggestion` | 规则建议接口 |
| 3.6 | API 错误处理 | 404、400、异常响应 | 稳定 API |
| 4.1 | LLM 基础概念 | prompt、message、model、token | 理解模型调用 |
| 4.2 | 配置 API Key | `.env`、环境变量 | 安全加载配置 |
| 4.3 | 第一次模型调用 | 封装 `llm.py` | AI 生成建议 |
| 4.4 | 结构化输出 | JSON schema / Pydantic | 稳定返回学习建议 |
| 5.1 | LangChain 定位 | `create_agent`、agent harness | 理解框架边界 |
| 5.2 | 创建第一个 Agent | model + prompt | AI 助手入口 |
| 5.3 | Python 函数变工具 | tool 思路 | 查询学员资料工具 |
| 5.4 | 多工具调用 | 查资料、查笔记、生成建议 | 工具型 AI 助手 |
| 5.5 | 结构化 Agent 输出 | 学习计划结构 | 可解析结果 |
| 5.6 | FastAPI 接入 Agent | `POST /chat` | API 调 AI 助手 |
| 6.1 | RAG 是什么 | 文档、chunk、embedding、retriever | 理解资料问答 |
| 6.2 | 本地资料加载 | `materials/*.md` | 加载学习资料 |
| 6.3 | 文档切分 | chunk size、overlap | 可检索片段 |
| 6.4 | 向量检索 | embedding、vector store | 找相关资料 |
| 6.5 | 基于资料回答 | answer + sources | 不凭空答疑 |
| 6.6 | RAG API | `POST /ask-materials` | 资料问答接口 |
| 7.1 | LangGraph 核心模型 | State、node、edge | 理解图结构 |
| 7.2 | 定义 LearningState | TypedDict / Pydantic 思路 | 学习流程状态 |
| 7.3 | 第一个节点 | 判断学习水平 | `assess_level` |
| 7.4 | 多节点流程 | 教学、出题、批改 | 基础学习流程 |
| 7.5 | 条件分支 | 答对/答错走不同路径 | 个性化流程 |
| 7.6 | FastAPI 调 Graph | `POST /study/session` | API 驱动流程 |
| 8.1 | Checkpoint | 保存流程进度 | 可恢复学习会话 |
| 8.2 | Streaming | 流式输出过程 | 前端友好 |
| 8.3 | Human-in-the-loop | 人工确认、人工改答案 | 可控流程 |
| 8.4 | 错误恢复 | 节点失败、重试、降级 | 稳定流程 |
| 8.5 | Graph 测试 | 测节点、测分支 | `test_graph.py` |
| 9.1 | Deep Agents 定位 | planning、filesystem、subagents | 理解高层 Agent |
| 9.2 | 第一个 Deep Agent | 复杂任务输入 | 自动规划学习任务 |
| 9.3 | 文件系统能力 | 写 `study_plan.md` | 生成学习计划文件 |
| 9.4 | 子 Agent | 研究 Agent、审查 Agent | 拆任务协作 |
| 9.5 | 长任务总结 | 多步研究、输出总结 | `study_summary.md` |
| 10.1 | 系统整合 | API、RAG、Graph、Deep Agent | 统一后端 |
| 10.2 | 学习助教主流程 | 问答、资料、流程、计划 | 主业务闭环 |
| 10.3 | 配置与依赖整理 | requirements、`.env.example` | 可复现环境 |
| 10.4 | README 编写 | 安装、运行、接口说明 | 可交付说明 |
| 10.5 | 最终验收 | 全链路跑通 | 完整项目 |
| 11.1 | 单元测试 | storage、models、graph | 基础测试 |
| 11.2 | API 测试 | FastAPI TestClient | 接口测试 |
| 11.3 | AI 功能人工验收 | 固定输入、期望输出 | 人工验收清单 |
| 11.4 | 后续扩展设计 | 前端、数据库、登录、多用户 | 下一阶段路线 |

## 6. 概念升级主线

| 早期概念 | 后续升级 |
| --- | --- |
| `student` 字典 | Pydantic Model / LangGraph State |
| Python 函数 | LangChain Tool / LangGraph node |
| `if/else` | LangGraph conditional edge |
| JSON 文件 | 简单持久化 / checkpoint 前置理解 |
| 本地 Markdown | RAG 知识库 |
| CLI 菜单 | FastAPI 路由 |
| 学习建议函数 | LLM Agent |
| 学习流程 | LangGraph 状态机 |
| 生成学习计划 | Deep Agents 长任务 |

## 7. 每课固定模板

后续正式生成教程正文时，每一课都按以下结构输出：

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
```

## 8. 阶段验收标准

| 阶段 | 验收标准 |
| --- | --- |
| 1 | 能用 CLI 添加资料、添加笔记、查看建议 |
| 2 | 重启程序后数据不丢 |
| 3 | FastAPI 能提供资料、笔记、建议接口 |
| 4 | AI 能生成结构化学习建议 |
| 5 | LangChain Agent 能调用工具查询资料 |
| 6 | RAG 回答必须带资料来源 |
| 7 | LangGraph 能跑完整学习流程 |
| 8 | 学习流程能恢复、分支、人工介入 |
| 9 | Deep Agent 能写学习计划文件 |
| 10 | 一个 API 服务串起所有能力 |
| 11 | 有测试、README、运行说明 |

## 9. 后续使用方式

用户可以按以下方式请求后续内容：

```text
开始第 0.1 课
继续下一课
生成第 3 阶段 FastAPI 课程
复习 LangGraph 阶段
给我第 5 阶段练习题
```

每次生成课程正文时，应先核对本规划，并根据当前官方文档确认 LangChain、LangGraph、Deep Agents 的推荐 API，避免使用过时写法。

## 10. 生成、回顾和代码主线规则

后续教程生成必须依赖以下治理文档：

- [教程索引](./README.md)
- [项目状态快照](./project-state.md)
- [代码一致性检查清单](./code-consistency-checklist.md)

生成规则：

- 每个小节单独归档到 `docs/tutorial/lessons/stage-X/`。
- 每个阶段结束后生成 `docs/tutorial/reviews/stage-X-review.md`。
- 代码只维护一份真实主线项目：`ai-learning-assistant/`。
- 不创建 `lesson-01-code/`、`lesson-02-code/` 这类课程代码副本。
- 每课如果涉及代码，必须同步更新真实项目代码、教程小节、教程索引、项目状态快照和一致性检查结果。
- 每课文档必须包含“本课变更清单”，记录新增文件、修改文件、新增依赖、验证命令、验证结果和下一课依赖。
- 不强制每个小节 commit 或打 tag；纯文档小节只记录变更，代码里程碑和阶段完成时再建议 commit / tag。
- 需要 commit、tag、push 或其它归档性 Git 操作时，必须先提示用户确认；只有用户明确授权“后续自归档”并写清触发条件、范围和命名规则后，才可自动执行。
- 当前已授权后续自归档：教程治理文档、课程正文或 `ai-learning-assistant/` 真实代码项目推进到可归档节点时，可在 `developer` 分支 commit、tag 并 push 到 `origin developer`。禁止往 `master` 分支提交、打 tag 或推送；如果当前分支不是 `developer`，必须停止并提示用户。
- Commit message 使用 `<type>(<scope>): <summary>` 格式；具体 type、scope 和示例以 `docs/tutorial/code-consistency-checklist.md` 为准。

生成一课前必须读取：

1. 本课程总纲。
2. `docs/tutorial/README.md`。
3. `docs/tutorial/project-state.md`。
4. `docs/tutorial/code-consistency-checklist.md`。
5. 上一课文档；如果是阶段第一课，则读取上一阶段 review。

生成一课后必须更新：

1. 本课 Markdown 文档。
2. `docs/tutorial/README.md` 的课程索引和更新记录。
3. `docs/tutorial/project-state.md` 的当前进度、目录结构、文件清单、依赖和运行命令。
4. `docs/tutorial/code-consistency-checklist.md` 中与本课相关的检查结果或遗留风险。

阶段结束后必须生成阶段复盘，说明本阶段新增能力、代码是否连贯、实际运行过的命令、常见错误、遗留问题和是否可以进入下一阶段。
