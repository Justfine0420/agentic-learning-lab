# 第 3.7 课：存储边界与数据库迁移预告

## 1. 本课目标

第 3 阶段已经把学习助手暴露成了一组 FastAPI 接口：

```http
GET /profile
POST /profile
GET /notes
GET /notes/{note_index}
POST /notes
GET /suggestion
```

这些接口目前都通过：

```text
data/student.json
```

保存和读取数据。

你可能会问：

```text
为什么不直接落数据库？
```

这是一个好问题。

本课不写新功能，也不把项目改成数据库。

本课目标是让你能解释：

- 当前为什么先用 JSON。
- JSON 存储的边界在哪里。
- 什么时候应该迁移到 SQLite 或 PostgreSQL。
- 后续迁移数据库前，为什么要先保护好 `storage.py` 这个存储边界。

这节课是阶段 3 的收口课。

它让你知道当前实现不是最终架构，而是一个有意设计的过渡形态。

## 2. 你会新增什么项目能力

本课不新增 API。

本课新增的是架构判断能力：

```text
知道现在的数据从哪里来。
知道 API 和存储之间的边界在哪里。
知道 JSON 什么时候够用。
知道数据库什么时候必须上。
知道未来迁移数据库时不要把 SQL 直接塞进 route。
```

当前项目的数据路径是：

```text
FastAPI route
-> load_student()
-> data/student.json
```

写入路径是：

```text
FastAPI route
-> save_student(student)
-> data/student.json
```

也就是说，API 代码没有直接操作 JSON 文件。

它只调用：

```python
load_student()
save_student(student)
```

这就是当前最小版本的存储边界。

## 3. 前置知识

开始前确认你已经理解：

- 阶段 2 用 JSON 文件实现了本地持久化。
- `storage.py` 负责读取、校验、修复和保存 `student`。
- `api.py` 通过 `load_student()` 和 `save_student()` 使用数据。
- `tests/test_storage.py` 测试存储行为。
- `tests/test_api.py` 测试 API 行为。
- `data/student.json` 是本地运行数据，不应该提交到仓库。

你还需要能读懂当前数据结构：

```python
class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]
```

这个结构以后会继续升级。

但现在它还是一个单用户学习档案。

## 4. 核心概念

### JSON 不是“没存储”

很多人会把“没有数据库”误解成“没有持久化”。

这是错的。

当前项目已经有持久化：

```text
data/student.json
```

它能做到：

- 程序重启后数据还在。
- 学员资料能保存。
- 学习笔记能追加。
- 测试可以用临时文件隔离。
- 学习者能直接打开文件观察数据。

所以当前不是“没落库”，而是“先用文件作为最小持久化方案”。

### 为什么当前阶段不用数据库

第 3 阶段的学习重点是 FastAPI：

```text
route
request body
response_model
HTTPException
TestClient
```

如果现在直接加入数据库，学习者会立刻面对：

```text
SQL
连接字符串
Session
ORM
迁移脚本
事务
表结构
测试数据库
```

这些都很重要。

但它们不是第 3 阶段的目标。

当前先保留 JSON，是为了让你把 FastAPI 的核心能力学扎实。

### JSON 的边界

JSON 很适合当前阶段，但它有明显边界。

| 问题 | JSON 文件的限制 |
| --- | --- |
| 多用户 | 当前只有一个 `student.json`，无法自然区分用户 |
| 并发写入 | 多个请求同时写文件时，容易互相覆盖 |
| 查询能力 | 想按标签、时间、关键词查笔记会很笨重 |
| 分页 | 文件越大，读取整个 JSON 越浪费 |
| 部署 | 很多云平台的本地磁盘不适合作为长期数据源 |
| 数据演进 | 字段变多后，手写兼容逻辑会越来越复杂 |
| 备份恢复 | 文件备份可以做，但缺少数据库级工具链 |

所以 JSON 是教学和早期原型的好选择。

它不是长期生产架构。

### `storage.py` 是当前的存储边界

现在的 route 没有这样写：

```python
with open("data/student.json") as file:
    ...
```

而是这样写：

```python
student = load_student()
save_student(student)
```

这很关键。

因为以后从 JSON 换成数据库时，理想情况是：

```text
API route 少改。
测试少改。
主要替换 storage / repository 实现。
```

当前的 `storage.py` 已经是一个很小的边界雏形。

