# 第 6.2 课：本地资料加载

## 1. 本课目标

第 6.1 课已经确定 RAG 的第一段数据流：资料不能只是一堆散落的 Markdown 文件，而要成为能够保留内容与来源的 `Document`。

这一课让项目真正读取顶层 `materials/*.md`，并把每一份文件转换为 LangChain `Document`：

```text
materials/stage-2.md
-> Document(
       page_content="资料原文",
       metadata={"source": "materials/stage-2.md"},
   )
```

完成后，应能解释：

- 为什么 RAG 资料加载不能只返回 `list[str]`。
- 为什么来源路径要在加载时保存到 `metadata`。
- 为什么文件遍历顺序必须稳定。
- 为什么这一层不应该提前处理 chunk、embedding、向量库或模型回答。

## 2. 你会新增什么项目能力

项目新增一个可复用的本地资料加载器：

```text
app/rag.py
└── load_local_materials()
    └── materials/*.md -> list[Document]
```

它的行为边界是：

| 输入状态 | 结果 |
| --- | --- |
| 顶层 Markdown 文件 | 返回按文件名排序的 `Document` 列表 |
| 非 Markdown 文件 | 忽略 |
| 空资料目录 | 返回空列表 |
| 资料目录不存在 | 抛出 `FileNotFoundError` |
| 传入的是文件而不是目录 | 抛出 `NotADirectoryError` |

每个 `Document` 只保存两类信息：

```text
page_content       Markdown 原始内容
metadata["source"] 相对来源路径，例如 materials/stage-5.md
```

还没有新增：

- 文档切分或 overlap。
- embedding、向量库、retriever 或 reranker。
- LangChain Agent 的 RAG 工具。
- `POST /ask-materials`。
- provider、API Key 或新的 `requirements.txt` 依赖。

## 3. 前置知识

开始前，应已理解：

- RAG 的最小数据流以及来源引用的价值。
- `Path` 的目录遍历和 UTF-8 文本读取。
- 现有项目使用 `pytest` 和 `tmp_path` 为文件逻辑创建隔离样例。
- 阶段 5 的 Agent 已能调用只读工具，但尚未读取 Markdown 资料。

还不需要：

- 使用 `RecursiveCharacterTextSplitter` 切分文档。
- 配置 embedding 模型或外部向量数据库。
- 调用真实 provider。
- 让 API 返回资料问答结果。

## 4. 核心概念

### `Document` 是内容和元数据的组合

LangChain `Document` 用于 retrieval workflow，不是聊天消息。它把文本放在 `page_content`，把来源、标题或其他描述信息放在 `metadata`。

```python
from langchain_core.documents import Document

document = Document(
    page_content="Python 类型标注可以说明参数和返回值的预期类型。",
    metadata={"source": "materials/python_basics.md"},
)
```

后面的切分器会从 `Document` 生成 chunk，检索器会返回相关 chunk。来源元数据在最开始就存在，才能自然传递到回答与引用层。

### 为什么 `source` 使用相对路径

绝对路径会把机器用户名和本地目录泄露到 API 或日志中，也无法在另一台机器上稳定复现。加载器以 `materials/` 的父目录作为相对根：

```text
E:/Code/study/ai-learning-assistant/materials/stage-5.md
-> materials/stage-5.md
```

这让测试、CLI、未来 API 和资料引用使用相同的值。来源不是展示文案，也不能在回答结束时临时猜测文件名。

### 稳定顺序是可测试性的前提

文件系统遍历的顺序不应成为业务契约。加载器使用不区分大小写的文件名排序，因此：

```text
a.md
B.MD
z.md
```

总是得到相同的 `Document` 顺序。现在的顺序方便测试；后续检索阶段仍会按相关性排序，而不是按文件加载顺序回答。

### 为什么这里手写 Markdown loader

LangChain 提供不同格式的 Document loader 集成。当前项目只需要读取少量、受控且 UTF-8 编码的顶层 Markdown，使用 `Path.read_text()` 和 `Document` 能让数据路径完全透明，也不需要新增社区 integration 依赖。

PDF、网页、递归目录、编码探测和云端数据源属于不同问题。需要这些格式时，再依据官方集成文档选择对应 loader，不能把所有输入场景提前塞进这个函数。

### 加载、切分和检索的边界

```text
6.2 读取文件 -> Document + source
6.3 Document -> chunk
6.4 chunk + embedding -> retriever
6.5 retriever -> answer + sources
6.6 HTTP request -> RAG response
```

`load_local_materials()` 只负责第一行。它不决定 chunk size，不调用模型，也不修改资料文件。这样后续每一层都有独立测试和错误边界。

## 5. 代码实现

新增 `app/rag.py`：

```python
from pathlib import Path

from langchain_core.documents import Document


MATERIALS_DIR = Path(__file__).resolve().parent.parent / "materials"


def load_local_materials(materials_dir: Path = MATERIALS_DIR) -> list[Document]:
    if not materials_dir.exists():
        raise FileNotFoundError(f"Materials directory does not exist: {materials_dir}")
    if not materials_dir.is_dir():
        raise NotADirectoryError(f"Materials path is not a directory: {materials_dir}")

    material_paths = sorted(
        (
            path
            for path in materials_dir.iterdir()
            if path.is_file() and path.suffix.lower() == ".md"
        ),
        key=lambda path: path.name.lower(),
    )

    return [
        Document(
            page_content=material_path.read_text(encoding="utf-8"),
            metadata={
                "source": material_path.relative_to(materials_dir.parent).as_posix(),
            },
        )
        for material_path in material_paths
    ]
```

