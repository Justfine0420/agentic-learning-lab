# 第 3.2 课：Pydantic 模型

## 1. 本课目标

第 3.1 课已经让项目拥有了第一个 FastAPI 接口：

```http
GET /health
```

现在要解决一个更现实的问题：

```text
API 收到的数据应该长什么样？
API 返回的数据应该长什么样？
```

本课目标是引入 Pydantic 模型，并用一个预览接口演示请求体和响应模型：

```http
POST /profile/preview
```

它不会保存数据。

真正读写学习档案的接口会放到第 3.3 课。

本课你会学到：

- 什么是 Pydantic `BaseModel`。
- 如何用模型描述请求体。
- 如何做基础字段校验。
- 什么是 FastAPI 的 `response_model`。
- 为什么请求不合法时会返回 `422`。
- Pydantic 模型和阶段 2 的 `TypedDict` 有什么区别。

官方文档对应阅读：

- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/)

## 2. 你会新增什么项目能力

本课之后，项目会新增两个 Pydantic 模型：

```python
class StudentProfile(BaseModel):
    ...


class StudentProfileResponse(StudentProfile):
    ...
```

并新增一个 API：

```http
POST /profile/preview
```

请求示例：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner"
}
```

响应示例：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner",
  "note_count": 0
}
```

如果 `python_level` 传入不允许的值，例如：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "expert"
}
```

FastAPI 会返回：

```text
422 Unprocessable Entity
```

这说明请求体已经被模型校验拦住。

## 3. 前置知识

开始前确认你已经理解：

- `app/api.py` 是 FastAPI 入口。
- `@app.get("/health")` 定义了一个 GET 接口。
- pytest 中可以用 `TestClient` 调 API。
- 阶段 2 中的 `Student` 是 `TypedDict`。
- `data/student.json` 现在仍由 `storage.py` 负责读写。

本课会在 `models.py` 中同时保留：

```text
TypedDict 版本：给现有 storage.py 使用。
Pydantic 版本：给 FastAPI 请求体和响应使用。
```

不要急着删除 `Student`。

## 4. 核心概念

### 什么是 Pydantic `BaseModel`

FastAPI 官方 Request Body 文档会用 Pydantic 模型声明请求体。

基本写法是：

```python
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    price: float
```

本项目要声明的是学员资料：

```python
class StudentProfile(BaseModel):
    name: str
    goal: str
    python_level: str
```

这表示：

```text
请求体里应该有 name、goal、python_level。
这三个字段都应该是字符串。
```

### 字段校验

只写 `str` 还不够。

我们还希望：

```text
name 不能为空。
goal 不能为空。
python_level 只能是 beginner / basic / intermediate。
```

所以本课使用：

```python
from pydantic import Field
```

并写成：

```python
name: str = Field(min_length=1)
goal: str = Field(min_length=1)
python_level: str = Field(pattern="^(beginner|basic|intermediate)$")
```

这不是业务逻辑函数，而是数据契约。

请求体不满足契约时，FastAPI 会在进入你的函数前直接返回错误。

### 请求体模型

在 FastAPI 里，如果一个路径操作函数参数是 Pydantic 模型：

```python
def preview_profile(profile: StudentProfile) -> StudentProfileResponse:
```

FastAPI 会把 HTTP 请求体解析成 `StudentProfile`。

也就是说，客户端发来的 JSON：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner"
}
```

会变成 Python 对象：

```python
profile.name
profile.goal
profile.python_level
```

### 响应模型

FastAPI 的 `response_model` 用于声明接口响应结构。

本课代码：

```python
@app.post("/profile/preview", response_model=StudentProfileResponse)
```

表示：

```text
这个接口的响应应该符合 StudentProfileResponse。
```

`StudentProfileResponse` 比请求体多一个字段：

```python
note_count: int = 0
```

这模拟后续真实资料接口中会返回“笔记数量”。

### `model_dump()`

Pydantic v2 中，模型实例可以用：

```python
profile.model_dump()
```

转换成普通字典。

本课会写：

```python
StudentProfileResponse(**profile.model_dump(), note_count=0)
```

意思是：

```text
把请求体模型里的字段展开成响应模型需要的字段，
再额外添加 note_count。
```

## 5. 代码实现

### 第一步：更新 `app/models.py`

打开：

```text
ai-learning-assistant/app/models.py
```

保留原来的 `Student`：

```python
from typing import TypedDict

from pydantic import BaseModel, Field


class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]
```

新增：

```python
class StudentProfile(BaseModel):
    name: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    python_level: str = Field(pattern="^(beginner|basic|intermediate)$")


class StudentProfileResponse(StudentProfile):
    note_count: int = 0
```

现在 `models.py` 同时服务两个阶段：

```text
Student                 阶段 2 存储层使用
StudentProfile          阶段 3 请求体使用
StudentProfileResponse  阶段 3 响应模型使用
```

### 第二步：更新 `app/api.py`

打开：

```text
ai-learning-assistant/app/api.py
```

导入模型：

```python
from app.models import StudentProfile, StudentProfileResponse
```

新增接口：

```python
@app.post("/profile/preview", response_model=StudentProfileResponse)
def preview_profile(profile: StudentProfile) -> StudentProfileResponse:
    return StudentProfileResponse(**profile.model_dump(), note_count=0)
```

完整文件现在是：

