# AI 学习助教

这是 Agentic Learning Lab 的贯穿教学项目。

当前阶段：阶段 4 进行中，已完成第 4.5 课 AI 建议 API 与降级边界。

## 当前能力

- 项目目录已创建。
- 可以通过命令行收集学员名字、学习目标和 Python 水平。
- 使用 `student` 字典保存当前学员资料。
- 可以添加一条学习笔记，并保存在 `student["notes"]` 列表中。
- 已把标题展示、资料收集、笔记添加和档案展示拆成独立函数。
- 可以根据 Python 水平输出今日学习建议。
- 提供循环菜单，可以反复添加笔记、查看资料、生成建议和退出。
- 已把入口、CLI 交互和学习状态拆分到不同模块：`main.py`、`cli.py`、`student_state.py`。
- 可以把学员资料和学习笔记保存到 `data/student.json`，下次运行时自动加载。
- 可以处理文件不存在、JSON 损坏和字段缺失等基础存储异常。
- 使用 `TypedDict` 描述 `Student` 数据结构，为后续 Pydantic 和 LangGraph State 铺路。
- 已为存储模块添加第一批 pytest 单元测试。
- 已补充 Stage 2 学习资料：`materials/stage-2.md`。
- 已新增最小 FastAPI 应用：`app/api.py`。
- 已提供健康检查接口：`GET /health`。
- 已为 `/health` 添加 API 测试：`tests/test_api.py`。
- 已新增 Pydantic 模型：`StudentProfile` 和 `StudentProfileResponse`。
- 已提供请求体/响应模型示例接口：`POST /profile/preview`。
- 已提供学员资料接口：`GET /profile`、`POST /profile`。
- `POST /profile` 会保存学员资料，并保留已有学习笔记。
- 已新增学习笔记模型：`NoteCreate` 和 `NotesResponse`。
- 已提供学习笔记接口：`GET /notes`、`POST /notes`。
- `POST /notes` 会追加学习笔记，并保留已有学员资料。
- 已把学习建议规则抽到 `app/suggestions.py`，供 CLI 和 API 共用。
- 已新增学习建议模型：`SuggestionResponse`。
- 已提供学习建议接口：`GET /suggestion`。
- 已新增单条学习笔记响应模型：`NoteResponse`。
- 已新增单条学习笔记查询接口：`GET /notes/{note_index}`。
- 已为学习笔记 API 增加基础业务错误处理：笔记不存在返回 `404`，空白笔记返回 `400`。
- 已明确当前阶段的存储边界：继续使用 `data/student.json`，后续再按需要迁移到 SQLite / PostgreSQL。
- 已补充 Stage 3 学习资料：`materials/stage-3.md`。
- 已进入 Stage 4：先理解 LLM 调用中的 `model`、prompt、message、instructions、input 和 token，暂不新增真实模型调用代码。
- 已新增 LLM Provider 配置层：`app/config.py`。
- 已支持通过 `LLM_PROVIDER` 在火山引擎 Ark Agent Plan、DeepSeek 和 Ollama 本地模型之间切换。
- 已更新 `.env.example`，提供云端模型和本地 Ollama 的配置模板。
- 已为配置读取新增测试：`tests/test_config.py`。
- 已新增 LLM 调用封装：`app/llm.py`。
- 已能把学员资料组织成 OpenAI 兼容 `chat/completions` 请求，并解析模型返回的建议文本。
- 已新增普通文本模型调用 demo：`app/llm_demo.py`，可在 provider 配置可用时手动跑真实模型调用。
- 已为 LLM 调用封装新增离线测试：`tests/test_llm.py`。
- 已新增结构化学习建议模型：`LearningSuggestionItem` 和 `StructuredLearningSuggestion`。
- 已能请求模型返回 JSON 对象，并用 Pydantic 校验为结构化建议。
- 已新增结构化模型调用 demo：`app/structured_llm_demo.py`，可在 provider 配置可用时手动打印结构化 JSON。
- 已为结构化输出新增成功路径和失败路径测试。
- 已新增 AI 建议接口：`POST /ai/suggestion`。
- `POST /ai/suggestion` 返回结构化 AI 建议，provider 不可用或模型输出无效时返回 `503`。
- `GET /suggestion` 仍保留为稳定规则建议接口。

## 推荐运行方式

后续课程优先使用 Python 3.13：

```powershell
py -3.13 -m app.main
```

## 目录说明

```text
app/        Python 应用代码
data/       本地学习数据
materials/  学习资料
outputs/    生成的学习计划和总结
tests/      测试代码
```

## 学习资料

- `materials/stage-2.md`：阶段 2 补充学习资料，覆盖模块导入、`Path`、JSON 文件读写、异常处理、pytest 基础和当前数据流。
- `materials/stage-3.md`：阶段 3 补充学习资料，覆盖 FastAPI route、Pydantic 模型、状态码、`TestClient`、虚拟环境和 API 数据流。

## 依赖说明

阶段 2.5 引入 pytest 作为测试依赖。
阶段 3.1 引入 FastAPI 作为 Web API 框架，并固定到本课已验证版本。
同时引入 `fastapi-cli`、`uvicorn[standard]` 和 `httpx`，用于开发服务器和 API 测试。
阶段 4.2 引入 `python-dotenv`，用于从本地 `.env` 读取模型服务配置。

后续课程会逐步把依赖写入 `requirements.txt`。

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行测试：

```powershell
py -3.13 -m pytest
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

健康检查：

```text
GET http://127.0.0.1:8000/health
```

学员资料预览：

```text
POST http://127.0.0.1:8000/profile/preview
```

学员资料 API：

```text
GET  http://127.0.0.1:8000/profile
POST http://127.0.0.1:8000/profile
```

学习笔记 API：

```text
GET  http://127.0.0.1:8000/notes
GET  http://127.0.0.1:8000/notes/{note_index}
POST http://127.0.0.1:8000/notes
```

学习建议 API：

```text
GET http://127.0.0.1:8000/suggestion
```

AI 学习建议 API：

```text
POST http://127.0.0.1:8000/ai/suggestion
```

如果 provider 不可用，AI 建议接口会返回 `503`。规则建议接口仍然可用。

LLM Provider 配置：

```text
LLM_PROVIDER=volcengine_agent_plan
LLM_PROVIDER=deepseek
LLM_PROVIDER=ollama
```

真实密钥写入本地 `.env`，不要写入 `.env.example` 或代码。

LLM 调用封装：

```text
app/llm.py
```

首次真实模型调用入口：

```powershell
py -3.13 -m app.llm_demo
```

这条命令需要在 `ai-learning-assistant/` 目录下运行，并且需要 `.env` 中的 provider 配置可用。

当前 `GET /suggestion` 仍返回规则建议；AI 建议调用先封装在 `generate_learning_suggestion()`，后续课程再接入 API。

手动跑普通文本模型调用：

```powershell
py -3.13 -m app.llm_demo
```

结构化 AI 建议入口：

```text
generate_structured_learning_suggestion()
```

它返回 `StructuredLearningSuggestion`，而不是普通字符串。

手动跑结构化模型调用：

```powershell
py -3.13 -m app.structured_llm_demo
```