后续可以升级成：

```text
repositories/
└── student_repository.py
```

或者：

```text
app/
├── storage.py
├── repositories/
│   └── student.py
└── database.py
```

但现在不需要急着创建这些目录。

没有真实复杂度时提前建抽象，只会增加学习负担。

### SQLite 和 PostgreSQL 的迁移时机

未来可以按这个顺序考虑：

| 阶段 | 适合方案 | 判断依据 |
| --- | --- | --- |
| 当前教程早期 | JSON | 单用户、低并发、可观察、易测试 |
| 本地数据库入门 | SQLite | 需要 SQL、表结构、简单查询，但还不需要数据库服务器 |
| 正式服务端 | PostgreSQL | 多用户、并发、事务、权限、备份、部署稳定性 |

SQLite 的优势是轻量、单文件、零服务进程，适合本地应用和教学过渡。

PostgreSQL 更适合长期运行的服务端应用，尤其是多用户、并发读写和事务完整性要求更高时。

## 5. 代码实现

本课不改代码。

你要做的是读懂当前边界。

### 第一步：查看 `storage.py`

打开：

```text
ai-learning-assistant/app/storage.py
```

关注这几个函数：

```python
def load_student() -> Student:
    ...


def save_student(student: Student) -> None:
    ...
```

它们是当前所有数据读写的入口。

同时还有这些辅助函数：

```python
create_default_student()
is_valid_student(data)
normalize_student(data)
backup_broken_data()
```

这些函数解决的是 JSON 文件时代的具体问题：

- 文件不存在怎么办。
- JSON 损坏怎么办。
- 字段缺失怎么办。
- 旧数据格式不完整怎么办。

### 第二步：查看 API 如何使用存储

打开：

```text
ai-learning-assistant/app/api.py
```

你会看到：

```python
from app.storage import load_student, save_student
```

然后 route 里调用：

```python
student = load_student()
```

以及：

```python
save_student(updated_student)
```

这说明 API 只依赖存储函数。

它没有关心底层到底是 JSON、SQLite，还是 PostgreSQL。

这是好事。

### 第三步：查看测试如何隔离存储

打开：

```text
ai-learning-assistant/tests/test_api.py
```

你会看到：

```python
def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"
```

这说明 API 测试没有直接污染真实：

```text
data/student.json
```

后续换成数据库时，也要保留这个习惯：

```text
测试用测试数据库。
开发用开发数据库。
生产用生产数据库。
```

### 第四步：想象未来迁移步骤

未来如果要迁移数据库，不应该一步到位乱改。

更稳的顺序是：

```text
1. 先确认当前 API 测试全通过。
2. 给存储层定义更明确的接口。
3. 保留 JSON 实现，补充 repository 测试。
4. 新增 SQLite 实现。
5. 让测试先跑通 SQLite。
6. 再让 API 切换到新的 repository。
7. 最后考虑 PostgreSQL 和迁移脚本。
```

也就是说，迁移数据库不是把：

```python
json.load(...)
```

直接替换成：

```python
SELECT ...
```

真正要迁移的是“存储实现”，不是“API 业务语义”。

## 6. 运行方式

进入项目目录：

```powershell
cd ai-learning-assistant
```

运行测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

你也可以检查 API 文件没有直接操作 JSON：

```powershell
rg "json|open\\(" app/api.py
```

如果没有输出，说明 API 目前没有直接读写 JSON 文件。

这不是唯一标准，但它能帮助你观察存储边界。

## 7. 常见错误

### 看到 JSON 就急着上数据库

数据库很重要。

但在第 3 阶段直接上数据库，会把学习重点打乱。

你现在应该先掌握：

```text
API 如何接收请求。
API 如何返回响应。
API 如何处理错误。
API 如何测试。
```

数据库可以后面单独学。

### 把 SQL 写进 route

未来哪怕引入数据库，也不要在 route 里堆 SQL：

```python
@app.get("/profile")
def get_profile():
    cursor.execute("SELECT ...")
```

这会让 API 层和存储层绑死。

更好的方向是：

```python
student = student_repository.get_current_student()
```

route 应该表达业务流程。

repository 才应该处理存储细节。

### 以为 SQLite 和 PostgreSQL 是同一个层级的问题

SQLite 和 PostgreSQL 都是数据库，但适用场景不同。

