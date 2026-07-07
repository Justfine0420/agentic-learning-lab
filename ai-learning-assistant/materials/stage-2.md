# Stage 2 补充学习资料：模块导入与 JSON 文件保存

本文记录 Stage 2 中围绕模块拆分、学生状态保存、JSON 文件读写补充出来的 Python 基础知识点：

- `from app.student_state import student` 为什么不写文件路径
- `__all__` 的作用
- PyCharm 为什么会提示“未解析的引用 app”
- `DATA_FILE = Path("data/student.json")` 的含义
- `DATA_FILE.exists()`、`Path.open()`、`json.dump()` 等常见用法
- 为什么 `storage.py` 不应该直接调用 `input()`
- `isinstance()`、`all()`、列表推导式、变量名作用域
- `try / except` 异常处理
- `backup_broken_data()` 与坏 JSON 文件隔离

## 目录

- [1. Python 导入的是模块路径，不是文件路径](#1-python-导入的是模块路径不是文件路径)
- [2. Python 不需要 export 语法](#2-python-不需要-export-语法)
- [3. `__all__` 是什么](#3-__all__-是什么)
- [4. PyCharm 中“未解析的引用 app”的原因](#4-pycharm-中未解析的引用-app的原因)
- [5. `DATA_FILE` 是什么](#5-data_file-是什么)
- [6. `DATA_FILE.exists()` 的作用](#6-data_fileexists-的作用)
- [7. `DATA_FILE.parent.mkdir(...)` 的作用](#7-data_fileparentmkdir-的作用)
- [8. `DATA_FILE.open(...)` 的作用](#8-data_fileopen-的作用)
- [9. `json.load()` 与 `json.dump()`](#9-jsonload-与-jsondump)
- [10. `dump`、`dumps`、`load`、`loads` 的区别](#10-dumpdumpsloadloads-的区别)
- [11. 为什么 `storage.py` 不应该直接调用 `input()`](#11-为什么-storagepy-不应该直接调用-input)
- [12. `isinstance()` 的用法](#12-isinstance-的用法)
- [13. `all()` 的用法](#13-all-的用法)
- [14. 列表推导式：`[note for note in data["notes"] if ...]`](#14-列表推导式note-for-note-in-datanotes-if-)
- [15. 变量名可以相同的场景](#15-变量名可以相同的场景)
- [16. `try / except` 是什么](#16-try--except-是什么)
- [17. `backup_broken_data()` 是什么样的备份](#17-backup_broken_data-是什么样的备份)
- [18. pytest 测试中的 `assert`、`tmp_path` 和 `write_text()`](#18-pytest-测试中的-asserttmp_path-和-write_text)
- [19. 当前项目中的完整数据流](#19-当前项目中的完整数据流)

## 1. Python 导入的是模块路径，不是文件路径

项目中有这样的代码：

```python
from app.student_state import student
```

它不是在写系统文件路径，而是在写 Python 的模块路径。

对应的文件结构是：

```text
ai-learning-assistant/
  app/
    __init__.py
    student_state.py
    cli.py
    main.py
```

这句代码的意思是：

```text
从 app 这个包里
找到 student_state.py 这个模块
导入里面名为 student 的变量
```

也就是：

```python
from app.student_state import student
```

对应：

```text
app/student_state.py 里的 student
```

`app` 能被当成包，是因为 `app` 目录下有 `__init__.py` 文件。

## 2. Python 不需要 export 语法

JavaScript / TypeScript 中经常会写：

```javascript
export const student = {}
```

Python 里没有这种 `export` 语法。

在 Python 中，只要一个变量、函数、类定义在模块顶层，外部就可以导入它。

例如：

```python
# app/student_state.py

student = {}
teacher = {}

def teach():
    print("teaching")


class Student:
    pass
```

外部可以明确导入：

```python
from app.student_state import student
from app.student_state import teacher
from app.student_state import teach
from app.student_state import Student
```

也可以先导入整个模块：

```python
import app.student_state as state

print(state.student)
state.teach()
```

## 3. `__all__` 是什么

如果想显式声明一个模块“推荐公开”的名字，可以在文件顶层写：

```python
# app/student_state.py

student = {}
teacher = {}

def teach():
    print("teaching")


__all__ = ["student"]
```

这表示：

```text
当别人使用 from app.student_state import * 时，只导入 student。
```

例如：

```python
from app.student_state import *
```

如果有：

```python
__all__ = ["student"]
```

那么 `import *` 只会导入 `student`，不会自动导入 `teacher` 和 `teach`。

但要注意：`__all__` 不是权限控制。

即使写了：

```python
__all__ = ["student"]
```

外部仍然可以明确导入：

```python
from app.student_state import teacher
from app.student_state import teach
```

所以可以这样理解：

```text
__all__ 只影响 from xxx import *。
它不是 private/export 限制。
```

## 4. PyCharm 中“未解析的引用 app”的原因

如果 PyCharm 中这句报错：

```python
from app.student_state import student
```

提示：

```text
未解析的引用 'app'
```

常见原因是 PyCharm 没有把正确的目录当成源码根目录。

当前仓库结构大致是：

```text
<workspace-root>/
  ai-learning-assistant/
    app/
      main.py
      cli.py
      student_state.py
      storage.py
```

`app` 实际在：

```text
ai-learning-assistant/app
```

所以应该把这个目录设置为源码根：

```text
ai-learning-assistant
```

在 PyCharm 中可以这样操作：

```text
右键 ai-learning-assistant
-> Mark Directory as
-> Sources Root
```

运行配置建议使用模块运行方式：

```text
Run -> Edit Configurations...
```

配置：

```text
Name: main
Module name: app.main
Working directory: <workspace-root>/ai-learning-assistant
```

它等价于在终端中运行：

```powershell
cd <workspace-root>/ai-learning-assistant
py -m app.main
```

## 5. `DATA_FILE` 是什么

项目中的 `app/storage.py` 里有：

```python
from pathlib import Path


DATA_FILE = Path("data/student.json")
```

`DATA_FILE` 不是 Python 内置关键字，它只是一个普通变量名。

它保存的是一个路径对象：

```text
data/student.json
```

`Path("data/student.json")` 来自 `pathlib` 模块，用来更方便地处理文件路径。

和直接写字符串相比：

```python
"data/student.json"
```

`Path` 对象可以直接调用很多路径相关方法，例如：

```python
DATA_FILE.exists()
DATA_FILE.parent
DATA_FILE.open("r", encoding="utf-8")
```

## 6. `DATA_FILE.exists()` 的作用

```python
DATA_FILE.exists()
```

表示：

```text
判断 DATA_FILE 这个路径是否存在。
```

它返回布尔值：

```python
True
False
```

项目中的代码：

```python
def load_student() -> dict:
    if not DATA_FILE.exists():
        return create_default_student()

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)
```

意思是：

```text
如果 data/student.json 不存在，就返回一个默认学生数据。
如果文件存在，就打开文件并读取 JSON 内容。
```

注意：

```python
DATA_FILE.exists()
```

后面有括号，因为 `exists` 是方法，不是普通属性。

另外还有两个常见判断：

```python
DATA_FILE.is_file()
```

判断路径是不是文件。

```python
DATA_FILE.is_dir()
```

判断路径是不是目录。

## 7. `DATA_FILE.parent.mkdir(...)` 的作用

项目中保存数据前有：

```python
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
```

拆开看：

```python
DATA_FILE
```

表示：

```text
data/student.json
```

```python
DATA_FILE.parent
```

表示父目录：

```text
data
```

```python
mkdir(...)
```

表示创建目录。

所以这句完整意思是：

```text
在保存 student.json 之前，先确保 data 目录存在。
```

参数含义：

```python
parents=True
```

如果中间目录不存在，也一起创建。

```python
exist_ok=True
```

如果目录已经存在，不要报错。

## 8. `DATA_FILE.open(...)` 的作用

`open()` 用来打开文件。项目中主要用到两种模式：

```python
with DATA_FILE.open("r", encoding="utf-8") as file:
    return json.load(file)
```

这里的 `"r"` 表示 read，读取文件。

```python
with DATA_FILE.open("w", encoding="utf-8") as file:
    json.dump(student, file, ensure_ascii=False, indent=2)
```

这里的 `"w"` 表示 write，写入文件。文件不存在时会创建；文件已存在时会覆盖原内容。

```python
"a"
```

`"a"` 表示 append，追加写入。当前项目暂时没有用到。

初学阶段先记住：

```text
"r" = read，读文件
"w" = write，写文件
```

`encoding="utf-8"` 表示用 UTF-8 编码读写文本。保存中文内容时应该保留这个参数。

`with ... as file:` 是上下文管理写法。它的好处是：代码块结束后，文件会自动关闭。

## 9. `json.load()` 与 `json.dump()`

项目中读取 JSON：

```python
json.load(file)
```

表示：

```text
从文件对象中读取 JSON，并转换为 Python 数据。
```

例如 JSON 文件内容是：

```json
{
  "name": "张三",
  "goal": "学习 Python",
  "notes": ["今天学习了 JSON"]
}
```

读取后会变成 Python 字典：

```python
{
    "name": "张三",
    "goal": "学习 Python",
    "notes": ["今天学习了 JSON"],
}
```

项目中写入 JSON：

```python
json.dump(student, file, ensure_ascii=False, indent=2)
```

表示：

```text
把 Python 数据 student 写入 file 对应的 JSON 文件。
```

参数解释：

```python
student
```

要保存的数据，通常是字典或列表。

也可以叫成更通用的名字：

```python
json.dump(data, file)
```

这里的 `data` 就表示要转换成 JSON 的 Python 数据。

```python
file
```

已经打开的文件对象。

```python
ensure_ascii=False
```

保存中文原文。

如果不写这个参数，中文可能会被保存成：

```json
"\u5f20\u4e09"
```

如果写了：

```python
ensure_ascii=False
```

中文会保存成：

```json
"张三"
```

```python
indent=2
```

表示用 2 个空格缩进，让 JSON 文件更容易阅读。

保存效果类似：

```json
{
  "name": "张三",
  "goal": "学习 Python",
  "python_level": "beginner",
  "notes": [
    "今天学习了 JSON"
  ]
}
```

## 10. `dump`、`dumps`、`load`、`loads` 的区别

这四个名字很像，但作用不同。

```python
json.dump(data, file)
```

把 Python 数据写入 JSON 文件。

```python
json.dumps(data)
```

把 Python 数据转换成 JSON 字符串。

例如测试中有：

```python
json.dumps(
    {
        "name": "Carol",
        "notes": ["Only partial data", 123],
    },
    ensure_ascii=False,
)
```

它不会直接写入文件，而是返回一个字符串：

```json
{"name": "Carol", "notes": ["Only partial data", 123]}
```

所以测试里会把它交给 `write_text()`：

```python
storage.DATA_FILE.write_text(
    json.dumps(
        {
            "name": "Carol",
            "notes": ["Only partial data", 123],
        },
        ensure_ascii=False,
    ),
    encoding="utf-8",
)
```

这段可以拆成两步理解：

```python
text = json.dumps(
    {
        "name": "Carol",
        "notes": ["Only partial data", 123],
    },
    ensure_ascii=False,
)

storage.DATA_FILE.write_text(text, encoding="utf-8")
```

```python
json.load(file)
```

从 JSON 文件读取数据，转换成 Python 数据。

```python
json.loads(text)
```

从 JSON 字符串读取数据，转换成 Python 数据。

可以这样记：

```text
带 s 的 dumps / loads 处理 string。
不带 s 的 dump / load 处理 file。
```

## 11. 为什么 `storage.py` 不应该直接调用 `input()`

当前项目把代码拆成了几个模块：

```text
app/cli.py            负责 input() / print()，和用户交互
app/storage.py        负责 load_student() / save_student()，读写 JSON 文件
app/student_state.py  负责保存当前内存中的 student 状态
```

所以 `storage.py` 不应该直接写：

```python
name = input("请输入姓名：")
```

原因是：`input()` 属于用户交互层，`json.load()` / `json.dump()` 属于数据存储层。

如果 `storage.py` 直接调用 `input()`，它就不只是“存储模块”了，而变成了：

```text
存储 + 命令行交互
```

这样会带来几个问题：

```text
1. 复用性变差
   以后如果换成网页、API、桌面程序，storage.py 仍然会强行等待命令行输入。

2. 测试变麻烦
   测试 save_student() 时，本来只需要传一个 dict。
   如果函数内部有 input()，测试会卡住等待人工输入。

3. 职责混乱
   storage.py 应该只关心文件是否存在、JSON 怎么读、JSON 怎么写。
   它不应该关心菜单怎么展示、提示语怎么写、用户输入什么。
```

更好的写法是：

```python
# app/cli.py

student["name"] = input("请输入你的名字：")
save_student(student)
```

而不是：

```python
# app/storage.py

def save_student() -> None:
    name = input("请输入你的名字：")
    ...
```

可以这样记：

```text
cli.py 负责问用户。
storage.py 负责保存数据。
```

## 12. `isinstance()` 的用法

`isinstance()` 用来判断一个值是不是某种类型。

```python
isinstance("abc", str)
```

结果是：

```python
True
```

例子：

```python
name = "张三"
age = 18
notes = ["学习 JSON"]

print(isinstance(name, str))    # True
print(isinstance(age, int))     # True
print(isinstance(notes, list))  # True
```

也可以一次判断多个类型：

```python
value = 18

isinstance(value, (int, float))
```

意思是：

```text
value 是不是 int 或 float。
```

当前项目中用它校验 JSON 读取出来的数据：

```python
if not isinstance(data, dict):
    return False
```

意思是：

```text
如果 data 不是字典，就不是合法的 student 数据。
```

## 13. `all()` 的用法

`all()` 用来判断一组条件是否全部成立。

```python
all([True, True, True])
```

结果是：

```python
True
```

只要里面有一个是 `False`，整体就是 `False`。

例子：

```python
scores = [80, 90, 100]

all(score >= 60 for score in scores)
```

意思是：

```text
所有分数是否都大于等于 60。
```

当前项目中有：

```python
required_keys = ("name", "goal", "python_level", "notes")

if not all(key in data for key in required_keys):
    return False
```

这句的意思是：

```text
required_keys 里的每一个 key，都必须存在于 data 里。
```

也就是检查 `data` 是否至少包含：

```text
name
goal
python_level
notes
```

## 14. 列表推导式：`[note for note in data["notes"] if ...]`

当前项目中有：

```python
student["notes"] = [note for note in data["notes"] if isinstance(note, str)]
```

这叫列表推导式。

结构是：

```python
[要放进新列表的值 for 临时变量 in 原列表 if 条件]
```

对应到这句：

```python
[
    note                         # 要放进新列表的值
    for note in data["notes"]     # 从 data["notes"] 中逐个取出，临时叫 note
    if isinstance(note, str)      # 只保留字符串
]
```

它等价于：

```python
valid_notes = []

for note in data["notes"]:
    if isinstance(note, str):
        valid_notes.append(note)

student["notes"] = valid_notes
```

所以两个 `note` 的写法是对的。它们不是两个来源的变量，而是同一个临时变量。

举例：

```python
data = {
    "notes": ["学习 JSON", 123, "学习 Path", None]
}

valid_notes = [note for note in data["notes"] if isinstance(note, str)]
```

结果是：

```python
["学习 JSON", "学习 Path"]
```

也可以换成其他变量名：

```python
[item for item in data["notes"] if isinstance(item, str)]
```

但这里处理的是笔记，所以叫 `note` 更清楚。

## 15. 变量名可以相同的场景

变量名能不能相同，关键看作用域。

可以先记一句：

```text
同一个作用域里，同名变量通常就是同一个变量，会被覆盖或复用。
不同作用域里，可以有同名变量，互不影响。
```

常见例子：

```python
def add_note():
    note = input("请输入笔记：")


def show_note():
    note = "默认笔记"
```

这两个 `note` 在不同函数里，互不影响。

字典 key 和变量名也不是一回事：

```python
name = "张三"
student = {"name": "李四"}
```

这里的变量 `name` 和字典 key `"name"` 没有直接关系。

但不要覆盖 Python 内置名字：

```python
list = [1, 2, 3]
input = "hello"
```

因为 `list`、`input` 原本是 Python 内置名字，覆盖后后面容易出问题。

## 16. `try / except` 是什么

Python 里的异常处理写法是：

```python
try:
    # 尝试执行这里的代码
except 某种错误:
    # 如果发生这种错误，就执行这里
```

它对应很多语言里的 `try / catch`。

Python 不叫 `catch`，叫 `except`。

当前项目中有：

```python
try:
    with DATA_FILE.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
except json.JSONDecodeError:
    backup_broken_data()
    return create_default_student()
except OSError:
    return create_default_student()
```

意思是：

```text
尝试打开 data/student.json。
尝试把文件内容按 JSON 读取出来。
```

如果 JSON 内容坏了，例如文件不是合法 JSON：

```python
except json.JSONDecodeError:
```

就执行：

```python
backup_broken_data()
return create_default_student()
```

也就是：

```text
先把坏 JSON 文件隔离起来，再返回默认 student 数据。
```

如果是文件系统错误，例如权限问题、文件打不开：

```python
except OSError:
```

就执行：

```python
return create_default_student()
```

另外这里用的是：

```python
encoding="utf-8-sig"
```

它表示用 UTF-8 读取，并且如果文件开头有 BOM 标记，会自动处理掉。

## 17. `backup_broken_data()` 是什么样的备份

当前项目中有：

```python
BROKEN_DATA_FILE = Path("data/student.broken.json")


def backup_broken_data() -> None:
    if DATA_FILE.exists():
        DATA_FILE.replace(BROKEN_DATA_FILE)
```

这里的 `replace()` 不是复制，而是移动/改名。

它的效果类似：

```text
data/student.json
-> data/student.broken.json
```

所以它更准确地说是：

```text
把坏掉的 student.json 挪到 student.broken.json。
```

这样做的目的不是保留多个历史版本，而是：

```text
让坏掉的 JSON 文件不要继续阻塞程序启动。
```

当前流程是：

```text
1. load_student() 读取 data/student.json
2. 发现 JSON 格式损坏
3. backup_broken_data() 把 student.json 改名为 student.broken.json
4. load_student() 返回默认 student 数据
5. 后续 save_student() 会重新生成新的 data/student.json
```

需要注意：

```python
DATA_FILE.replace(BROKEN_DATA_FILE)
```

如果 `data/student.broken.json` 已经存在，会被新的坏文件覆盖。

所以当前策略是：

```text
单份覆盖式备份 / 改名隔离
```

当前阶段先理解现有逻辑即可：

```text
坏 JSON 文件被挪走，程序用默认数据继续运行。
```

## 18. pytest 测试中的 `assert`、`tmp_path` 和 `write_text()`

Stage 2 中已经开始为 `storage.py` 写测试。

测试文件大致是：

```text
tests/test_storage.py
```

测试函数名通常以 `test_` 开头：

```python
def test_load_student_returns_default_when_file_missing(tmp_path: Path) -> None:
    ...
```

这样 pytest 才会自动识别并运行它。

### `assert` 是什么

`assert` 是断言。

它的意思是：

```text
我认为这个条件必须成立。
如果不成立，测试就失败。
```

例如：

```python
assert storage.load_student() == storage.create_default_student()
```

意思是：

```text
我断定 load_student() 的结果应该等于默认 student 数据。
```

如果左右两边不相等，pytest 会把这条测试标记为失败。

### 为什么 `tmp_path` 不能随便改成 `temp_path`

测试中常见：

```python
def test_load_student_backs_up_broken_json(tmp_path: Path) -> None:
    ...
```

这里的 `tmp_path` 是 pytest 内置 fixture。

可以理解为：

```text
pytest 看到测试函数需要 tmp_path，就自动创建一个临时目录 Path 对象传进来。
```

所以这个名字不能随便改。

如果写成：

```python
def test_normal_notes_is_null(temp_path: Path) -> None:
    ...
```

pytest 会去找一个叫 `temp_path` 的 fixture。

但 pytest 默认没有这个 fixture，于是会报：

```text
fixture 'temp_path' not found
```

注意：

```python
temp_path: Path
```

里的 `Path` 只是类型提示，不会告诉 pytest 自动创建变量。

如果你想在函数内部使用 `temp_path` 这个名字，可以这样写：

```python
def test_normal_notes_is_null(tmp_path: Path) -> None:
    temp_path = tmp_path
    use_tmp_storage(temp_path)
```

### `use_tmp_storage(tmp_path)` 的作用

当前测试里有：

```python
def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"
```

它的作用是：

```text
让测试使用 pytest 创建的临时目录，而不是项目真实的 data 目录。
```

这样测试不会污染真实文件：

```text
data/student.json
data/student.broken.json
```

测试结束后，pytest 会处理临时目录。

### `Path.write_text()` 的作用

测试中有：

```python
storage.DATA_FILE.write_text("{ bad json", encoding="utf-8")
```

这里的 `write_text()` 来自 `pathlib.Path`。

它的意思是：

```text
把字符串写入 DATA_FILE 指向的文件。
如果文件不存在，就创建。
如果文件已经存在，就覆盖。
写完后自动关闭文件。
```

它大致等价于：

```python
with storage.DATA_FILE.open("w", encoding="utf-8") as file:
    file.write("{ bad json")
```

### 为什么坏 JSON 测试里的断言会成立

测试代码：

```python
def test_load_student_backs_up_broken_json(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.DATA_FILE.write_text("{ bad json", encoding="utf-8")

    assert storage.load_student() == storage.create_default_student()
    assert not storage.DATA_FILE.exists()
    assert storage.BROKEN_DATA_FILE.exists()
    assert storage.BROKEN_DATA_FILE.read_text(encoding="utf-8") == "{ bad json"
```

执行顺序是：

```text
1. use_tmp_storage(tmp_path) 把 DATA_FILE 指到临时目录
2. write_text("{ bad json") 写入一个坏 JSON 文件
3. load_student() 尝试 json.load(file)
4. json.load(file) 发现格式错误，抛出 JSONDecodeError
5. except json.JSONDecodeError 捕获错误
6. backup_broken_data() 把 student.json 改名为 student.broken.json
7. load_student() 返回 create_default_student()
```

所以这个断言成立：

```python
assert storage.load_student() == storage.create_default_student()
```

因为坏 JSON 场景下，`load_student()` 明确会返回默认 student。

后面几个断言是在检查副作用：

```python
assert not storage.DATA_FILE.exists()
```

坏的 `student.json` 已经被挪走，所以原路径不存在。

```python
assert storage.BROKEN_DATA_FILE.exists()
```

坏文件被改名成了 `student.broken.json`。

```python
assert storage.BROKEN_DATA_FILE.read_text(encoding="utf-8") == "{ bad json"
```

确认备份文件里保留了原来的坏内容。

## 19. 当前项目中的完整数据流

当前 `app/storage.py` 里不只是简单读写 JSON，还做了默认数据创建、结构校验、结构修复和坏文件隔离。

核心函数关系是：

```text
create_default_student()
    创建一个新的默认 student 字典

is_valid_student(data)
    判断 JSON 读出来的数据是否是合法 student 结构

normalize_student(data)
    尝试从不完整的数据中修复出可用 student

backup_broken_data()
    JSON 文件格式坏掉时，把坏文件挪到 student.broken.json

load_student()
    启动时加载 student 数据

save_student(student)
    用户修改数据后保存到 JSON 文件
```

当前读取流程：

```text
程序启动
-> run_cli()
-> replace_student(load_student())
-> load_student() 检查 data/student.json 是否存在
-> 不存在：返回默认 student
-> 存在：尝试打开并 json.load(file)
-> JSON 格式损坏：挪到 data/student.broken.json，返回默认 student
-> 文件读取异常：返回默认 student
-> JSON 读取成功：检查 is_valid_student(data)
-> 完全合法：直接返回 data
-> 不完整或类型不完全正确：normalize_student(data) 后返回
```

当前保存流程：

```text
用户输入学习档案
-> cli.py 修改内存里的 student 字典
-> save_student(student)
-> 确保 data 目录存在
-> 用 "w" 模式打开 data/student.json
-> json.dump(student, file, ensure_ascii=False, indent=2)
-> 最新学习档案被写入 JSON 文件
```

从职责上看：

```text
cli.py
    负责 input() / print() / 菜单流程

student_state.py
    负责当前运行中的 student 状态

storage.py
    负责 JSON 文件读写、默认值、校验、修复、坏文件隔离
```

这个阶段的核心目标是：

```text
让程序的数据从“只存在于内存中”，变成“可以保存到本地文件中”，并且在文件缺失、文件损坏、数据结构不完整时仍然能继续运行。
```
