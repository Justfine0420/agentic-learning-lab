# 第 3.6 课：API 错误处理

## 1. 本课目标

前面几课已经有了这些接口：

```http
GET /profile
POST /profile
GET /notes
POST /notes
GET /suggestion
```

这些接口在正常输入下能工作。

但真实 API 不能只处理正常输入。

调用方可能会：

- 传一个不存在的笔记编号。
- 传一条只有空格的笔记。
- 传错请求体结构。

本课目标是给学习助手 API 加上第一批明确错误响应：

```http
GET /notes/{note_index}  笔记不存在时返回 404
POST /notes              空白笔记返回 400
```

同时你要理解：

```text
422 是 FastAPI / Pydantic 自动校验错误。
400 / 404 是我们主动抛出的业务错误。
```

## 2. 你会新增什么项目能力

本课之后，项目会新增一个接口：

```http
GET /notes/{note_index}
```

例如：

```http
GET /notes/1
```

返回：

```json
{
  "index": 1,
  "content": "Read FastAPI docs"
}
```

如果笔记不存在：

```http
GET /notes/99
```

返回：

```json
{
  "detail": "学习笔记不存在。"
}
```

状态码是：

```text
404
```

另外，`POST /notes` 会新增业务校验。

如果请求体是：

```json
{
  "content": "   "
}
```

返回：

```json
{
  "detail": "学习笔记不能为空。"
}
```

状态码是：

```text
400
```

## 3. 前置知识

开始前确认你已经理解：

- `GET /notes` 会返回所有学习笔记。
- `POST /notes` 会添加一条学习笔记。
- `student["notes"]` 是一个列表。
- 列表下标从 `0` 开始。
- 用户界面更习惯从 `1` 开始编号。
- Pydantic 会在进入 route 函数前校验请求体。
- pytest 可以断言状态码和响应 JSON。

本课会引入 FastAPI 的：

```python
HTTPException
```

它用于主动返回错误响应。

## 4. 核心概念

### `HTTPException` 表达业务错误

FastAPI 推荐用 `HTTPException` 抛出 HTTP 错误：

```python
raise HTTPException(status_code=404, detail="学习笔记不存在。")
```

这句话的意思是：

```text
停止当前 route。
返回 404。
响应体里放 detail。
```

响应会变成：

```json
{
  "detail": "学习笔记不存在。"
}
```

### 422 和 400 的区别

第 3.2 课开始，你已经见过 `422`。

例如：

```json
{
  "content": ""
}
```

因为 `NoteCreate` 里写了：

```python
content: str = Field(min_length=1)
```

所以空字符串会被 Pydantic 拦住，返回 `422`。

但下面这种输入：

```json
{
  "content": "   "
}
```

长度不是 0，所以 Pydantic 会放行。

可是从业务角度看，只有空格的笔记没有意义。

这时我们用：

```python
if note.content.strip() == "":
    raise HTTPException(status_code=400, detail="学习笔记不能为空。")
```

所以：

| 场景 | 谁处理 | 状态码 |
| --- | --- | --- |
| 字段缺失 | Pydantic | 422 |
| 空字符串 | Pydantic | 422 |
| 只有空格 | 业务规则 | 400 |
| 笔记编号不存在 | 业务规则 | 404 |

### API 编号和列表下标不是一回事

Python 列表下标从 0 开始：

```python
notes[0]
```

但 API 给用户看的笔记编号更适合从 1 开始：

```http
GET /notes/1
```

所以代码里要做转换：

```python
notes[note_index - 1]
```

这也是本课最容易写错的地方。

## 5. 代码实现

### 第一步：导入 `HTTPException`

打开：

```text
ai-learning-assistant/app/api.py
```

把导入改成：

```python
from fastapi import FastAPI, HTTPException
```

### 第二步：新增单条笔记响应模型

打开：

```text
ai-learning-assistant/app/models.py
```

新增：

```python
class NoteResponse(BaseModel):
    index: int
    content: str
```

