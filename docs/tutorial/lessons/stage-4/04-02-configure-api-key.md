# 第 4.2 课：配置 LLM Provider 和 API Key

## 1. 本课目标

第 4.1 课已经讲清楚一次 LLM 调用里会出现 `model`、prompt、message、input 和 token。

本课开始做真实项目准备：把模型服务的配置从代码里拿出去，放到环境变量和 `.env` 文件里。

你要学会：

- 为什么 API Key 不能写进代码。
- `.env` 和 `.env.example` 分别负责什么。
- 如何用 `python-dotenv` 读取本地配置。
- 如何用 `LLM_PROVIDER` 在不同模型服务之间切换。
- 如何同时支持火山引擎 Ark Agent Plan、DeepSeek 和 Ollama 本地模型。
- 为什么 4.2 只做配置读取，不直接发起模型请求。

本课会新增代码，但不会调用真实模型。

真实模型调用放到第 4.3 课。

## 2. 你会新增什么项目能力

本课后，项目会新增一个配置层：

```text
ai-learning-assistant/app/config.py
```

它负责读取当前要用哪个模型服务：

```text
LLM_PROVIDER=volcengine_agent_plan
```

然后根据 provider 读取对应配置：

```text
VOLCENGINE_AGENT_PLAN_API_KEY
VOLCENGINE_AGENT_PLAN_BASE_URL
VOLCENGINE_AGENT_PLAN_MODEL
```

或：

```text
DEEPSEEK_API_KEY
DEEPSEEK_BASE_URL
DEEPSEEK_MODEL
```

或：

```text
OLLAMA_BASE_URL
OLLAMA_MODEL
```

当前支持的 provider：

| Provider | 用途 | 是否需要真实 API Key |
| --- | --- | --- |
| `volcengine_agent_plan` | 火山引擎 Ark Agent Plan，默认云端方案 | 需要 |
| `volcengine_coding` | 兼容旧称，指向 Ark Agent Plan 配置 | 需要 |
| `deepseek` | DeepSeek 云端模型 | 需要 |
| `ollama` | 本机 Ollama 模型 | 不需要真实 key |

注意，`volcengine_coding` 只是为了兼容前面讨论里的叫法。
后续课程统一推荐使用 `volcengine_agent_plan`。

## 3. 前置知识

开始前，你应该已经理解：

- Python 如何读取字符串变量。
- 字典如何保存不同 provider 的配置。
- 函数如何返回结构化数据。
- pytest 如何验证函数行为。
- `.gitignore` 可以阻止敏感文件进入 Git。

你还需要理解一个现实问题：

```text
模型配置会变。
```

模型名称会变，base URL 可能会分不同产品线，API Key 也可能分不同权限。

所以课程不能把所有配置写死在业务代码里。
我们要先做一层 `config.py`，后面 `llm.py` 只从这层拿配置。

## 4. 核心概念

本课配置参考了这些官方文档：

