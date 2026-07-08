# 阶段 4 复盘：LLM 基础、结构化输出与 AI 建议入口

## 1. 阶段目标

阶段 4 的目标是把阶段 3 已经稳定的规则学习助手，升级成具备真实 LLM 调用能力的 AI 学习助教雏形。

本阶段重点不是直接引入 LangChain，也不是把所有建议都替换成模型生成，而是先建立后续 LangChain、RAG、LangGraph 和 Deep Agents 都会依赖的模型调用基础：

- 理解 `model`、prompt、message、instructions、input 和 token。
- 把 provider 配置从代码里移到 `.env` 和环境变量。
- 支持火山引擎 Ark Agent Plan、DeepSeek 和本地 Ollama。
- 封装 OpenAI 兼容 `chat/completions` 调用。
- 用 fake client 测试模型调用边界，不让单元测试依赖真实 provider。
- 用 Pydantic 把模型输出校验成结构化学习建议。
- 通过 API 和 CLI 暴露 AI 建议入口。
- 保留离线规则建议作为稳定 fallback，而不是偷偷伪装成 AI 成功。

## 2. 已生成课程

| 小节 | 标题 | 文档 | 状态 |
| --- | --- | --- | --- |
| 4.1 | LLM 基础概念 | `docs/tutorial/lessons/stage-4/04-01-llm-basic-concepts.md` | 已生成 / 已验证 |
| 4.2 | 配置 LLM Provider 和 API Key | `docs/tutorial/lessons/stage-4/04-02-configure-api-key.md` | 已生成 / 已验证 |
| 4.3 | 第一次模型调用 | `docs/tutorial/lessons/stage-4/04-03-first-llm-call.md` | 已生成 / 已验证 |
| 4.4 | 结构化输出 | `docs/tutorial/lessons/stage-4/04-04-structured-output.md` | 已生成 / 已验证 |
| 4.5 | AI 建议 API、CLI 入口与降级边界 | `docs/tutorial/lessons/stage-4/04-05-ai-suggestion-api.md` | 已生成 / 已验证 |

## 3. 补充学习资料

阶段 4 额外沉淀了一份补充资料：

```text
ai-learning-assistant/materials/stage-4.md
```

它适合在完成 4.1 到 4.5 之后回看，重点解释：

- `LLM_PROVIDER`、`.env`、API Key 和 provider 配置层。
- `@dataclass(frozen=True)` 为什么适合保存配置。
- 为什么不在 `api.py` 里直接读取 API Key。
- `python -m app.llm_demo` 和脚本路径运行的区别。
- OpenAI 兼容 `chat/completions` 请求格式。
- `system` message、`user` message、prompt、input 和 token 的分工。
- `httpx.Client.post()`、`response.raise_for_status()` 和 `response.json()`。
- 为什么 LLM 单元测试要使用 fake client。
- `Field()`、`model_json_schema()`、`model_validate_json()` 和 `response_format={"type": "json_object"}`。
- `/suggestion` 和 `/ai/suggestion` 为什么分开。
- CLI 为什么同时保留离线规则建议和 AI 建议。
- 当前 Stage 4 从 CLI/API 到 `llm.py` 的完整数据流。

## 4. 当前项目能力

阶段 4 完成后，`AI 学习助教` 已经具备：

- 通过 `app/config.py` 读取 LLM provider 配置。
- 用 `.env.example` 提供可提交的配置模板，并继续忽略真实 `.env`。
- 支持 `LLM_PROVIDER=volcengine_agent_plan`、`deepseek` 和 `ollama`。
- 保留 `volcengine_coding` 作为兼容别名。
- 用 `LLMSettings` 表达统一后的 provider、API Key、base URL、model 和是否需要 API Key。
- 用 `require_llm_api_key()` 在云端 provider 缺少密钥时明确失败。
- 用 `app/llm.py` 封装模型调用，而不是把 HTTP 请求散落在 API 或 CLI 中。
- 能把学员资料、学习目标、Python 水平和最近 5 条笔记组织成 messages。
- 能调用 OpenAI 兼容的 `{base_url}/chat/completions`。
- 能解析 `choices[0].message.content`。
- 能生成普通文本学习建议。
- 能请求模型返回 JSON 对象，并用 Pydantic 校验成 `StructuredLearningSuggestion`。
- 能用 `LearningSuggestionItem` 限制每条建议的标题、描述和预计分钟数。
- 能用 `app/llm_demo.py` 手动跑普通文本模型调用。
- 能用 `app/structured_llm_demo.py` 手动跑结构化模型调用。
- 提供 `POST /ai/suggestion` 返回结构化 AI 建议。
- 保留 `GET /suggestion` 作为稳定离线规则建议。
- CLI 菜单中 `3. 查看离线规则建议` 继续走规则函数。
- CLI 菜单中 `4. 生成 AI 学习建议` 复用 `generate_structured_learning_suggestion()`。
- AI provider 配置缺失、网络失败或模型输出不合 schema 时，API 返回 `503`，CLI 给出明确不可用提示。
- 用 `tests/test_config.py`、`tests/test_llm.py`、`tests/test_llm_demo.py`、`tests/test_structured_llm_demo.py`、`tests/test_api.py` 和 `tests/test_cli.py` 覆盖主要边界。

## 5. 当前入口

真实代码仍然只有一份：

```text
ai-learning-assistant/
```

CLI 入口：

```powershell
cd ai-learning-assistant
py -3.13 -m app.main
```

