# AI 学习助教教程索引

## 0. 使用方式

本目录用于沉淀“从 Python 到 LangChain / LangGraph / Deep Agents”的项目驱动教程。

开源仓库名：`agentic-learning-lab`

根目录 README：[../../README.md](../../README.md)

先读：

- [课程总纲](./ai-learning-assistant-course-plan.md)
- [阶段 0 复盘](./reviews/stage-0-review.md)

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

## 3. 阶段复盘

| 阶段 | 文档 |
| --- | --- |
| 0 | [阶段 0 复盘：环境与项目初始化](./reviews/stage-0-review.md) |
| 1 | [阶段 1 复盘：Python 基础与 CLI 学习助手](./reviews/stage-1-review.md) |

## 4. 当前学习位置

- 当前阶段：阶段 2 进行中
- 当前课程：第 2.3 课已生成并验证
- 开源仓库名：`agentic-learning-lab`
- 真实代码项目：`ai-learning-assistant/` 已创建
- 阶段复盘：`docs/tutorial/reviews/stage-0-review.md`、`docs/tutorial/reviews/stage-1-review.md`
- 下一步建议：进入第 2.4 课：类型标注