SQLite 更像一个嵌入到应用里的轻量 SQL 存储。

PostgreSQL 是独立的数据库服务，更适合正式服务端、多用户和高并发场景。

不要因为“迟早要生产化”就跳过 SQLite。

也不要因为 SQLite 简单，就把它当成永远的生产答案。

### 忽略测试迁移

存储切换最容易坏的是测试。

如果以后换数据库，必须先回答：

```text
测试数据库怎么创建？
每个测试如何隔离数据？
测试结束如何清理？
迁移脚本如何验证？
```

不解决这些问题，数据库迁移会让项目变脆。

### 提交本地学习数据

`data/student.json` 是本地运行数据。

它不应该进入 Git 提交。

教程仓库要提交的是：

```text
代码
测试
课程文档
示例配置
```

不是你本地的学习档案。

## 8. 练习

练习 1：画出当前数据流：

```text
POST /notes
-> add_note()
-> load_student()
-> student["notes"].append(...)
-> save_student()
-> data/student.json
```

练习 2：列出当前项目中所有调用 `save_student()` 的位置。

可以运行：

```powershell
rg "save_student" app tests
```

练习 3：回答下面的问题：

```text
如果要支持多个学员，当前 student.json 会遇到什么问题？
```

练习 4：设计一个未来的数据库表，不需要写代码，只写字段：

```text
students
notes
```

例如：

```text
students: id, name, goal, python_level
notes: id, student_id, content, created_at
```

练习 5：判断下面哪些场景需要数据库：

| 场景 | 是否需要数据库 |
| --- | --- |
| 单人本地学习 | 不一定 |
| 多用户网页登录 | 需要 |
| 笔记按关键词搜索 | 倾向需要 |
| 学习笔记只有 3 条 | 不一定 |
| 部署到正式服务端并长期保存数据 | 需要 |

## 9. 验收标准

本课完成时，你应该能做到：

- 解释当前为什么使用 JSON。
- 解释 JSON 和数据库的区别。
- 说出 JSON 存储的至少 4 个限制。
- 说出什么时候应该迁移 SQLite。
- 说出什么时候应该迁移 PostgreSQL。
- 指出当前存储边界是 `storage.py`。
- 指出 API 不应该直接操作 JSON 或 SQL。
- 理解后续迁移数据库前要先保护测试。
- 知道本课不新增 API、不改运行逻辑、不引入数据库依赖。
- `py -3.13 -m pytest` 通过。
- `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

存储边界会影响后续所有 Agent 能力。

| 现在 | 后续升级 |
| --- | --- |
| `storage.py` | Repository / database layer |
| `student.json` | SQLite / PostgreSQL |
| `load_student()` | LangChain 工具读取资料 |
| `save_student()` | Agent 写入学习记录 |
| JSON 文件 | LangGraph checkpoint 的前置理解 |
| 本地笔记 | RAG 资料来源之一 |

到了 LangChain 阶段，工具不应该到处直接读文件。

它应该调用稳定函数或 repository。

到了 RAG 阶段，本地资料、笔记和索引会变多。

你会开始关心：

```text
资料存在哪里？
向量索引存在哪里？
metadata 存在哪里？
```

到了 LangGraph 阶段，checkpoint 也是一种持久化。

你现在理解 JSON 文件的边界，以后理解 checkpoint 数据库会轻松很多。

到了 Deep Agents 阶段，文件系统能力和长期任务输出会让“哪些内容是文件、哪些内容是数据库记录”变得更重要。

本课就是先把这个边界讲清楚。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-3/03-07-storage-boundary-database-preview.md`

修改文件：

- `README.md`
- `ai-learning-assistant/README.md`
- `docs/tutorial/README.md`

代码变更：

- 无。

新增依赖：

- 无。

验证命令：

在 `ai-learning-assistant/` 下运行：

```powershell
py -3.13 -m pytest
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_suggestions.py
```

验证结果：

- 本课不改变运行逻辑。
- 现有 API 和存储测试应继续通过。
- 当前阶段仍然使用 JSON 存储。
- 数据库迁移保留到后续专门课程。

下一步：

- 先记录阶段 3 的补充笔记。
- 等补充笔记完成并确认后，再生成阶段 3 复盘。
- 阶段 3 复盘完成后，再进入阶段 4：LLM 基础。
