# 阶段 2 复盘：Python 工程化与文件持久化

## 1. 阶段目标

阶段 2 的目标是把阶段 1 的单文件 CLI 程序，升级成一个更接近真实项目的小型 Python 应用。

本阶段重点不在新增复杂业务，而在建立后续 FastAPI、LangChain、LangGraph 和 Deep Agents 都会依赖的工程基础：

- 把入口、交互、状态和存储拆到不同模块。
- 用 JSON 文件保存学员资料和学习笔记。
- 处理文件不存在、JSON 损坏、字段缺失等基础异常。
- 用 `TypedDict` 表达核心数据结构。
- 用 pytest 为存储模块建立第一批自动化测试。

## 2. 已生成课程

| 小节 | 标题 | 文档 | 状态 |
| --- | --- | --- | --- |
| 2.1 | 模块拆分 | `docs/tutorial/lessons/stage-2/02-01-module-split.md` | 已生成 / 已验证 |
| 2.2 | JSON 文件读写 | `docs/tutorial/lessons/stage-2/02-02-json-file-io.md` | 已生成 / 已验证 |
| 2.3 | 异常处理 | `docs/tutorial/lessons/stage-2/02-03-exception-handling.md` | 已生成 / 已验证 |
| 2.4 | 类型标注 | `docs/tutorial/lessons/stage-2/02-04-type-hints.md` | 已生成 / 已验证 |
| 2.5 | 简单 pytest | `docs/tutorial/lessons/stage-2/02-05-simple-pytest.md` | 已生成 / 已验证 |

## 3. 补充学习资料

阶段 2 额外沉淀了一份补充资料：

```text
ai-learning-assistant/materials/stage-2.md
```

它适合在完成 2.1 到 2.5 之后回看，重点解释：

- `from app.student_state import student` 为什么是模块路径，不是文件路径。
- `__all__` 的作用和限制。
- PyCharm 中 `app` 无法解析时如何设置源码根目录。
- `Path("data/student.json")`、`exists()`、`mkdir()`、`open()` 的含义。
- `json.load()`、`json.dump()`、`json.loads()`、`json.dumps()` 的区别。
- 为什么 `storage.py` 不应该直接调用 `input()`。
- `isinstance()`、`all()`、列表推导式和变量作用域。
- `try / except` 与坏 JSON 文件隔离。
- pytest 中 `assert`、`tmp_path` 和 `write_text()` 的用法。
- 当前项目从 CLI 输入到 JSON 保存、再到测试验证的完整数据流。

## 4. 当前项目能力

阶段 2 完成后，`AI 学习助教` 已经具备：

- 通过 `py -3.13 -m app.main` 以模块方式运行 CLI。
- 用 `app/main.py` 保持入口职责。
- 用 `app/cli.py` 处理命令行输入、输出和菜单流程。
- 用 `app/student_state.py` 保存当前运行中的学员状态。
- 用 `app/storage.py` 负责 JSON 文件读写、默认值、结构校验、结构修复和坏文件隔离。
- 用 `app/models.py` 中的 `Student` 描述学员数据结构。
- 把学习数据保存到 `data/student.json`，下一次启动时自动加载。
- 在 JSON 损坏时把坏文件移动到 `data/student.broken.json`，程序用默认数据继续运行。
- 在字段缺失或笔记列表混入非字符串时做基础归一化。
- 用 `tests/test_storage.py` 验证存储模块的关键路径。

## 5. 当前代码入口

真实代码仍然只有一份：

```text
ai-learning-assistant/
```

核心入口：

```text
ai-learning-assistant/app/main.py
```

运行方式：

```powershell
cd ai-learning-assistant
py -3.13 -m app.main
```

测试方式：

```powershell
cd ai-learning-assistant
py -3.13 -m pytest
```

## 6. 验证命令与结果

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
```

结果：

```text
5 passed
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/__init__.py tests/test_storage.py
```

结果：通过。

CLI 冒烟测试：

```powershell
"2`n4" | py -3.13 -m app.main
```

结果：通过，程序可以启动、读取当前学习档案并退出。

## 7. 已知限制

- 目前仍是 CLI 项目，还没有 HTTP API。
- `Student` 仍是 `TypedDict`，还没有切换到 Pydantic 模型。
- 本地 JSON 文件只是入门级持久化，还不是数据库。
- `backup_broken_data()` 只保留单份 `student.broken.json`，再次遇到坏文件会覆盖旧的坏文件。
- pytest 当前只覆盖 `storage.py`，还没有覆盖 CLI 交互。
- 没有 FastAPI、LangChain、LangGraph 或 Deep Agents 依赖。

这些限制符合 Stage 2 范围。下一阶段会进入 FastAPI，把当前 CLI 能力逐步暴露成 API。

## 8. 后续升级关系

| Stage 2 概念 | 后续升级 |
| --- | --- |
| `app/main.py` 入口 | FastAPI 应用入口 |
| `cli.py` 交互层 | API route 层 |
| `storage.py` 存储层 | repository / service 层 |
| `Student` `TypedDict` | Pydantic request / response model |
| `data/student.json` | 数据库、checkpoint 或 agent 文件系统 |
| `load_student()` | 查询学员资料工具 |
| `save_student()` | 更新学员资料 API / tool |
| `try / except` | API 错误响应、Agent 输出解析恢复 |
| `pytest` | API 测试、RAG 测试、LangGraph 节点测试 |
| `tmp_path` | 隔离 RAG 资料、Agent 文件输出和 checkpoint 测试 |

## 9. 下一步建议

下一阶段：Stage 3，FastAPI 基础。

先做第 3.1 课：FastAPI 入门，新增一个最小 API 应用和 `/health` 接口。随后再逐步把阶段 2 中已经稳定的学员资料、学习笔记和学习建议接成 HTTP API。
