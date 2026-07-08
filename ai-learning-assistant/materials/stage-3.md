# Stage 3 补充学习资料：FastAPI、Pydantic 与接口测试

本文记录 Stage 3 中围绕 FastAPI API、Pydantic 模型、接口测试和错误处理补充出来的知识点。

- `FastAPI()`、`@app.get()`、`@app.post()` 是什么
- `response_model` 为什么会校验返回值
- `BaseModel`、`Field()`、`model_dump()` 的用法
- `**dict` 为什么可以把字典展开成参数
- 请求模型和响应模型为什么要分开
- `TestClient`、`client.get()`、`client.post()` 怎么测试接口
- `HTTPException`、`raise`、`400 / 404 / 422 / 500` 的区别
- `.venv`、`python -m pip install -r requirements.txt` 与解释器选择

## 目录

- [1. Stage 3 在项目中新增了什么](#1-stage-3-在项目中新增了什么)
- [2. FastAPI 应用对象是什么](#2-fastapi-应用对象是什么)
- [3. 路由装饰器是什么](#3-路由装饰器是什么)
- [4. 请求模型：`profile: StudentProfile`](#4-请求模型profile-studentprofile)
- [5. 响应模型：`response_model=...`](#5-响应模型response_model)
- [6. Pydantic 的 `BaseModel` 和 `Field()`](#6-pydantic-的-basemodel-和-field)
- [7. `Field(default_factory=list)`](#7-fielddefault_factorylist)
- [8. `model_dump()` 与 `**dict`](#8-model_dump-与-dict)
- [9. 请求模型和响应模型为什么分开](#9-请求模型和响应模型为什么分开)
- [10. `return build_suggestion(...)` 为什么会导致 500](#10-return-build_suggestion-为什么会导致-500)
- [11. `HTTPException` 与 `raise`](#11-httpexception-与-raise)
- [12. 400、404、422、500 怎么区分](#12-400404422500-怎么区分)
- [13. `TestClient` 怎么测试 API](#13-testclient-怎么测试-api)
- [14. `.venv`、解释器和依赖安装](#14-venv解释器和依赖安装)
- [15. `python -m` 和 `pip -r` 是什么](#15-python--m-和-pip--r-是什么)
- [16. 当前项目中的 API 数据流](#16-当前项目中的-api-数据流)

## 1. Stage 3 在项目中新增了什么

Stage 2 主要是命令行程序和 JSON 文件保存。

Stage 3 开始把学习助手变成 Web API。

当前项目新增了：

```text
app/api.py          FastAPI API 入口
app/models.py       TypedDict 和 Pydantic 模型
app/suggestions.py  学习建议规则
tests/test_api.py   API 测试
```

当前 API 包括：

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

可以这样启动 API：

```powershell
python -m uvicorn app.api:app --reload
```

其中：

```text
app.api
```

表示 `app/api.py` 这个模块。

```text
app.api:app
```

冒号后面的 `app` 是 `api.py` 里创建的 FastAPI 应用对象。

## 2. FastAPI 应用对象是什么

当前代码：

```python
from fastapi import FastAPI, HTTPException


app = FastAPI(title="AI Learning Assistant")
```

`FastAPI()` 会创建一个 Web API 应用。

可以理解为：

```text
app 是整个 API 服务的入口。
所有接口都挂在 app 上。
```

例如：

```python
@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-learning-assistant",
    }
```

这表示：

```text
当有人请求 GET /health 时，执行 health_check()。
```

## 3. 路由装饰器是什么

FastAPI 中常见：

```python
@app.get("/profile")
def get_profile():
    ...
```

和：

```python
@app.post("/profile")
def update_profile():
    ...
```

这里的 `@app.get(...)`、`@app.post(...)` 是装饰器。

在这里可以先理解为：

```text
把一个普通函数注册成 API 接口。
```

`GET` 通常用来读取数据。

```http
GET /profile
GET /notes
GET /suggestion
```

`POST` 通常用来提交或修改数据。

```http
POST /profile
POST /notes
```

函数名本身不会决定接口路径，路径由装饰器里的字符串决定：

```python
@app.get("/notes/{note_index}")
def get_note(note_index: int):
    ...
```

这里的路径是：

```text
/notes/{note_index}
```

不是：

```text
get_note
```

## 4. 请求模型：`profile: StudentProfile`

当前代码：

```python
@app.post("/profile", response_model=StudentProfileResponse)
def update_profile(profile: StudentProfile) -> StudentProfileResponse:
    ...
```

这里的：

```python
profile: StudentProfile
```

告诉 FastAPI：

```text
这个接口需要一个请求体。
请求体应该符合 StudentProfile 模型。
```

当前模型：

```python
class StudentProfile(BaseModel):
    name: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    python_level: str = Field(pattern="^(beginner|basic|intermediate)$")
```

所以请求体应该类似：

```json
{
  "name": "Alice",
  "goal": "Learn FastAPI",
  "python_level": "beginner"
}
```

FastAPI 收到请求后，会自动：

```text
1. 读取 JSON 请求体
2. 用 StudentProfile 做校验
3. 校验通过后创建 StudentProfile 对象
4. 把对象传给 update_profile(profile)
```

所以函数里可以写：

```python
profile.name
profile.goal
profile.python_level
```

而不是：

```python
profile["name"]
```

因为 `profile` 是 Pydantic 对象，不是普通字典。

## 5. 响应模型：`response_model=...`

当前代码：

```python
@app.get("/suggestion", response_model=SuggestionResponse)
def get_suggestion() -> SuggestionResponse:
    ...
```

`response_model=SuggestionResponse` 的意思是：

```text
这个接口返回的数据应该符合 SuggestionResponse 模型。
```

当前模型：

```python
class SuggestionResponse(BaseModel):
    python_level: str = ""
    suggestion: str
```

所以接口应该返回类似：

```json
{
  "python_level": "beginner",
  "suggestion": "建议：今天学习变量、函数、字典。"
}
```

如果接口返回的内容不符合 `response_model`，FastAPI 会在返回响应前发现问题。

例如：

```python
return "建议：今天学习变量、函数、字典。"
```

这是字符串，不是 `SuggestionResponse` 需要的对象结构，就会导致响应校验错误。

## 6. Pydantic 的 `BaseModel` 和 `Field()`

Pydantic 模型通常继承 `BaseModel`：

```python
class NoteCreate(BaseModel):
    content: str = Field(min_length=1)
```

它表示：

```text
NoteCreate 是一个请求体模型。
content 必须是字符串。
content 至少有 1 个字符。
```

所以这个请求会通过：

```json
{
  "content": "New API note"
}
```

这个请求会被 Pydantic 拦住：

```json
{
  "content": ""
}
```

因为：

```python
Field(min_length=1)
```

要求长度至少为 1。

`Field()` 还可以写正则规则：

```python
python_level: str = Field(pattern="^(beginner|basic|intermediate)$")
```

意思是 `python_level` 只能是：

```text
beginner
basic
intermediate
```

如果传：

```json
{
  "python_level": "expert"
}
```

FastAPI 会返回 `422`。

## 7. `Field(default_factory=list)`

当前模型：

```python
class NotesResponse(BaseModel):
    notes: list[str] = Field(default_factory=list)
    note_count: int = 0
```

`Field(default_factory=list)` 的意思是：

```text
如果没有传 notes，就自动调用 list()，生成一个新的空列表。
```

也就是默认：

```python
notes = []
```

但它比直接写 `notes: list[str] = []` 更适合表达“每个对象都有自己的空列表”。

初学阶段可以记：

```text
default_factory=list = 默认创建一个新的空列表。
default_factory=dict = 默认创建一个新的空字典。
```

字符串、数字这种不可变默认值可以直接写：

```python
note_count: int = 0
python_level: str = ""
```

## 8. `model_dump()` 与 `**dict`

当前代码：

```python
@app.post("/profile/preview", response_model=StudentProfileResponse)
def preview_profile(profile: StudentProfile) -> StudentProfileResponse:
    return StudentProfileResponse(**profile.model_dump(), note_count=0)
```

`profile.model_dump()` 会把 Pydantic 对象转成普通字典。

如果 `profile` 是：

```python
StudentProfile(
    name="Alice",
    goal="Learn FastAPI",
    python_level="beginner",
)
```

那么：

```python
profile.model_dump()
```

会得到：

```python
{
    "name": "Alice",
    "goal": "Learn FastAPI",
    "python_level": "beginner",
}
```

`**profile.model_dump()` 表示把字典展开成关键字参数。

所以：

```python
StudentProfileResponse(**profile.model_dump(), note_count=0)
```

等价于：

```python
StudentProfileResponse(
    name="Alice",
    goal="Learn FastAPI",
    python_level="beginner",
    note_count=0,
)
```

可以把 `**dict` 先理解成：

```text
把字典里的 key/value 展开成 name=value 这种参数。
```

## 9. 请求模型和响应模型为什么分开

当前有：

```python
class StudentProfile(BaseModel):
    name: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    python_level: str = Field(pattern="^(beginner|basic|intermediate)$")
```

还有：

```python
class StudentProfileResponse(BaseModel):
    name: str = ""
    goal: str = ""
    python_level: str = ""
    note_count: int = 0
```

`StudentProfile` 是请求模型。

```text
用户提交资料时，必须传 name、goal、python_level。
```

`StudentProfileResponse` 是响应模型。

```text
接口返回资料时，除了 name、goal、python_level，还会返回 note_count。
```

所以它们分开是合理的。

请求模型更关心：

```text
用户必须传什么？
用户传的值是否合法？
```

响应模型更关心：

```text
接口要返回什么？
返回给调用方的数据结构是什么？
```

注意：模型之间可以继承，但不是必须。

如果写：

```python
class StudentProfileResponse(StudentProfile):
    note_count: int = 0
```

表示响应模型继承请求模型的字段，再额外增加 `note_count`。

当前项目使用的是显式写出字段：

```python
class StudentProfileResponse(BaseModel):
    name: str = ""
    goal: str = ""
    python_level: str = ""
    note_count: int = 0
```

这让请求和响应的边界更清楚。

## 10. `return build_suggestion(...)` 为什么会导致 500

当前正确写法：

```python
@app.get("/suggestion", response_model=SuggestionResponse)
def get_suggestion() -> SuggestionResponse:
    student = load_student()

    return SuggestionResponse(
        python_level=student["python_level"],
        suggestion=build_suggestion(student["python_level"]),
    )
```

`build_suggestion(...)` 返回的是字符串。

例如：

```python
"建议：今天学习变量、函数、字典。"
```

但路由声明了：

```python
response_model=SuggestionResponse
```

也就是 FastAPI 期待返回：

```json
{
  "python_level": "beginner",
  "suggestion": "建议：今天学习变量、函数、字典。"
}
```

如果直接写：

```python
return build_suggestion(student["python_level"])
```

就会返回字符串，而不是对象结构。

FastAPI 会尝试把字符串校验成 `SuggestionResponse`，校验失败后抛出响应校验错误，接口表现为：

```text
Internal Server Error
```

所以要么返回 `SuggestionResponse` 对象，要么把接口设计改成返回字符串。

当前项目推荐保留对象结构。

## 11. `HTTPException` 与 `raise`

当前代码：

```python
from fastapi import FastAPI, HTTPException
```

`HTTPException` 是 FastAPI 提供的 HTTP 错误类型。

当业务上发现请求不合理时，可以主动抛出：

```python
raise HTTPException(status_code=404, detail="学习笔记不存在。")
```

`raise` 是 Python 关键字，意思是：

```text
主动抛出异常。
```

这里的 `HTTPException` 不是关键字，而是一个异常类。

结构可以这样看：

```python
raise 异常类型(错误信息或参数)
```

普通 Python 里也可以写：

```python
raise ValueError("age 不能是负数")
```

其中：

```text
raise      关键字
ValueError 异常类
"..."      错误提示信息
```

在 FastAPI 里，抛出 `HTTPException` 后，FastAPI 会把它转换成 HTTP 响应。

例如：

```python
raise HTTPException(status_code=400, detail="学习笔记不能为空。")
```

响应会是：

```json
{
  "detail": "学习笔记不能为空。"
}
```

状态码是：

```text
400
```

## 12. 400、404、422、500 怎么区分

Stage 3 当前会遇到几种状态码。

`200` 表示成功。

```text
GET /health
POST /notes
```

正常处理完成后返回 `200`。

`400` 表示业务上认为请求不合理。

当前项目里：

```python
if note.content.strip() == "":
    raise HTTPException(status_code=400, detail="学习笔记不能为空。")
```

`content=""` 会先被 Pydantic 拦住，返回 `422`。

`content="   "` 长度不是 0，所以能通过 Pydantic，但业务上仍然是空白笔记，于是返回 `400`。

`404` 表示资源不存在。

当前项目里：

```python
if note_index < 1 or note_index > len(notes):
    raise HTTPException(status_code=404, detail="学习笔记不存在。")
```

比如只有 1 条笔记，却请求：

```http
GET /notes/2
```

就返回 `404`。

`422` 是 FastAPI / Pydantic 自动校验失败。

例如：

```json
{
  "python_level": "expert"
}
```

不符合：

```python
Field(pattern="^(beginner|basic|intermediate)$")
```

所以返回 `422`。

`500` 表示服务端内部错误。

例如接口声明了：

```python
response_model=SuggestionResponse
```

却返回字符串：

```python
return build_suggestion(student["python_level"])
```

这会触发响应校验错误，表现为 `500`。

## 13. `TestClient` 怎么测试 API

当前测试里有：

```python
from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)
```

`TestClient(app)` 的作用是：

```text
在测试里模拟一个 HTTP 客户端，不需要真的启动 uvicorn 服务。
```

测试 GET 接口：

```python
response = client.get("/health")

assert response.status_code == 200
assert response.json() == {
    "status": "ok",
    "service": "ai-learning-assistant",
}
```

测试 POST 接口：

```python
response = client.post(
    "/notes",
    json={
        "content": "New API note",
    },
)
```

这里的 `json={...}` 表示把这个字典作为 JSON 请求体发送。

响应对象常用：

```python
response.status_code
response.json()
```

`status_code` 是 HTTP 状态码。

`json()` 会把响应 JSON 转成 Python 字典或列表。

### 测试为什么要用 `use_tmp_storage(tmp_path)`

API 测试也会读写 `storage.DATA_FILE`。

如果不改路径，测试会动真实文件：

```text
data/student.json
```

所以测试里继续使用：

```python
def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"
```

这样每个测试都使用临时文件，不污染真实学习数据。

## 14. `.venv`、解释器和依赖安装

`.venv` 是当前项目自己的虚拟环境。

如果依赖装在：

```text
ai-learning-assistant/.venv
```

但 PyCharm 选择了另一个项目的解释器，编辑器就可能报：

```text
未解析的引用 'fastapi'
```

要看解释器显示名背后的真实路径。

正确解释器应该类似：

```text
<workspace-root>/ai-learning-assistant/.venv/Scripts/python.exe
```

不要把 `python.exe` 填到 `Script path` 里。

它应该作为：

```text
Python interpreter
```

主程序运行配置可以是：

```text
Module name: app.main
Working directory: <workspace-root>/ai-learning-assistant
```

API 运行配置可以是：

```text
Module name: uvicorn
Parameters: app.api:app --reload
Working directory: <workspace-root>/ai-learning-assistant
```

如果出现类似：

```text
SyntaxError: Non-UTF-8 code starting with ...
```

并且报错文件是：

```text
.venv/Scripts/python.exe
```

通常说明你把一个 `python.exe` 当成脚本运行了。

正确做法是：

```text
python.exe 是解释器，不是 Script path。
```

## 15. `python -m` 和 `pip -r` 是什么

`-m` 是 Python 解释器参数，意思是：

```text
把后面的名字当成模块运行。
```

例如：

```powershell
python -m pytest
```

表示运行 `pytest` 模块。

```powershell
python -m uvicorn app.api:app --reload
```

表示运行 `uvicorn` 模块。

```powershell
python -m pip install -r requirements.txt
```

表示运行 `pip` 模块，并安装依赖。

`-r` 是 `pip install` 的参数。

```powershell
python -m pip install -r requirements.txt
```

意思是：

```text
让 pip 读取 requirements.txt，然后安装里面列出的所有依赖。
```

注意安装到哪里，取决于前面的 `python` 是谁。

如果激活了 `.venv`，并且：

```powershell
python -c "import sys; print(sys.executable)"
```

输出的是：

```text
<workspace-root>/ai-learning-assistant/.venv/Scripts/python.exe
```

那么依赖就安装到当前项目的 `.venv`。

如果用：

```powershell
py -3.13 -m pip install -r requirements.txt
```

通常是安装到 Python 3.13 的全局环境，不一定是 `.venv`。

更稳的方式是直接指定 `.venv` 的解释器：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 16. 当前项目中的 API 数据流

### `GET /profile`

```text
client / browser
-> GET /profile
-> get_profile()
-> load_student()
-> StudentProfileResponse(...)
-> JSON 响应
```

返回：

```json
{
  "name": "Bob",
  "goal": "Build APIs",
  "python_level": "basic",
  "note_count": 1
}
```

### `POST /profile`

```text
client 提交 JSON
-> FastAPI 用 StudentProfile 校验请求体
-> update_profile(profile)
-> load_student() 读取现有 notes
-> 组装 updated_student
-> save_student(updated_student)
-> StudentProfileResponse(...)
```

重点：

```text
POST /profile 会更新资料，但保留已有 notes。
```

### `GET /notes`

```text
GET /notes
-> get_notes()
-> load_student()
-> NotesResponse(notes=..., note_count=...)
```

### `GET /notes/{note_index}`

```text
GET /notes/2
-> get_note(note_index=2)
-> load_student()
-> 检查 note_index 是否存在
-> 返回 NoteResponse(index=2, content=...)
```

注意：

```python
notes[note_index - 1]
```

是因为 API 使用从 1 开始的编号，但 Python 列表下标从 0 开始。

### `POST /notes`

```text
client 提交 {"content": "..."}
-> FastAPI 用 NoteCreate 校验请求体
-> add_note(note)
-> 检查 note.content.strip() 是否为空
-> load_student()
-> student["notes"].append(note.content)
-> save_student(student)
-> NotesResponse(...)
```

### `GET /suggestion`

```text
GET /suggestion
-> get_suggestion()
-> load_student()
-> build_suggestion(student["python_level"])
-> SuggestionResponse(...)
```

这里一定要返回 `SuggestionResponse` 结构，而不是只返回 `build_suggestion(...)` 的字符串。

## 17. 现阶段建议先记住什么

如果内容太多，Stage 3 先抓住这几条：

```text
1. FastAPI route = 一个普通 Python 函数 + @app.get/@app.post。
2. 请求体模型写在函数参数里，例如 profile: StudentProfile。
3. 响应模型写在装饰器里，例如 response_model=StudentProfileResponse。
4. Pydantic 会自动校验请求体，不合法通常返回 422。
5. 业务错误用 raise HTTPException(...) 主动返回 400 或 404。
6. response_model 会校验返回值，返回错结构可能导致 500。
7. TestClient 可以不用启动服务，直接在测试里调用 API。
8. .venv 是项目自己的依赖环境，PyCharm 要选对解释器路径。
```
