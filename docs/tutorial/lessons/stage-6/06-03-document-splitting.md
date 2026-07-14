# 第 6.3 课：文档切分

## 1. 本课目标

第 6.2 课已经把顶层 Markdown 加载为带来源元数据的完整 `Document`。完整资料往往很长，不能直接作为一次检索或一次模型调用的最小单位。

这一课用 `RecursiveCharacterTextSplitter` 把 `Document` 拆成相互重叠的 chunk：

```text
完整 Document
-> chunk 1
-> chunk 2（保留前一块尾部的一部分上下文）
-> chunk 3
```

完成后，应能解释：

- `chunk_size` 和 `chunk_overlap` 各自控制什么。
- 为什么 overlap 能减少边界处的上下文断裂。
- 为什么 chunk 数量不等于检索结果数量。
- 为什么每个 chunk 必须继承原 `Document` 的 `source`。

## 2. 你会新增什么项目能力

`app/rag.py` 新增：

```text
split_material_documents(
    documents,
    chunk_size=800,
    chunk_overlap=120,
) -> list[Document]
```

数据流变为：

```text
materials/*.md
-> load_local_materials()
-> 完整 Document + source
-> split_material_documents()
-> chunk Document + source
```

函数保证：

- 使用 `RecursiveCharacterTextSplitter` 切分文本。
- chunk 保留原有全部 `metadata`，包括 `source`。
- `chunk_size` 必须大于 0。
- `chunk_overlap` 不能为负数，且必须小于 `chunk_size`。
- 空文档列表返回空列表。

仍未新增：

- embedding 模型或向量数据库。
- retriever、相似度搜索或 reranker。
- 根据 chunk 生成答案。
- RAG API、Agent RAG 工具、LangGraph State 或 streaming。

## 3. 前置知识

开始前，应已理解：

- `load_local_materials()` 如何返回带 `source` 的 `Document`。
- `Document.page_content` 与 `Document.metadata` 的职责。
- RAG 中完整资料、chunk、embedding 和 retriever 的先后关系。
- `pytest` 如何对纯函数的输入、输出和异常做断言。

还不需要：

- 配置真实 embedding provider。
- 决定向量库、top-k 或相似度阈值。
- 提示模型引用资料。
- 建模多步骤学习流程。

## 4. 核心概念

### `chunk_size` 不是检索条数

`chunk_size` 是单个 chunk 的目标文本长度；当前 `RecursiveCharacterTextSplitter` 默认按字符长度计算。它决定“每块资料有多大”，不决定一次检索返回多少块。

```text
chunk_size=800

一份 2,000 字符资料
-> 大约多个 800 字符以内的 chunk
```

检索返回多少候选片段是 Stage 6.4 的职责，不能在切分阶段混在一起。

### `chunk_overlap` 保留边界上下文

如果两块文档完全不重叠，一句话或一个概念恰好落在边界上时，后半块可能失去理解所需的前文。`chunk_overlap` 让相邻 chunk 共享一小段内容：

```text
chunk_size=4, chunk_overlap=1

abcdefghij
-> abcd
-> defg
-> ghij
```

`d` 同时出现在第一、第二块，`g` 同时出现在第二、第三块。默认值 `800 / 120` 只是当前本地 Markdown 的起点，不是所有语料、模型和语言的万能配置。

### 为什么使用递归切分器

`RecursiveCharacterTextSplitter` 会优先尝试较自然的分隔符，例如段落、换行和空格；当它们无法满足大小约束时，再继续向更细的分隔方式退化。

这比单纯每隔固定字符截断更容易保留段落或句子的边界，但不会保证每个 chunk 都是完整语义单元。遇到代码块、表格、中文长段落或非常长的 URL 时，仍需要在后续根据语料观察效果。

### 元数据必须随 chunk 传递

切分前：

```text
Document(
  page_content="完整资料",
  metadata={"source": "materials/stage-5.md", "topic": "agent"},
)
```

切分后每一块仍应包含：

```text
metadata={"source": "materials/stage-5.md", "topic": "agent"}
```

后续检索只会命中其中一个 chunk。若切分时丢失 `source`，回答层就无法指出资料来自哪里。

### 参数校验是业务边界，不是框架细节

`chunk_overlap >= chunk_size` 会让相邻块无法向前推进；负数 overlap 和非正数 chunk size 同样没有合理语义。项目函数先给出明确的 `ValueError`，避免调用方依赖底层库难以理解的异常文本。

```text
chunk_size <= 0        -> ValueError
chunk_overlap < 0      -> ValueError
chunk_overlap >= size  -> ValueError
```

### 切分不是 LangGraph 编排

切分是 RAG 的资料预处理步骤。LangGraph 解决的是有状态、可分支、可恢复的工作流编排；当前函数接收文档、返回文档，没有 node、edge、checkpoint 或 long-running state。

## 5. 代码实现

先在 `requirements.txt` 固定当前已验证版本：

```text
langchain-text-splitters==1.1.2
```

然后在 `app/rag.py` 引入切分器并定义默认值：

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter


DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120


