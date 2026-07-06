# AI 学习助教项目状态快照

## 0. 状态说明

本文件记录教程主线代码项目的当前状态。后续每生成一课，都必须先读本文件，再继续写教程或代码。

## 1. 当前进度

- 当前阶段：阶段 0：环境与项目初始化
- 当前小节：0.1 开发环境准备
- 最近生成课程：第 0.1 课：开发环境准备
- 开源仓库名：`agentic-learning-lab`
- 仓库 README：`README.md`
- 当前 Git 分支：`developer`
- 自归档授权：允许在 `developer` 分支自归档；禁止往 `master` 分支提交、打 tag 或推送；未明确要求 push 时只本地 commit。
- 真实代码项目路径：`ai-learning-assistant/`
- 真实代码项目状态：尚未创建
- 教程总纲：[ai-learning-assistant-course-plan.md](./ai-learning-assistant-course-plan.md)

## 2. 已实现能力

当前已完成：

- 教程规划和治理规则落盘。
- 第 0.1 课开发环境准备文档。

仓库治理能力：

- 已确定开源仓库名：`agentic-learning-lab`。
- 已创建根目录 `README.md`，说明课程定位、学习路线、目录结构、生成规则和当前状态。

## 3. 当前目录结构

教程文档当前结构：

```text
docs/tutorial/
├── ai-learning-assistant-course-plan.md
├── README.md
├── project-state.md
├── code-consistency-checklist.md
└── lessons/
    └── stage-0/
        └── 00-01-dev-environment.md
```

真实代码项目目标结构，正式开始第 0 阶段后创建：

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

## 4. 已创建文件

教程治理文件：

- `README.md`
- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`
- `docs/tutorial/lessons/stage-0/00-01-dev-environment.md`

真实项目代码文件：

- 暂无

## 5. 已安装依赖

暂无。依赖应在第 0 阶段正式初始化项目时写入 `ai-learning-assistant/requirements.txt`。

## 6. 已确认运行命令

已确认：

- `python --version` -> `Python 3.11.6`
- `py --version` -> `Python 3.13.3`

第 0.2 课创建虚拟环境时，优先使用 `py -3.13`。

## 7. 已知限制

- 仅生成了第 0.1 课，后续课程正文尚未生成。
- 真实代码项目尚未创建。
- LangChain、LangGraph、Deep Agents 相关课程生成前必须重新核对官方文档。

## 8. 下一课基线

下一课：第 0.2 课：项目目录设计

生成前必须读取：

- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`

生成后必须更新：

- 第 0.2 课文档
- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`
