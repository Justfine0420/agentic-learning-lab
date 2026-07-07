# 第 3.1 课：FastAPI 入门

## 1. 本课目标

阶段 2 已经让 `AI 学习助教` 具备了稳定的命令行能力：可以保存学习档案、读取 JSON、处理坏文件，并且有第一批 pytest 测试。

现在进入阶段 3：FastAPI 基础。

本课目标很窄，只做一件事：

```text
让项目拥有第一个 HTTP API：GET /health
```

你会学到：

- FastAPI 应用对象是什么。
- 什么是 route / path operation。
- 为什么 API 函数返回字典时会变成 JSON。
- 如何用 Uvicorn 启动开发服务器。
- 如何用浏览器访问 `/health`。
- 如何用 `TestClient` 写第一个 API 测试。

官方文档对应阅读：

- [FastAPI 安装](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## 2. 你会新增什么项目能力

本课之后，项目新增：

```text
ai-learning-assistant/app/api.py
ai-learning-assistant/tests/test_api.py
```

新增接口：

```http
GET /health
```

返回：

```json
{
  "status": "ok",
  "service": "ai-learning-assistant"
}
```

这表示：

```text
API 服务能启动。
应用能响应 HTTP 请求。
测试可以直接验证 API 返回值。
```

阶段 3 后续课程会把阶段 2 的 CLI 能力继续接成 API：

- `GET /profile`
- `POST /profile`
- `GET /notes`
- `POST /notes`
- `GET /suggestion`

但本课先只做 `/health`。

## 3. 前置知识

开始前确认你已经理解：

- `app/` 是 Python 包。
- `app/main.py` 是当前 CLI 入口。
- `app/storage.py` 负责读写 JSON。
- pytest 可以自动发现 `tests/test_*.py`。
- `assert` 可以验证结果。

还要记住一个边界：

```text
CLI 入口和 API 入口可以同时存在。
```

所以本课不会删除 `app/main.py`，也不会把 CLI 改没。

## 4. 核心概念

### FastAPI 应用对象

FastAPI 官方 First Steps 示例从这行开始：

```python
from fastapi import FastAPI

app = FastAPI()
```

这里的 `app` 是 FastAPI 应用实例。

可以把它理解成：

```text
所有 API route 都挂在这个 app 上。
开发服务器启动时会加载这个 app。
测试时 TestClient 也会拿这个 app 发请求。
```

### route / path operation

本课代码里会写：

```python
@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-learning-assistant",
    }
```

拆开看：

```python
@app.get("/health")
```

表示：

```text
当浏览器或客户端用 GET 方法访问 /health 时，执行下面这个函数。
```

下面这个函数：

```python
def health_check() -> dict[str, str]:
```

就是这个 route 对应的处理逻辑。

FastAPI 文档里把这类函数叫 path operation function。

### 返回字典为什么会变成 JSON

函数返回的是 Python 字典：

```python
{
    "status": "ok",
    "service": "ai-learning-assistant",
}
```

HTTP API 返回给客户端时会变成 JSON。

所以你在浏览器中看到的是：

```json
{"status":"ok","service":"ai-learning-assistant"}
```

这是后续所有 API 的基础。

### 为什么不用 `input()`

HTTP API 不会像 CLI 一样调用：

```python
input("请输入你的名字：")
```

API 的输入来自 HTTP 请求。

后面第 3.2 和 3.3 课会开始处理请求体。现在 `/health` 不需要输入，只负责证明服务可用。

## 5. 代码实现

### 第一步：更新依赖

打开：

```text
ai-learning-assistant/requirements.txt
```

修改为：

```text
fastapi==0.115.14
fastapi-cli>=0.0.7
uvicorn[standard]>=0.30.0
httpx>=0.27.0
pytest>=8.0.0

# 后续课程会逐步加入 FastAPI、LangChain、LangGraph、Deep Agents 等依赖。
```

官方文档快速开始会用：

```powershell
pip install "fastapi[standard]"
```

本项目把依赖写进 `requirements.txt`，并显式列出本课用到的运行与测试依赖，所以后续统一运行：

```powershell
py -3.13 -m pip install -r requirements.txt
```

### 第二步：新增 `app/api.py`

新增文件：

```text
ai-learning-assistant/app/api.py
```

写入：

```python
from fastapi import FastAPI


app = FastAPI(title="AI Learning Assistant")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-learning-assistant",
    }
```

注意：

```text
app/api.py 是 API 入口。
app/main.py 继续作为 CLI 入口。
```

不要把两个入口混在一起。

### 第三步：新增 `tests/test_api.py`

新增文件：

```text
ai-learning-assistant/tests/test_api.py
```

写入：

```python
from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-learning-assistant",
    }
```

官方测试文档建议用 `fastapi.testclient.TestClient` 来测试应用，不需要真的启动 HTTP 服务器。

这和你用浏览器访问接口不一样：

```text
浏览器访问：需要启动服务器。
TestClient 测试：直接在测试进程里调用 FastAPI app。
```

### 第四步：CLI 显示阶段更新

打开：

```text
ai-learning-assistant/app/cli.py
```

把：

```python
COURSE_STAGE = "Stage 2"
```

改成：

```python
COURSE_STAGE = "Stage 3"
```

这只是显示当前课程阶段，不改变 CLI 行为。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

启动成功后访问：

```text
http://127.0.0.1:8000/health
```

你应该看到：

```json
{"status":"ok","service":"ai-learning-assistant"}
```

也可以打开自动文档：

```text
http://127.0.0.1:8000/docs
```

FastAPI 会根据当前 API 自动生成 OpenAPI 文档和交互页面。

运行测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/__init__.py tests/test_storage.py tests/test_api.py
```

确认 CLI 仍可运行：

```powershell
"2`n4" | py -3.13 -m app.main
```

## 7. 常见错误

### 没安装 FastAPI

如果看到：

```text
ModuleNotFoundError: No module named 'fastapi'
```

先运行：

```powershell
py -3.13 -m pip install -r requirements.txt
```

### 启动命令位置不对

本项目应该在：

```text
ai-learning-assistant/
```

下运行：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

不要在仓库根目录直接运行这个命令，否则路径会对不上。

### `fastapi dev` 在 Windows 终端输出乱码或报编码错误

FastAPI 官方快速开始会使用：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

在某些 Windows 终端里，CLI 的彩色输出可能遇到本地编码问题。

本教程使用更稳定的模块启动方式：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

这同样会启动 FastAPI 应用。

### 把 API 写进 `main.py`

当前项目保留两个入口：

```text
app/main.py  CLI 入口
app/api.py   API 入口
```

如果把 FastAPI app 直接写进 `main.py`，后续学习者容易混淆：

```text
到底是运行 CLI，还是运行 API？
```

所以本课单独新增 `api.py`。

### 忘记写测试

只用浏览器访问 `/health` 是人工验证。

本课还要保留自动化测试：

```powershell
py -3.13 -m pytest
```

后面 API 变多后，测试会防止你改坏旧接口。

## 8. 练习

练习 1：新增一个接口：

```http
GET /version
```

返回：

```json
{
  "version": "0.1.0"
}
```

并为它新增测试。

练习 2：把 `FastAPI(title="AI Learning Assistant")` 改成你自己的标题，然后打开：

```text
http://127.0.0.1:8000/docs
```

观察页面标题变化。

练习 3：故意把测试里的期望值改错，运行：

```powershell
py -3.13 -m pytest
```

观察 pytest 如何提示 API 返回值差异。

练习完成后，建议恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `requirements.txt` 包含 `fastapi==0.115.14`、`fastapi-cli>=0.0.7`、`uvicorn[standard]>=0.30.0` 和 `httpx>=0.27.0`。
- `app/api.py` 存在，并定义 `app = FastAPI(...)`。
- `GET /health` 返回 `status` 和 `service`。
- `tests/test_api.py` 存在，并用 `TestClient` 验证 `/health`。
- `py -3.13 -m uvicorn app.api:app --reload` 能启动服务。
- 浏览器或 HTTP 客户端访问 `/health` 能得到 JSON。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。
- CLI 入口 `py -3.13 -m app.main` 仍可运行。
- 没有创建课程代码快照目录。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

FastAPI 是后续能力对外暴露的入口。

| 现在 | 后续升级 |
| --- | --- |
| `GET /health` | 服务健康检查 / 部署探针 |
| `app/api.py` | 统一 API 入口 |
| `@app.get(...)` | 资料、笔记、建议、RAG、Graph、Agent 接口 |
| `TestClient` | API 回归测试 |
| 返回 dict | 结构化响应 / Pydantic response model |
| HTTP route | 调用 LangChain Agent / LangGraph workflow 的入口 |

后面真正接入 LangChain、RAG、LangGraph 和 Deep Agents 时，用户不会直接调用 Python 函数。

他们会通过 API 访问这些能力。

本课的 `/health` 是最小起点。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-3/03-01-fastapi-first-api.md`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_api.py`

修改文件：

- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/README.md`
- `docs/tutorial/README.md`
- `README.md`

新增依赖：

- `fastapi==0.115.14`
- `fastapi-cli>=0.0.7`
- `uvicorn[standard]>=0.30.0`
- `httpx>=0.27.0`

新增命令：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/__init__.py tests/test_storage.py tests/test_api.py
"2`n4" | py -3.13 -m app.main
```

API 人工验证：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

然后访问：

```text
http://127.0.0.1:8000/health
```

验证结果：

- `/health` 返回 `{"status":"ok","service":"ai-learning-assistant"}`。
- pytest 测试全部通过。
- Python 文件可以编译通过。
- CLI 仍能加载并展示当前学习档案。

下一步：

- 第 3.2 课：Pydantic 模型，为后续 `GET/POST /profile` 做准备。
