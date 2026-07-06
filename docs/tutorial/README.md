# AI 学习助教教程索引

## 0. 使用方式

本目录用于沉淀“从 Python 到 LangChain / LangGraph / Deep Agents”的项目驱动教程。

开源仓库名：`agentic-learning-lab`

根目录 README：[../../README.md](../../README.md)

先读：

- [课程总纲](./ai-learning-assistant-course-plan.md)
- [项目状态快照](./project-state.md)
- [代码一致性检查清单](./code-consistency-checklist.md)

后续每生成一课，都必须更新本索引和项目状态快照。

## 1. 生成规则

- 每个小节单独归档到 `docs/tutorial/lessons/stage-X/`。
- 每个阶段结束后单独生成 `docs/tutorial/reviews/stage-X-review.md`。
- 代码只维护一份真实主线项目：`ai-learning-assistant/`。
- 不创建 `lesson-01-code/`、`lesson-02-code/` 这类课程代码副本。
- 每课如果涉及代码，必须同步更新真实项目代码、教程小节、本索引、项目状态快照和一致性检查结果。
- 不强制每个小节 commit 或打 tag；每小节必须记录变更，代码里程碑和阶段完成时再建议 commit / tag。
- 需要 commit、tag、push 或其它归档性 Git 操作时，必须先提示用户确认；只有用户明确授权“后续自归档”并写清触发条件和范围后，才可自动执行。
- 到 LangChain、LangGraph、Deep Agents 阶段时，生成课程前必须核对当前官方文档，避免使用过时 API。

## 2. 推荐目录结构

```text
docs/tutorial/
├── ai-learning-assistant-course-plan.md
├── README.md
├── project-state.md
├── code-consistency-checklist.md
├── lessons/
│   ├── stage-0/
│   ├── stage-1/
│   └── ...
└── reviews/
    ├── stage-0-review.md
    ├── stage-1-review.md
    └── ...
```

真实代码项目结构：

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

## 3. 课程索引

| 阶段 | 小节 | 标题 | 文档路径 | 状态 | 验收 |
| --- | --- | --- | --- | --- | --- |
| 0 | 0.1 | 开发环境准备 | `docs/tutorial/lessons/stage-0/00-01-dev-environment.md` | 未生成 | 未验证 |
| 0 | 0.2 | 项目目录设计 | `docs/tutorial/lessons/stage-0/00-02-project-structure.md` | 未生成 | 未验证 |
| 0 | 0.3 | 第一个健康检查脚本 | `docs/tutorial/lessons/stage-0/00-03-health-check.md` | 未生成 | 未验证 |

后续课程生成时，把新小节追加到本表；不要只依赖聊天记录。

## 4. 每课更新记录模板

生成每课后，在本节追加记录：

```text
YYYY-MM-DD
- 课程：
- 文档：
- 新增代码：
- 修改代码：
- 新增依赖：
- 验收命令：
- 验收结果：
- 下一课：
```

## 5. 当前进度

- 当前阶段：规划阶段
- 当前课程：尚未开始第 0.1 课
- 开源仓库名：`agentic-learning-lab`
- 根目录 README：已创建
- 真实代码项目：尚未创建
- 下一步建议：生成第 0.1 课并创建初始项目目录