- 火山引擎 Ark Agent Plan：[其他工具](https://www.volcengine.com/docs/82379/2373746)
- DeepSeek：[Your First API Call](https://api-docs.deepseek.com/)
- Ollama：[OpenAI compatibility](https://docs.ollama.com/api/openai-compatibility)

### API Key 是什么

API Key 是访问模型服务的密钥。

它通常代表：

- 你是谁。
- 你是否有权限调用模型。
- 调用费用算到哪个账号。
- 服务端如何限制你的调用频率。

所以 API Key 不能写进代码仓库。

错误做法：

```python
api_key = "sk-真实密钥"
```

正确做法：

```python
api_key = os.getenv("DEEPSEEK_API_KEY")
```

### `.env` 是什么

`.env` 是本地环境变量文件。

它只应该存在于你自己的机器上。

例如：

```text
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
```

或：

```text
LLM_PROVIDER=volcengine_agent_plan
VOLCENGINE_AGENT_PLAN_API_KEY=你的真实密钥
VOLCENGINE_AGENT_PLAN_MODEL=ark-code-latest
```

`.env` 不能提交。

本仓库的 `.gitignore` 已经忽略了 `.env`。

### `.env.example` 是什么

`.env.example` 是配置模板。

它可以提交，因为里面不能放真实密钥。

它告诉后来学习的人：

```text
这个项目需要哪些环境变量。
每个变量大概应该填什么。
```

所以本课会维护：

```text
ai-learning-assistant/.env.example
```

### Provider 是什么

Provider 是“模型服务提供方”的意思。

在本项目里，provider 不只是公司名字。
它代表一套完整调用配置：

```text
provider = api_key_env + base_url_env + model_env + 默认值
```

例如火山引擎 Ark Agent Plan：

```text
api_key_env = VOLCENGINE_AGENT_PLAN_API_KEY
base_url_env = VOLCENGINE_AGENT_PLAN_BASE_URL
model_env = VOLCENGINE_AGENT_PLAN_MODEL
```

DeepSeek：

```text
api_key_env = DEEPSEEK_API_KEY
base_url_env = DEEPSEEK_BASE_URL
model_env = DEEPSEEK_MODEL
```

Ollama：

```text
api_key_env = OLLAMA_API_KEY
base_url_env = OLLAMA_BASE_URL
model_env = OLLAMA_MODEL
```

这样后面切换模型时，只需要改：

```text
LLM_PROVIDER=ollama
```

而不是到处改业务代码。

### 火山引擎 Ark Agent Plan

你提到“火山引擎的 coding plan”，这里要用官方更准确的名字：Ark Agent Plan。

官方文档里，Agent Plan 兼容 OpenAI 接口协议，适用于 Codex CLI、Cline、Cursor、Roo Code、Kilo Code 等工具。

关键配置是：

```text
Base URL = https://ark.cn-beijing.volces.com/api/plan/v3
Model = ark-code-latest 或控制台支持的 Model Name
```

还有一个非常重要的点：

```text
Agent Plan 专属 API Key 不能和普通火山方舟 API Key 混用。
```

这就是为什么本项目用独立变量名：

```text
VOLCENGINE_AGENT_PLAN_API_KEY
```

而不是模糊地叫：

```text
ARK_API_KEY
```

### DeepSeek

DeepSeek 也提供 OpenAI 兼容格式。

本课给它保留独立配置：

```text
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的真实密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

这样你以后如果想从火山切到 DeepSeek，只改 `.env`，不改业务代码。

### Ollama 本地模型

Ollama 是本地模型服务。

你本机启动 Ollama 后，可以通过 OpenAI 兼容接口访问：

```text
http://localhost:11434/v1
```

Ollama 的 OpenAI 兼容示例里，`api_key` 字段需要传，但会被忽略。
所以项目里给它默认：

```text
OLLAMA_API_KEY=ollama
```

这不是密钥，只是为了兼容 OpenAI 风格客户端的占位值。

本课不检查你的本机 Ollama 是否真的启动。
4.3 调用模型时再做真实连通性验证。

## 5. 代码实现

### 第一步：新增依赖

打开：

```text
ai-learning-assistant/requirements.txt
```

确认新增：

```text
python-dotenv>=1.0.0
```

`python-dotenv` 负责把 `.env` 文件里的内容加载到环境变量。

### 第二步：更新 `.env.example`

打开：

```text
ai-learning-assistant/.env.example
```

本课后它应该包含三组配置：

```text
LLM_PROVIDER=volcengine_agent_plan

VOLCENGINE_AGENT_PLAN_API_KEY=
VOLCENGINE_AGENT_PLAN_BASE_URL=https://ark.cn-beijing.volces.com/api/plan/v3
VOLCENGINE_AGENT_PLAN_MODEL=ark-code-latest

DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

OLLAMA_API_KEY=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
```

注意：

- `.env.example` 可以提交。
- `.env` 不能提交。
- 空着的 API Key 位置由学习者自己填。
- 模型名以你控制台或本机实际可用模型为准。

### 第三步：新增 `config.py`

新增文件：

```text
ai-learning-assistant/app/config.py
```

核心结构是两个 dataclass：

```python
@dataclass(frozen=True)
class LLMProviderConfig:
    api_key_env: str
    base_url_env: str
    model_env: str
    default_base_url: str
    default_model: str
    default_api_key: str = ""
    requires_api_key: bool = True
```

它描述某个 provider 应该从哪些环境变量读取配置。

运行时真正拿到的是：

```python
@dataclass(frozen=True)
class LLMSettings:
    provider: str
    api_key: str
    api_key_env: str
    base_url: str
    model: str
    requires_api_key: bool
```

`LLMSettings` 是后面 `llm.py` 会使用的配置结果。

当前默认 provider 是：

```text
volcengine_agent_plan
```

如果你想改成本地模型，后面只需要在 `.env` 写：

```text
LLM_PROVIDER=ollama
```

### 第四步：新增配置测试

新增文件：

```text
ai-learning-assistant/tests/test_config.py
```

它会验证：

- 默认 provider 是 `volcengine_agent_plan`。
- `volcengine_coding` 这个旧别名仍然可用。
- DeepSeek 可以从环境变量读取配置。
- Ollama 不要求真实 API Key。
- 不支持的 provider 会报错。
- 云端 provider 缺 API Key 会报错。

这些测试不会访问外网，也不会要求你真的有 API Key。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py tests/test_config.py
```

你也可以临时查看当前配置读取结果：

```powershell
py -3.13 -c "from app.config import get_llm_settings; print(get_llm_settings(load_dotenv_file=False))"
```

它应该打印类似：

```text
LLMSettings(provider='volcengine_agent_plan', ...)
```

如果你想试 Ollama 配置读取：

```powershell
$env:LLM_PROVIDER="ollama"
py -3.13 -c "from app.config import get_llm_settings; print(get_llm_settings(load_dotenv_file=False))"
```

注意，这只是读取配置，不会连接 Ollama。

## 7. 常见错误

### 把真实 API Key 写进 `.env.example`

不要这样做。

`.env.example` 是公开模板。
真实密钥只能写在本地 `.env` 或系统环境变量里。

### 把 `.env` 提交到 Git

`.env` 已经被 `.gitignore` 忽略。

如果你发现 `git status` 里出现 `.env`，先停下来，不要提交。

### 混用火山普通 API Key 和 Agent Plan API Key

火山 Agent Plan 使用专属 API Key。

如果你拿普通火山方舟 API Key 去配置 Agent Plan，后续真实调用可能会认证失败。

### 把 `base_url` 写错成普通服务地址

本课火山默认配置是 Agent Plan 的 OpenAI 兼容地址：

```text
https://ark.cn-beijing.volces.com/api/plan/v3
```

不要写成其它普通 chat completion 地址，除非你明确切换了产品线和后续调用方式。

### 以为 Ollama 不需要 `api_key` 字段就可以不填

Ollama 本地服务不校验真实 key。

但 OpenAI 风格客户端通常仍要求传 `api_key` 参数。
所以我们使用占位值：

```text
OLLAMA_API_KEY=ollama
```

### 忘记安装 `python-dotenv`

如果看到：

```text
ModuleNotFoundError: No module named 'dotenv'
```

说明你还没有安装依赖。

运行：

```powershell
py -3.13 -m pip install -r requirements.txt
```

## 8. 练习

练习 1：解释下面三个文件的区别：

```text
.env
.env.example
.gitignore
```

练习 2：把当前 provider 改成本地 Ollama。

你应该在本地 `.env` 写：

```text
LLM_PROVIDER=ollama
OLLAMA_MODEL=你的本地模型名
```

练习 3：解释为什么 `volcengine_agent_plan` 和 `deepseek` 都需要真实 API Key，而 `ollama` 不需要。

练习 4：解释为什么不应该在 `api.py` 里直接读取 `DEEPSEEK_API_KEY`。

练习 5：如果你未来要新增一个 provider，写出你认为需要增加的 3 个环境变量。

例如：

```text
SOME_PROVIDER_API_KEY
SOME_PROVIDER_BASE_URL
SOME_PROVIDER_MODEL
```

## 9. 验收标准

完成本课后，你应该能做到：

- 解释 API Key 为什么不能写进代码。
- 解释 `.env` 和 `.env.example` 的区别。
- 解释 `LLM_PROVIDER` 的作用。
- 说出当前支持的三个主要 provider：`volcengine_agent_plan`、`deepseek`、`ollama`。
- 说出火山 Agent Plan 使用专属 API Key。
- 说出 Ollama 的 `api_key=ollama` 是兼容占位值，不是真实密钥。
- 运行 `py -3.13 -m pytest` 通过。
- 运行 `py_compile` 通过。
- 知道第 4.3 课才会真实调用模型。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

本课的配置层会直接影响后面所有模型调用。

| 本课内容 | 后续升级 |
| --- | --- |
| `LLM_PROVIDER` | 切换 LangChain 使用的模型服务 |
| `base_url` | 对接 OpenAI 兼容模型、本地 Ollama 或云厂商 |
| `model` | 传给 LangChain chat model 或 Deep Agents |
| `api_key` | 作为模型客户端认证配置 |
| `LLMSettings` | `llm.py`、Agent、Graph 节点共用的配置结果 |

LangChain 阶段不会重新发明 provider 配置。
它会复用本课的 `get_llm_settings()`。

LangGraph 阶段也一样。
Graph 节点只关心“调用模型拿结果”，不应该关心 API Key 从哪里来。

Deep Agents 阶段更需要这层配置。
因为 Deep Agent 会跑更长任务，一旦 provider 配置散落在多个文件里，后面会很难排查。

## 11. 本课变更清单

新增文件：

- `ai-learning-assistant/app/config.py`
- `ai-learning-assistant/tests/test_config.py`
- `docs/tutorial/lessons/stage-4/04-02-configure-api-key.md`

修改文件：

- `ai-learning-assistant/.env.example`
- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/README.md`
- `README.md`
- `docs/tutorial/README.md`
- `docs/tutorial/ai-learning-assistant-course-plan.md`

代码变更：

- 新增 `LLMProviderConfig`。
- 新增 `LLMSettings`。
- 新增 `get_llm_settings()`。
- 新增 `require_llm_api_key()`。
- 支持 `volcengine_agent_plan`、`volcengine_coding`、`deepseek`、`ollama`。

新增依赖：

- `python-dotenv>=1.0.0`

环境变量变更：

- 新增 `LLM_PROVIDER`。
- 新增火山 Agent Plan 配置变量。
- 新增 DeepSeek 配置变量。
- 新增 Ollama 配置变量。

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py tests/test_config.py
```

下一步：

- 第 4.3 课：新增 `llm.py`，用当前 provider 配置发起第一次真实模型调用。
