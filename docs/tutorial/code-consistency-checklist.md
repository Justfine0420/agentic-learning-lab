# 代码一致性检查清单

## 0. 使用原则

本清单用于防止分课生成教程时出现代码前后不一致、文件路径漂移、依赖遗漏或命令不可运行。

每生成一课，必须在课前和课后各检查一次。阶段结束时再做阶段级复盘。

## 1. 核心规则

- 教程文档按小节单独归档。
- 代码只保留一份真实主线项目：`ai-learning-assistant/`。
- 不创建按课程复制的代码目录，例如 `lesson-01-code/`、`lesson-02-code/`。
- 每课文档必须写清“本课变更清单”。
- 如果修改旧代码，必须说明为什么修改、影响哪些后续课程。
- 如果新增依赖，必须更新 `requirements.txt`，并在课程文档写明安装命令。
- 如果新增 API、模型或工具，必须检查命名与前文一致。
- 如果进入 LangChain、LangGraph、Deep Agents 阶段，必须先核对官方文档的推荐 API。

## 2. 课前检查

生成新课前，确认：

- [ ] 已读取 `docs/tutorial/ai-learning-assistant-course-plan.md`。
- [ ] 已读取 `docs/tutorial/README.md`。
- [ ] 已读取 `docs/tutorial/project-state.md`。
- [ ] 已读取上一课文档；如果是阶段第一课，读取上一阶段 review。
- [ ] 已确认当前真实代码项目路径是 `ai-learning-assistant/`。
- [ ] 已确认本课要新增或修改的文件范围。
- [ ] 已确认本课不会创建重复代码副本。
- [ ] 如涉及外部库或框架 API，已核对当前官方文档。

## 3. 课后检查

生成新课后，确认：

- [ ] 本课文档已落到 `docs/tutorial/lessons/stage-X/`。
- [ ] 本课文档包含固定章节：目标、能力、前置知识、概念、代码、运行、常见错误、练习、验收、后续关系、变更清单。
- [ ] 真实代码项目只在 `ai-learning-assistant/` 下推进。
- [ ] 新代码接着上一课文件结构写，没有改名漂移。
- [ ] import 路径与当前目录结构一致。
- [ ] `requirements.txt` 包含本课新增依赖。
- [ ] `.env.example` 包含本课新增环境变量。
- [ ] 示例命令能从项目根目录运行，或明确标记未验证原因。
- [ ] 示例输出和代码真实行为一致。
- [ ] 新增 API 与 Pydantic 模型、路由命名、返回结构一致。
- [ ] 新增 LangGraph State 字段与前文数据结构一致。
- [ ] 新增 LangChain tool 与真实 Python 函数能力一致。
- [ ] 新增 Deep Agents 文件输出路径与 `outputs/` 规划一致。
- [ ] 已更新 `docs/tutorial/README.md`。
- [ ] 已更新 `docs/tutorial/project-state.md`。

## 4. 阶段结束检查

每个阶段结束后，确认：

- [ ] 阶段内所有小节文档都已生成。
- [ ] 阶段内所有代码变更能连起来运行。
- [ ] 阶段验收命令已运行，或明确标记 `Unverified` 及原因。
- [ ] 阶段新增概念已反映在 `project-state.md`。
- [ ] 已生成 `docs/tutorial/reviews/stage-X-review.md`。
- [ ] 已列出下一阶段依赖的代码文件、命令和概念。

## 5. 每课变更清单模板

每个小节文档末尾必须包含：

```markdown
## 本课变更清单

新增文件：
- 

修改文件：
- 

新增依赖：
- 

新增命令：
- 

验证命令：
- 

验证结果：
- 

下一课依赖：
- 
```

## 6. Git 建议

不要强制每个小节都提交代码或打 tag。每小节必须有变更清单，但 Git 节点按实际代码价值控制：

- 纯教程文档小节：只更新文档、索引和项目状态，不需要 commit / tag，除非用户明确要求。
- 小代码增量小节：可在阶段内累积，用本课变更清单和 `project-state.md` 保持可追踪。
- 可运行里程碑小节：建议 commit，例如第一次 CLI 跑通、FastAPI 接口跑通、RAG 跑通、LangGraph 流程跑通。
- 阶段完成：建议 commit 并打阶段 tag，例如 `stage-1-complete`。
- 需要回滚演示或教学对照的关键课：可以打 lesson tag，但这是例外，不是默认动作。
- 需要提交到仓库、创建 tag、推送远端或执行任何归档性 Git 操作时，必须先提示用户确认；只有用户明确授权“后续自归档”或指定自动归档规则后，才可按授权范围自动执行。
- 自归档授权必须写清触发条件、操作范围、tag / commit 命名规则和是否允许 push；没有写清时，默认只提示不执行。
- 当前仓库已授权后续自归档：当教程治理文档、课程正文或 `ai-learning-assistant/` 真实代码项目推进到可归档节点时，可以在 `developer` 分支 commit、tag 并 push 到 `origin developer`。
- 自归档分支限制：只允许在 `developer` 分支执行 commit / tag / push；禁止往 `master` 分支提交、打 tag 或推送。若当前分支不是 `developer`，必须停止并提示用户切换或确认处理方式。
- 当前自归档命名规则：commit message 使用 `docs: ...`、`course: ...`、`code: ...`、`chore: ...` 前缀；阶段 tag 使用 `stage-X-complete`，里程碑 tag 使用 `milestone-<name>`。归档时 push 目标只允许是 `origin developer`；禁止使用 `git push origin master` 或等价操作。

推荐 tag 粒度：

```bash
git tag milestone-cli-runnable
git tag milestone-fastapi-runnable
git tag milestone-langgraph-flow
git tag stage-1-complete
```

如果未启用 git，则必须依靠每课变更清单、`project-state.md` 和阶段 review 保留可追踪记录。

## 7. 检查记录

### 2026-07-06：第 0.1 课

课前检查：

- [x] 已读取 `docs/tutorial/ai-learning-assistant-course-plan.md`。
- [x] 已读取 `docs/tutorial/README.md`。
- [x] 已读取 `docs/tutorial/project-state.md`。
- [x] 已读取 `docs/tutorial/code-consistency-checklist.md`。
- [x] 已确认当前真实代码项目路径是 `ai-learning-assistant/`。
- [x] 已确认本课不创建真实代码项目，不创建重复代码副本。
- [x] 已核对 Python 官方下载页和源码发布页。

课后检查：

- [x] 本课文档已落到 `docs/tutorial/lessons/stage-0/00-01-dev-environment.md`。
- [x] 本课文档包含固定章节和本课变更清单。
- [x] 真实代码项目尚未创建，符合第 0.1 课范围。
- [x] 未新增依赖。
- [x] 已更新 `docs/tutorial/README.md`。
- [x] 已更新 `docs/tutorial/project-state.md`。

验证结果：

- `python --version` -> `Python 3.11.6`
- `py --version` -> `Python 3.13.3`

归档判断：

- 本课是纯环境教程小节，无代码里程碑，不打 tag。
- 可在 `developer` 分支进行 commit 并 push 到 `origin developer` 归档；禁止推送到 `master`。
