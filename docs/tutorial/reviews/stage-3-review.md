# 阶段 3 复盘：FastAPI 基础与学习助手 API

## 1. 阶段目标

阶段 3 的目标是把前两阶段已经稳定的 CLI 学习助手，升级成可以通过 HTTP 调用的 FastAPI API。

本阶段重点不是引入 AI，也不是急着做数据库，而是先建立后续 LLM、LangChain、RAG、LangGraph 和 Deep Agents 都会依赖的 API 基础：

- 用 `FastAPI()` 创建 Web API 应用。
- 用 `@app.get()` 和 `@app.post()` 把 Python 函数注册成接口。
- 用 Pydantic 模型校验请求体和响应体。
- 把学员资料、学习笔记和学习建议暴露成 API。
- 用 `HTTPException` 区分业务错误和自动校验错误。
- 用 `TestClient` 为 API 建立自动化测试。
- 明确当前 JSON 存储边界，为后续数据库迁移和 Agent 工具调用留出接口。

## 2. 已生成课程

| 小节 | 标题 | 文档 | 状态 |
| --- | --- | --- | --- |
| 3.1 | FastAPI 入门 | `docs/tutorial/lessons/stage-3/03-01-fastapi-first-api.md` | 已生成 / 已验证 |
| 3.2 | Pydantic 模型 | `docs/tutorial/lessons/stage-3/03-02-pydantic-models.md` | 已生成 / 已验证 |
| 3.3 | 学员资料 API | `docs/tutorial/lessons/stage-3/03-03-profile-api.md` | 已生成 / 已验证 |
| 3.4 | 学习笔记 API | `docs/tutorial/lessons/stage-3/03-04-notes-api.md` | 已生成 / 已验证 |
| 3.5 | 学习建议 API | `docs/tutorial/lessons/stage-3/03-05-suggestion-api.md` | 已生成 / 已验证 |
| 3.6 | API 错误处理 | `docs/tutorial/lessons/stage-3/03-06-api-error-handling.md` | 已生成 / 已验证 |
| 3.7 | 存储边界与数据库迁移预告 | `docs/tutorial/lessons/stage-3/03-07-storage-boundary-database-preview.md` | 已生成 / 已验证 |

## 3. 补充学习资料

阶段 3 额外沉淀了一份补充资料：

```text
ai-learning-assistant/materials/stage-3.md
```

它适合在完成 3.1 到 3.7 之后回看，重点解释：

- `FastAPI()`、`@app.get()`、`@app.post()` 的角色。
- 路由装饰器如何把普通 Python 函数注册成 API。
- 请求模型和响应模型为什么要分开。
- `BaseModel`、`Field()`、`Field(default_factory=list)` 的用法。
- `model_dump()` 和 `**dict` 如何把 Pydantic 对象转换为构造参数。
- `response_model` 为什么会校验返回值，错误结构为什么可能导致 `500`。
- `HTTPException`、`raise`、`400`、`404`、`422`、`500` 的区别。
- `TestClient` 如何在不启动 uvicorn 的情况下测试 API。
- `.venv`、解释器选择、`python -m` 和 `pip install -r requirements.txt` 的关系。
- 当前项目从 API 请求到 JSON 存储再到响应返回的完整数据流。

## 4. 当前项目能力

阶段 3 完成后，`AI 学习助教` 已经具备：

- 通过 `app/api.py` 创建 FastAPI 应用。
- 提供健康检查接口：`GET /health`。
- 提供请求体和响应模型示例接口：`POST /profile/preview`。
- 提供学员资料接口：`GET /profile`、`POST /profile`。
- `POST /profile` 可以更新学员资料，并保留已有学习笔记。
- 提供学习笔记接口：`GET /notes`、`GET /notes/{note_index}`、`POST /notes`。
- `POST /notes` 可以追加学习笔记，并保留已有学员资料。
- 提供学习建议接口：`GET /suggestion`。
- 把学习建议规则抽到 `app/suggestions.py`，供 CLI 和 API 共用。
- 用 `StudentProfile`、`StudentProfileResponse`、`NoteCreate`、`NotesResponse`、`NoteResponse` 和 `SuggestionResponse` 表达 API 数据结构。
- 用 `HTTPException` 为学习笔记接口返回 `400` 和 `404` 业务错误。
- 保留 FastAPI / Pydantic 自动返回 `422` 的请求校验能力。
- 用 `tests/test_api.py` 覆盖主要 API 路径。
- 继续通过 `storage.py` 读写 `data/student.json`，API 层不直接操作 JSON 文件。

## 5. 当前 API 入口

真实代码仍然只有一份：

```text
ai-learning-assistant/
```

API 入口：

```text
ai-learning-assistant/app/api.py
```

启动 API：

```powershell
cd ai-learning-assistant
py -3.13 -m uvicorn app.api:app --reload
```

主要接口：

```text
GET  /health
POST /profile/preview
GET  /profile
POST /profile
GET  /notes
GET  /notes/{note_index}
POST /notes
GET  /suggestion
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
23 passed
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

结果：通过。

API 存储边界检查：

```powershell
rg "json|open\\(" app/api.py
```

结果：无输出，说明当前 API 层没有直接读写 JSON 文件。

## 7. 已知限制

- 当前 API 仍然是单用户学习助手，不支持登录和多用户隔离。
- 当前持久化仍然使用 `data/student.json`，不是数据库。
- `storage.py` 是当前最小存储边界，还没有正式拆成 repository 层。
- API 错误处理只覆盖了学习笔记缺失和空白笔记等基础业务错误。
- 当前学习建议仍是规则函数，不是 LLM 生成。
- 当前没有 `llm.py`、没有 API Key 配置，也没有真实模型调用。
- 当前没有 LangChain、RAG、LangGraph 或 Deep Agents 依赖。
- `.venv/` 还未作为课程步骤正式创建，本地解释器和依赖安装仍以命令说明为主。

这些限制符合 Stage 3 范围。下一阶段会进入 LLM 基础，先理解模型调用、prompt、message、token 和 API Key，再把规则学习建议升级为 AI 生成。

## 8. 后续升级关系

| Stage 3 概念 | 后续升级 |
| --- | --- |
| FastAPI route | LLM / Agent API 入口 |
| Pydantic request model | 结构化输入、工具参数、Graph State |
| Pydantic response model | 结构化输出、Agent 返回契约 |
| `HTTPException` | AI 调用失败、工具失败和流程失败的 API 表达 |
| `TestClient` | LLM API、RAG API、Graph API 测试 |
| `storage.py` | repository、数据库、LangChain 工具数据源 |
| `GET /suggestion` | LLM 生成学习建议 |
| `data/student.json` | 数据库、RAG 资料来源、LangGraph checkpoint 前置理解 |

## 9. 下一步建议

下一阶段：Stage 4，LLM 基础。

先做第 4.1 课：LLM 基础概念。不要急着写模型调用代码，先把 `model`、`prompt`、`message`、`token`、`instructions`、`input` 和响应结果这些词讲清楚。

随后再进入 API Key 配置、第一次真实模型调用和结构化输出。