```python
from fastapi import FastAPI

from app.models import StudentProfile, StudentProfileResponse


app = FastAPI(title="AI Learning Assistant")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-learning-assistant",
    }


@app.post("/profile/preview", response_model=StudentProfileResponse)
def preview_profile(profile: StudentProfile) -> StudentProfileResponse:
    return StudentProfileResponse(**profile.model_dump(), note_count=0)
```

注意这个接口叫 `preview`。

它只是演示请求体和响应模型，还不保存数据。

### 第三步：更新 `tests/test_api.py`

在原来的 `/health` 测试后面新增：

```python
def test_preview_profile_returns_response_model() -> None:
    response = client.post(
        "/profile/preview",
        json={
            "name": "Alice",
            "goal": "Learn FastAPI",
            "python_level": "beginner",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "name": "Alice",
        "goal": "Learn FastAPI",
        "python_level": "beginner",
        "note_count": 0,
    }
```

再新增一个非法输入测试：

```python
def test_preview_profile_rejects_invalid_level() -> None:
    response = client.post(
        "/profile/preview",
        json={
            "name": "Alice",
            "goal": "Learn FastAPI",
            "python_level": "expert",
        },
    )

    assert response.status_code == 422
```

这个测试证明：

```text
expert 不是允许的 python_level。
请求会被 Pydantic/FastAPI 拦截。
```

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

确认依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/__init__.py tests/test_storage.py tests/test_api.py
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

打开自动文档：

```text
http://127.0.0.1:8000/docs
```

在文档页面里找到：

```text
POST /profile/preview
```

用这个请求体试一下：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner"
}
```

你应该得到：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner",
  "note_count": 0
}
```

## 7. 常见错误

### 把 Pydantic 模型和 `TypedDict` 混为一谈

`TypedDict` 主要是类型提示：

```python
class Student(TypedDict):
    name: str
```

Pydantic `BaseModel` 会参与运行时解析和校验：

```python
class StudentProfile(BaseModel):
    name: str = Field(min_length=1)
```

FastAPI 请求体应该优先用 Pydantic 模型。

### 写成 `dict` 导致缺少 API 文档

不要把请求体写成：

```python
def preview_profile(profile: dict) -> dict:
```

这样 FastAPI 不知道字段结构，也无法生成清晰的 OpenAPI 文档。

本课写成：

```python
def preview_profile(profile: StudentProfile) -> StudentProfileResponse:
```

### 误以为 422 是程序崩了

如果非法请求返回：

```text
422 Unprocessable Entity
```

这通常表示：

```text
请求体格式或字段值不符合模型要求。
```

这是 FastAPI 和 Pydantic 正常工作，不是程序崩溃。

### 急着在本课保存文件

本课的 `/profile/preview` 不写入 `data/student.json`。

如果现在就把保存逻辑写进去，会和第 3.3 课的目标混在一起。

先把数据契约学清楚，再接真实存储。

## 8. 练习

练习 1：把 `name` 改成空字符串，观察接口返回什么状态码。

请求体：

```json
{
  "name": "",
  "goal": "Learn FastAPI",
  "python_level": "beginner"
}
```

练习 2：给 `StudentProfileResponse` 新增一个字段：

```python
ready: bool = True
```

同步修改测试，让响应中包含：

```json
"ready": true
```

练习 3：把 `python_level` 的正则暂时改成只允许 `beginner`，再用 `basic` 请求，观察测试是否失败。

练习完成后，建议恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `app/models.py` 中存在 `StudentProfile`。
- `app/models.py` 中存在 `StudentProfileResponse`。
- `StudentProfile` 校验 `name`、`goal` 和 `python_level`。
- `POST /profile/preview` 使用 `StudentProfile` 作为请求体。
- `POST /profile/preview` 声明 `response_model=StudentProfileResponse`。
- 合法请求返回 `200` 和 `note_count: 0`。
- 非法 `python_level` 返回 `422`。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。
- `/docs` 能展示 `POST /profile/preview` 的请求体和响应结构。
- 没有在本课提前实现真实保存资料 API。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

Pydantic 模型会贯穿后面的所有 API 和 AI 输出。

| 现在 | 后续升级 |
| --- | --- |
| `StudentProfile` | `GET/POST /profile` 请求和响应结构 |
| `StudentProfileResponse` | 更完整的 API response model |
| 字段校验 | API 边界校验 / Agent 输入校验 |
| `response_model` | 结构化输出和稳定接口契约 |
| `422` | 请求错误处理和用户输入反馈 |
| `model_dump()` | 模型转字典，交给 storage / tool / graph state |

后面 LangChain 和 Deep Agents 会经常需要“结构化数据”。

如果 API 边界一开始就是清晰模型，后面把数据交给 Agent、Graph 或 RAG 流程时会少很多混乱。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-3/03-02-pydantic-models.md`

修改文件：

- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_api.py`
- `ai-learning-assistant/README.md`
- `docs/tutorial/README.md`
- `README.md`

新增模型：

- `StudentProfile`
- `StudentProfileResponse`

新增接口：

```http
POST /profile/preview
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/__init__.py tests/test_storage.py tests/test_api.py
```

API 人工验证：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

然后打开：

```text
http://127.0.0.1:8000/docs
```

验证结果：

- 合法 `POST /profile/preview` 返回包含 `note_count` 的响应。
- 非法 `python_level` 返回 `422`。
- pytest 测试全部通过。
- Python 文件可以编译通过。

下一步：

- 第 3.3 课：学员资料 API，把 `GET/POST /profile` 接到阶段 2 的 `storage.py`。