当前建议相关菜单：

```text
3. 查看离线规则建议
4. 生成 AI 学习建议
5. 退出
```

普通文本模型调用：

```powershell
py -3.13 -m app.llm_demo
```

结构化模型调用：

```powershell
py -3.13 -m app.structured_llm_demo
```

API 入口：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

建议相关接口：

```text
GET  /suggestion
POST /ai/suggestion
```

## 6. 验证命令与结果

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
```

结果：

```text
54 passed
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py
```

结果：通过。

文档一致性检查：

```powershell
rg -n '5\. 生成 AI 学习建议' docs/tutorial/lessons/stage-4 ai-learning-assistant/app ai-learning-assistant/tests ai-learning-assistant/README.md
rg -n 'choice == "5"' docs/tutorial/lessons/stage-4/04-05-ai-suggestion-api.md ai-learning-assistant/app/cli.py
rg -n '下一步建议：生成阶段 4 复盘|阶段 4 进行中|第 4\.5 课已生成并验证' README.md docs/tutorial/README.md ai-learning-assistant/README.md
```

结果：均无输出。

## 7. 关键设计决策

### 不把 `GET /suggestion` 改成 AI

`GET /suggestion` 是阶段 3 已经稳定的离线规则接口。

它不需要 API Key、不访问外网、不产生费用，也不会因为 provider 不可用而失败。

Stage 4 新增的是：

```text
POST /ai/suggestion
```

这样学习者可以清楚地区分：

| 入口 | 能力 | 依赖 |
| --- | --- | --- |
| `GET /suggestion` | 离线规则建议 | 无模型依赖 |
| `POST /ai/suggestion` | AI 结构化建议 | 需要 provider |
| CLI `3` | 离线规则建议 | 无模型依赖 |
| CLI `4` | AI 结构化建议 | 需要 provider |

### 不让 CLI 通过 HTTP 调本地 API

CLI 不通过：

```text
POST http://127.0.0.1:8000/ai/suggestion
```

原因是这会要求使用 CLI 前先启动 `uvicorn`。

当前设计是：

```text
CLI -> generate_structured_learning_suggestion(student)
API -> generate_structured_learning_suggestion(student)
```

也就是说，CLI 和 API 共享同一个业务函数，但各自负责自己的交互边界。

### 不做服务端静默降级

错误做法：

```text
AI 失败 -> 服务端返回规则建议 -> HTTP 200
```

这会让调用方以为拿到了 AI 结果。

当前做法：

```text
AI 失败 -> API 返回 503
AI 失败 -> CLI 明确提示 AI 建议暂不可用
```

是否降级到规则建议，由调用方或用户显式选择。

### `response_format` 不是校验

`response_format={"type": "json_object"}` 只是请求 provider 尽量返回 JSON 对象。

真正的程序边界是：

```python
StructuredLearningSuggestion.model_validate_json(content)
```

这一步会拒绝非 JSON、空建议列表、缺失字段和不符合时间范围的内容。

## 8. 已知限制

- 当前还没有引入 LangChain，`app/llm.py` 仍是手写 HTTP 调用封装。
- 当前还没有工具调用、agent harness 或 memory。
- 当前还没有 RAG，不能基于本地学习资料自动检索答疑。
- 当前还没有 LangGraph，学习流程还不是状态机。
- 当前还没有 Deep Agents，不具备长期规划、文件系统写入和子 Agent 协作能力。
- 当前没有统一 `POST /chat` 对话接口。
- 当前仍然是单用户本地学习助手。
- 当前持久化仍然使用 `data/student.json`。
- 真实模型调用依赖 `.env`、云端 provider 或本地 Ollama；自动化测试只验证调用边界，不访问真实 provider。
- `response_format={"type": "json_object"}` 的兼容性取决于 provider；如果 provider 行为变化，需要重新验证。

这些限制符合 Stage 4 范围。Stage 4 的任务是建立 LLM 调用地基，不是提前完成 Agent 框架集成。

## 9. 后续升级关系

| Stage 4 概念 | 后续升级 |
| --- | --- |
| `LLMSettings` | LangChain model 初始化配置 |
| `SYSTEM_INSTRUCTIONS` | Agent system prompt |
| `messages` | LangChain messages / agent input |
| `generate_learning_suggestion()` | LangChain model 调用 |
| `generate_structured_learning_suggestion()` | LangChain structured output / Agent 输出契约 |
| `LearningSuggestionItem` / `StructuredLearningSuggestion` | 学习计划、工具结果和 Graph State 的结构化模型 |
| fake client 测试 | Agent、RAG、Graph 的离线测试策略 |
| `POST /ai/suggestion` | 后续 `POST /chat` 或 Agent API |
| CLI AI 建议入口 | 终端版 Agent 交互入口 |
| provider 失败返回 `503` | Agent 工具失败、RAG 失败和 Graph 节点失败的边界设计 |

## 10. 下一步建议

下一阶段：Stage 5，LangChain。

建议先做第 5.1 课：LangChain 定位。

进入 Stage 5 前需要重新核对官方文档，尤其是：

- 当前 LangChain 推荐的模型初始化方式。
- 当前 `create_agent` 的用法。
- tool 定义方式。
- 结构化输出和 FastAPI 接入方式。

Stage 5 的目标不是“换个库再写一遍模型调用”，而是把 Stage 4 手写的模型调用升级为可调用工具、可扩展、可测试的 Agent harness。
