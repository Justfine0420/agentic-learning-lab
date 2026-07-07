# 阶段 1 复盘：Python 基础与 CLI 学习助手

## 1. 阶段目标

阶段 1 的目标是用最小 Python 语法做出一个可交互的命令行学习助手。

本阶段不接入 FastAPI、LangChain、LangGraph、Deep Agents，也不保存文件。重点是把后续框架都会用到的基础概念先跑通。

## 2. 已生成课程

| 小节 | 标题 | 文档 | 状态 |
| --- | --- | --- | --- |
| 1.1 | 变量与输入输出 | `docs/tutorial/lessons/stage-1/01-01-variables-input-output.md` | 已生成 / 已验证 |
| 1.2 | 字典保存状态 | `docs/tutorial/lessons/stage-1/01-02-dictionary-state.md` | 已生成 / 已验证 |
| 1.3 | 列表与笔记 | `docs/tutorial/lessons/stage-1/01-03-lists-and-notes.md` | 已生成 / 已验证 |
| 1.4 | 函数拆分 | `docs/tutorial/lessons/stage-1/01-04-function-extraction.md` | 已生成 / 已验证 |
| 1.5 | 条件判断 | `docs/tutorial/lessons/stage-1/01-05-conditional-suggestion.md` | 已生成 / 已验证 |
| 1.6 | 循环菜单 | `docs/tutorial/lessons/stage-1/01-06-loop-menu.md` | 已生成 / 已验证 |

## 3. 当前项目能力

阶段 1 完成后，`AI 学习助教` 已经具备：

- 通过命令行收集学员名字、学习目标和 Python 水平。
- 用 `student` 字典保存当前运行中的学员资料。
- 用 `student["notes"]` 列表保存当前运行中的学习笔记。
- 用函数拆分标题展示、资料收集、笔记添加、资料展示和学习建议。
- 用 `if/elif/else` 根据 Python 水平生成学习建议。
- 用 `while True` 提供可反复操作的菜单。

## 4. 当前代码入口

真实代码仍然只有一份：

```text
ai-learning-assistant/app/main.py
```

运行方式：

```powershell
cd ai-learning-assistant
py -3.13 app/main.py
```

## 5. 验证命令与结果

在 `ai-learning-assistant/` 下运行：

```powershell
"Alice`nLearn Python CLI`nbeginner`n2`n1`nFinish Stage 1`n2`n3`n9`n4" | py -3.13 app/main.py
```

关键结果：

```text
暂无笔记
已保存。
1. Finish Stage 1
建议：今天学习变量、函数、字典。
无效选项，请重新输入。
Alice，下次继续学习。
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py
```

结果：通过。

## 6. 已知限制

- 数据只保存在内存中，程序退出后会丢失。
- `student` 仍然是普通字典，还没有 Pydantic 模型。
- 代码仍然集中在 `app/main.py`，还没有拆成模块。
- 没有单元测试。
- 没有 FastAPI 接口。
- 没有 AI 模型调用。

这些限制符合 Stage 1 范围。Stage 2 会优先处理模块拆分、JSON 文件保存、异常处理和基础测试。

## 7. 后续升级关系

| Stage 1 概念 | 后续升级 |
| --- | --- |
| `student` 字典 | Pydantic Model / LangGraph State |
| `student["notes"]` 列表 | 笔记数据结构 / RAG 输入 |
| `add_note()` | FastAPI `POST /notes` / LangChain Tool |
| `show_profile()` | FastAPI `GET /profile` / 查询工具 |
| `suggest_next_step()` | 学习建议 API / LangGraph node |
| `if/elif/else` | LangGraph conditional edge |
| CLI 菜单 | FastAPI 路由入口 |

## 8. 下一步建议

下一阶段：Stage 2，Python 工程化。

先做第 2.1 课：模块拆分，把当前 `app/main.py` 中的职责拆到 `cli.py`、`student_state.py` 等文件里；随后第 2.2 课再引入 `storage.py` 做 JSON 文件读写。
