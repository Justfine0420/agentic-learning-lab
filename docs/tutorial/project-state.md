# AI 学习助教项目状态快照

## 0. 状态说明

本文件记录教程主线代码项目的当前状态。后续每生成一课，都必须先读本文件，再继续写教程或代码。

## 1. 当前进度

- 当前阶段：阶段 0 已完成
- 当前小节：0.3 第一个健康检查脚本
- 最近生成课程：第 0.3 课：第一个健康检查脚本
- 开源仓库名：`agentic-learning-lab`
- 仓库 README：`README.md`
- 当前 Git 分支：`developer`
- 自归档授权：允许在 `developer` 分支 commit、tag 并 push 到 `origin developer`；禁止往 `master` 分支提交、打 tag 或推送。
- 真实代码项目路径：`ai-learning-assistant/`
- 真实代码项目状态：已创建，健康检查脚本已验证
- 教程总纲：[ai-learning-assistant-course-plan.md](./ai-learning-assistant-course-plan.md)

## 2. 已实现能力

当前已完成：

- 教程规划和治理规则落盘。
- 第 0.1 课开发环境准备文档。
- 第 0.2 课项目目录设计文档。
- 第 0.3 课健康检查脚本文档。
- `ai-learning-assistant/` 项目骨架。
- `ai-learning-assistant/app/main.py` 健康检查脚本。

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
├── lessons/
│   └── stage-0/
│       ├── 00-01-dev-environment.md
│       ├── 00-02-project-structure.md
│       └── 00-03-health-check.md
└── reviews/
    └── stage-0-review.md
```

真实代码项目当前结构：

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

## 4. 已创建文件

教程治理文件：

- `README.md`
- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`
- `docs/tutorial/lessons/stage-0/00-01-dev-environment.md`
- `docs/tutorial/lessons/stage-0/00-02-project-structure.md`
- `docs/tutorial/lessons/stage-0/00-03-health-check.md`
- `docs/tutorial/reviews/stage-0-review.md`

真实项目代码文件：

- `ai-learning-assistant/README.md`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/.env.example`
- `ai-learning-assistant/app/main.py`
- `ai-learning-assistant/data/.gitkeep`
- `ai-learning-assistant/materials/.gitkeep`
- `ai-learning-assistant/outputs/.gitkeep`
- `ai-learning-assistant/tests/.gitkeep`

## 5. 已安装依赖

暂无第三方依赖。`ai-learning-assistant/requirements.txt` 已创建，阶段 0 不需要安装包。

## 6. 已确认运行命令

已确认：

- `python --version` -> `Python 3.11.6`
- `py --version` -> `Python 3.13.3`
- `py -0p` -> 可用版本包含 Python 3.13 和 Python 3.11
- `py -3.13 app/main.py` -> 健康检查脚本运行成功

后续继续优先使用 `py -3.13`。

## 7. 已知限制

- 尚未创建 `.venv/`；阶段 0 只验证系统 Python 3.13。
- 尚未进入 Stage 1，未实现 CLI 学习助手。
- LangChain、LangGraph、Deep Agents 相关课程生成前必须重新核对官方文档。

## 8. 下一课基线

下一课：第 1.1 课：变量与输入输出

生成前必须读取：

- `docs/tutorial/ai-learning-assistant-course-plan.md`
- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`

生成后必须更新：

- 第 1.1 课文档
- `docs/tutorial/README.md`
- `docs/tutorial/project-state.md`
- `docs/tutorial/code-consistency-checklist.md`