它用于描述单条笔记响应：

```json
{
  "index": 1,
  "content": "Read FastAPI docs"
}
```

### 第三步：新增 `GET /notes/{note_index}`

在 `GET /notes` 后面新增：

```python
@app.get("/notes/{note_index}", response_model=NoteResponse)
def get_note(note_index: int) -> NoteResponse:
    student = load_student()
    notes = student["notes"]

    if note_index < 1 or note_index > len(notes):
        raise HTTPException(status_code=404, detail="学习笔记不存在。")

    return NoteResponse(index=note_index, content=notes[note_index - 1])
```

这里有两个关键点。

第一，先判断范围：

```python
if note_index < 1 or note_index > len(notes):
```

这样 `0`、负数、超过数量的编号都会返回 404。

第二，读取列表时要减 1：

```python
notes[note_index - 1]
```

因为 API 编号从 1 开始，Python 下标从 0 开始。

### 第四步：给 `POST /notes` 增加空白校验

把原来的：

```python
@app.post("/notes", response_model=NotesResponse)
def add_note(note: NoteCreate) -> NotesResponse:
    student = load_student()
    student["notes"].append(note.content)
    save_student(student)
```

改成：

```python
@app.post("/notes", response_model=NotesResponse)
def add_note(note: NoteCreate) -> NotesResponse:
    if note.content.strip() == "":
        raise HTTPException(status_code=400, detail="学习笔记不能为空。")

    student = load_student()
    student["notes"].append(note.content)
    save_student(student)
```

注意：

```python
strip()
```

会去掉字符串两边空白。

如果去掉后是空字符串，就说明这条笔记只有空格、换行或制表符。

这类内容不应该保存。

### 第五步：测试单条笔记读取

打开：

```text
ai-learning-assistant/tests/test_api.py
```

新增：

```python
def test_get_note_returns_one_saved_note(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Dana",
            "goal": "Review APIs",
            "python_level": "basic",
            "notes": ["Read FastAPI docs", "Write API tests"],
        }
    )

    response = client.get("/notes/2")

    assert response.status_code == 200
    assert response.json() == {
        "index": 2,
        "content": "Write API tests",
    }
```

这个测试确认：

```text
GET /notes/2
```

会返回第二条笔记。

### 第六步：测试笔记不存在

继续新增：

```python
def test_get_note_returns_404_when_note_missing(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Dana",
            "goal": "Review APIs",
            "python_level": "basic",
            "notes": ["Read FastAPI docs"],
        }
    )

    response = client.get("/notes/2")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "学习笔记不存在。",
    }
```

这里 `notes` 只有一条。

所以请求第二条应该返回 404。

### 第七步：测试空白笔记

继续新增：

```python
def test_post_notes_rejects_blank_note_with_business_error(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Eve",
            "goal": "Build note API",
            "python_level": "intermediate",
            "notes": ["Existing note"],
        }
    )

    response = client.post(
        "/notes",
        json={
            "content": "   ",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "学习笔记不能为空。",
    }
    assert storage.load_student()["notes"] == ["Existing note"]
```

最后一行断言很重要：

```python
assert storage.load_student()["notes"] == ["Existing note"]
```

它证明空白笔记没有被保存。

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
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

访问文档：

```text
http://127.0.0.1:8000/docs
```

你应该能看到：

```text
GET /notes/{note_index}
```

手动调用：

```http
GET http://127.0.0.1:8000/notes/1
```

如果已有第一条笔记，会返回：

```json
{
  "index": 1,
  "content": "..."
}
```

再试一个不存在的编号：

```http
GET http://127.0.0.1:8000/notes/999
```

你应该看到：

```json
{
  "detail": "学习笔记不存在。"
}
```

## 7. 常见错误

### 把 404 写成 200

错误方向：

```python
return {"error": "学习笔记不存在。"}
```

这样 HTTP 状态码仍然是 200。

调用方会误以为请求成功。

正确方向：

```python
raise HTTPException(status_code=404, detail="学习笔记不存在。")
```