`materials_dir` 是可注入参数，因此测试不需要读真实课程资料：

```python
def test_load_local_materials_returns_sorted_documents_with_sources(tmp_path: Path) -> None:
    materials_dir = tmp_path / "materials"
    materials_dir.mkdir()
    (materials_dir / "z.md").write_text("Zebra material", encoding="utf-8")
    (materials_dir / "a.md").write_text("Alpha material", encoding="utf-8")

    documents = load_local_materials(materials_dir)

    assert [document.metadata for document in documents] == [
        {"source": "materials/a.md"},
        {"source": "materials/z.md"},
    ]
```

本次不修改：

```text
requirements.txt
.env.example
app/langchain_agent.py
app/api.py
app/models.py
app/cli.py
```

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

运行本课测试：

```powershell
py -3.13 -m pytest tests/test_rag.py
```

查看真实资料的来源列表：

```powershell
py -3.13 -c "from app.rag import load_local_materials; print([document.metadata['source'] for document in load_local_materials()])"
```

运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

无需配置 `.env` 或真实 provider。

## 7. 常见错误

### 只返回字符串列表

`list[str]` 只能保存文本。切分、检索和回答阶段还需要知道片段来自哪里，因此加载阶段就应返回 `Document` 与 `metadata["source"]`。

### 使用绝对路径作为来源

绝对路径会随开发机器变化，还可能暴露本地目录。来源应是可展示、可测试的相对路径。

### 依赖 `iterdir()` 的默认顺序

默认顺序不是稳定契约。排序后，测试和后续调试才能稳定复现资料集合。

### 把 `.txt`、隐藏文件或子目录都当作 Markdown

当前约定是顶层 `materials/*.md`。扩大格式和目录范围前，要先定义解析、编码、来源和错误策略。

### 在 loader 中切分或生成 embedding

加载器的输出是完整 `Document`。把后续职责塞进来会让 chunk 测试、metadata 传递和错误定位难以拆开。

### 把缺失目录静默当成空资料库

空目录是合法状态，缺失目录通常是部署或路径配置错误。两者需要不同结果，调用方才能准确排障。

## 8. 练习

练习 1：为 `materials/python.md` 写出加载后的 `page_content` 与 `metadata` 形状。

练习 2：解释为什么 `materials/a.md` 和 `materials/z.md` 必须在任意机器上以相同顺序返回。

练习 3：给 `load_local_materials()` 增加递归目录支持前，需要先补充哪些来源路径和文件格式规则？不要直接修改代码。

练习 4：说明“资料目录为空”和“资料目录不存在”为什么不是同一种情况。

练习 5：判断以下需求分别属于哪个小节：

```text
A. 按 800 字符和 120 overlap 切分 Document。
B. 为每个 chunk 生成向量并找最相关的三个片段。
C. 将检索片段与问题交给模型，并返回来源。
```

## 9. 验收标准

完成后，应能做到：

- 使用 `load_local_materials()` 读取顶层 Markdown 文件。
- 得到 `list[Document]`，每个 `Document` 都包含原始内容与 `metadata["source"]`。
- 解释为什么来源使用相对路径、为什么文件按名称排序。
- 说明非 Markdown 文件不会加载，空目录返回空列表。
- 区分缺失目录和空目录的错误边界。
- 说明当前仍未实现 chunk、embedding、检索、回答或 API。
- 运行 `py -3.13 -m pytest tests/test_rag.py` 通过。
- 运行完整 `pytest` 和 `py_compile` 通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| `Document.page_content` | 6.3：切分为 chunk |
| `Document.metadata["source"]` | 6.3 到 6.5：随 chunk 保留并作为回答来源 |
| 稳定的资料集合 | 6.4：建立 embedding 与 retriever |
| 文件读取异常 | 6.6：转换为 RAG API 的明确错误响应 |
| retriever | 后续可以作为 LangChain Agent 的只读工具 |
| 有状态学习流程 | Stage 7：LangGraph State、node 和 edge |
| 长任务规划与文件输出 | Stage 9：Deep Agents |

项目仍然只有一条真实代码主线：

```text
ai-learning-assistant/
```

没有为课程创建代码副本。

## 11. 本课变更清单

新增文件：

- `ai-learning-assistant/app/rag.py`
- `ai-learning-assistant/tests/test_rag.py`
- `docs/tutorial/lessons/stage-6/06-02-local-material-loading.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- 新增 `load_local_materials()`，加载顶层 Markdown 为带来源元数据的 `Document`。
- 新增排序、文件类型过滤、空目录、缺失目录和非目录路径的测试。

新增依赖：无。`Document` 来自已有 `langchain` 依赖安装的 `langchain-core`。

环境变量变更：无。

官方文档核对：

- [LangChain Retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [LangChain Document loader integrations](https://docs.langchain.com/oss/python/integrations/document_loaders)

下一步：第 6.3 课，按 `chunk size` 和 `overlap` 切分 `Document`。