def split_material_documents(
    documents: list[Document],
    *,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[Document]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be greater than or equal to 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_documents(documents)
```

测试需要同时检查文本重叠和元数据：

```python
documents = [
    Document(
        page_content="abcdefghij",
        metadata={"source": "materials/example.md", "topic": "testing"},
    )
]

chunks = split_material_documents(documents, chunk_size=4, chunk_overlap=1)

assert [chunk.page_content for chunk in chunks] == ["abcd", "defg", "ghij"]
assert all(chunk.metadata["source"] == "materials/example.md" for chunk in chunks)
```

本次不修改：

```text
.env.example
app/api.py
app/langchain_agent.py
app/models.py
app/cli.py
```

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

安装锁定依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行 RAG 单元测试：

```powershell
py -3.13 -m pytest tests/test_rag.py
```

查看真实资料的默认 chunk 数量：

```powershell
py -3.13 -c "from app.rag import load_local_materials, split_material_documents; print(len(split_material_documents(load_local_materials())))"
```

运行完整测试集：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/rag.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_rag.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

无需 `.env` 或真实 provider。

## 7. 常见错误

### 把 `chunk_size` 当成 token 数

当前切分器默认按字符长度计算。token 数量会因模型和语言而变化，不能把 800 字符直接当成 800 token。

### 设置零或负数的 chunk size

这没有可执行的切分语义。调用会被项目函数明确拒绝，而不是交给底层库猜测意图。

### overlap 大于或等于 chunk size

相邻块没有足够前进空间，切分逻辑不成立。overlap 应该只保留边界上下文，而不是复制整块文档。

### 切分后重新构造没有来源的字符串

这样会丢失 6.2 建立的引用链。应继续处理 `Document`，让 splitter 自动保留 metadata。

### 用 chunk 顺序回答问题

chunk 顺序只代表资料预处理顺序，不代表相关性。Stage 6.4 才会根据问题和向量相似度检索候选片段。

### 在这里接入向量库或模型

切分产物还没有 embedding，也没有问答契约。提前接入会把预处理、检索和生成的测试揉成一个不可定位的流程。

## 8. 练习

练习 1：手工写出 `abcdefghij` 在 `chunk_size=4`、`chunk_overlap=1` 下的三个 chunk，并标记重叠字符。

练习 2：解释 `chunk_size=800` 与“检索返回 3 条结果”为什么是两个不同参数。

练习 3：为一份包含长代码块的 Markdown 资料设计一个实验，判断默认分隔符是否适合它。不要先修改生产默认值。

练习 4：说明为什么 `source` 和 `topic` 都必须随 chunk 保留。

练习 5：判断下面的参数是否有效，并说明原因：

```text
A. chunk_size=800, chunk_overlap=120
B. chunk_size=120, chunk_overlap=120
C. chunk_size=0, chunk_overlap=0
D. chunk_size=500, chunk_overlap=-10
```

## 9. 验收标准

完成后，应能做到：

- 用 `split_material_documents()` 将 `Document` 切分为 chunk。
- 解释 `chunk_size`、`chunk_overlap` 和检索返回条数的区别。
- 证明相邻 chunk 按配置保留 overlap。
- 证明 `source` 与其他 metadata 在所有 chunk 上保留。
- 识别并拒绝无效大小参数。
- 说明当前仍未实现 embedding、向量检索、回答或 API。
- 运行 `py -3.13 -m pytest tests/test_rag.py` 通过。
- 运行完整 `pytest`、`py_compile` 和依赖安装检查通过。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

| 当前能力 | 后续升级 |
| --- | --- |
| 完整 `Document` | 6.3：递归切分为保留 metadata 的 chunk |
| chunk 集合 | 6.4：生成 embedding 并建立 vector store / retriever |
| `source` 元数据 | 6.5：作为回答引用返回 |
| 参数校验 | 6.6：转换为 API 的明确请求错误 |
| retriever | 后续可以作为 LangChain Agent 的只读工具 |
| 多步骤学习流程 | Stage 7：LangGraph State、node 和 edge |
| 持久执行和人工协作 | Stage 8：LangGraph 进阶 |
| 长任务规划和文件产物 | Stage 9：Deep Agents |

项目继续只有一条真实代码主线：

```text
ai-learning-assistant/
```

没有为课程创建代码副本。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-6/06-03-document-splitting.md`

修改文件：

- `ai-learning-assistant/requirements.txt`
- `ai-learning-assistant/app/rag.py`
- `ai-learning-assistant/tests/test_rag.py`
- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`

生成器状态：

- `.agents/skills/tutorial-course-builder/references/course-state.md`
- `.agents/skills/tutorial-course-builder/references/quality-gates.md`

代码变更：

- 锁定 `langchain-text-splitters==1.1.2`。
- 新增 `split_material_documents()` 与默认 `800 / 120` 参数。
- 新增 chunk 内容、overlap、metadata、空输入和无效参数的回归测试。

环境变量变更：无。

官方版本与文档核对：

- [LangChain text splitter integrations](https://docs.langchain.com/oss/python/integrations/splitters)
- [Recursive text splitter guide](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)
- [langchain-text-splitters 1.1.2](https://pypi.org/project/langchain-text-splitters/1.1.2/)

下一步：第 6.4 课，使用 embedding、vector store 和 retriever 找到相关 chunk。