### API 编号忘记减 1

错误写法：

```python
notes[note_index]
```

如果请求：

```http
GET /notes/1
```

它会返回第二条笔记。

正确写法：

```python
notes[note_index - 1]
```

### 把 Pydantic 校验和业务校验混在一起

Pydantic 适合处理结构问题：

```text
字段缺失
类型错误
字符串太短
```

业务校验适合处理业务规则：

```text
只有空格的笔记没有意义
笔记编号不存在
```

不要把所有错误都强行塞进一个地方。

### 返回错误后继续执行保存

如果你不用 `raise`，而只是构造一个错误对象，函数可能继续往下执行。

`raise HTTPException(...)` 会中断当前函数。

这就是为什么空白笔记不会被保存。

## 8. 练习

练习 1：请求：

```http
GET /notes/0
```

观察返回状态码。

练习 2：请求：

```http
GET /notes/-1
```

观察返回状态码。

练习 3：请求：

```http
GET /notes/abc
```

观察它和 `/notes/999` 的状态码有什么不同。

提示：`note_index` 的类型是 `int`。

练习 4：把空白笔记错误信息改成你自己的文案，并同步更新测试。

练习完成后，建议恢复到课程版本。

## 9. 验收标准

本课完成时，应满足：

- `app/api.py` 导入 `HTTPException`。
- 存在 `NoteResponse`。
- 存在 `GET /notes/{note_index}`。
- `GET /notes/{note_index}` 能返回单条笔记。
- 笔记编号不存在时返回 `404`。
- 404 响应体包含 `detail`。
- `POST /notes` 会拒绝只有空格的笔记。
- 空白笔记返回 `400`。
- 空白笔记不会写入 `data/student.json`。
- 原有 `GET /notes`、`POST /notes`、`GET /suggestion` 不退化。
- pytest 覆盖 200、400、404 和原有 422。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。
- 没有引入数据库、LLM 或 LangChain。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

错误处理不是只给前端看的。

后续 Agent 调用工具或 API 时，也需要知道失败原因。

| 现在 | 后续升级 |
| --- | --- |
| `HTTPException` | 工具调用失败的结构化错误 |
| `404` | Agent 查询不存在资料时的恢复路径 |
| `400` | 用户输入不符合业务规则时的提示 |
| `422` | Pydantic / 结构化输入校验 |
| `GET /notes/{note_index}` | LangChain 工具读取指定笔记 |

到了 LangChain 阶段，Agent 可能会调用“读取第 N 条笔记”的工具。

如果笔记不存在，工具不能假装成功。

到了 LangGraph 阶段，节点失败后可以进入重试、提示用户或换路径。

到了 Deep Agents 阶段，长期任务需要可靠地区分：

```text
输入格式错了
业务对象不存在
任务可以重试
任务应该停止
```

本课就是在给这些能力铺第一层错误语义。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-3/03-06-api-error-handling.md`

修改文件：

- `ai-learning-assistant/app/models.py`
- `ai-learning-assistant/app/api.py`
- `ai-learning-assistant/tests/test_api.py`
- `ai-learning-assistant/README.md`
- `docs/tutorial/README.md`
- `README.md`

新增接口：

```http
GET /notes/{note_index}
```

新增模型：

```python
NoteResponse
```

新增错误响应：

```text
404 学习笔记不存在。
400 学习笔记不能为空。
```

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pip install -r requirements.txt
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

API 人工验证：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

然后访问：

```text
http://127.0.0.1:8000/docs
```

验证结果：

- `GET /notes/{note_index}` 可以读取指定笔记。
- 不存在的笔记返回 `404`。
- 空白笔记返回 `400`。
- 空字符串仍由 Pydantic 返回 `422`。
- pytest 测试全部通过。
- Python 文件可以编译通过。

下一步：

- 第 3.7 课：存储边界与数据库迁移预告，解释为什么当前阶段继续使用 JSON，以及什么时候应该迁移到 SQLite / PostgreSQL。
