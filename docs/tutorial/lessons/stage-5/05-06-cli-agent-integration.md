# 第 5.6 课：CLI 接入 LangChain Agent

## 1. 本课目标

第 5.5 课已经让 LangChain Agent 返回结构化结果：

```text
StructuredLearningSuggestion
```

但这个能力还停留在 demo 入口：

```powershell
py -3.13 -m app.langchain_structured_agent_demo
```

这一节要把结构化 Agent 接入真实 CLI 菜单。完成后，用户在命令行里选择第 4 项时，不再直接调用 Stage 4 的普通 LLM 封装，而是调用 LangChain Agent：

```text
CLI 选项 4
-> run_structured_learning_agent()
-> LangChain Agent
-> 读取本地学习档案和笔记
-> 返回 StructuredLearningSuggestion
-> CLI 格式化展示
```

你会学到：

- 为什么 CLI 不应该绕过 Agent 继续调用旧的模型函数。
- 为什么调用 Agent 前要先保存当前 `student`。
- 如何把结构化对象展示成命令行文本。
- 如何保留离线规则建议作为降级入口。
- 如何用 pytest 测试 CLI 菜单路由，而不真的调用模型 provider。
- 为什么这里仍然不做 streaming。

## 2. 你会新增什么项目能力

完成后，CLI 菜单会变成：

```text
请选择操作：
1. 添加学习笔记
2. 查看学习信息
3. 查看离线规则建议
4. 生成 Agent 学习建议
5. 退出
```

第 3 项仍然是离线规则建议，不依赖 provider。

第 4 项会调用 LangChain Agent。Agent 会通过工具读取同一份本地学习状态：

```text
data/student.json
```

这比 Stage 4 的 CLI 入口更接近真正的 Agent 应用：

| 阶段 | CLI 第 4 项调用什么 | 特点 |
| --- | --- | --- |
| Stage 4.5 | `generate_structured_learning_suggestion(student)` | 直接把内存里的学生资料发给模型 |
| Stage 5.6 | `run_structured_learning_agent()` | Agent 自己通过工具读取资料、笔记和规则建议 |

## 3. 前置知识

开始前需要理解：

- Stage 4.5 已经有 CLI AI 建议入口。
- Stage 5.4 已经给 Agent 注册多个只读工具。
- Stage 5.5 已经新增 `run_structured_learning_agent()`。
- `StructuredLearningSuggestion` 已经可以被 CLI 格式化展示。
- 当前项目仍使用 JSON 文件作为学习状态存储。

现有 CLI 的关键结构是：

```python
def run_cli() -> None:
    while True:
        print("1. 添加学习笔记")
        print("2. 查看学习信息")
        print("3. 查看离线规则建议")
        print("4. 生成 AI 学习建议")
        print("5. 退出")
```

这一次只改第 4 项背后的实现，不改 CLI 的整体交互模型。

## 4. 核心概念

### CLI 是入口层，不应该复制 Agent 逻辑

CLI 的职责是：

```text
接收用户选择
调用业务函数
把结果打印出来
```

Agent 的职责是：

```text
根据问题决定调用哪些工具
读取学习档案和笔记
结合离线规则建议
生成结构化学习建议
```

如果 CLI 直接拼 prompt、直接读笔记、直接解析模型输出，它就会和 Agent 层重复。后续 FastAPI 再接入时还会重复一遍。

所以 CLI 要做的是调用稳定入口：

```python
run_structured_learning_agent()
```

### 为什么调用前要保存 `student`

当前 CLI 会把学习状态保存在内存中的 `student` 字典里，同时也会写入：

```text
data/student.json
```

LangChain 工具不是直接读取 CLI 的内存变量，而是调用：

```python
load_student()
```

也就是说，Agent 看到的是 JSON 文件里的状态。

因此，调用 Agent 前先执行：

```python
save_student(student)
```

这能保证 CLI 当前状态和 Agent 工具读取到的状态一致。

### 为什么菜单文案改成 Agent 建议

Stage 4 的菜单文案是：

```text
4. 生成 AI 学习建议
```

这句话太宽。普通模型调用也可以叫 AI 建议，Agent 工具调用也可以叫 AI 建议。

Stage 5 的重点是 LangChain Agent，所以菜单改成：

```text
4. 生成 Agent 学习建议
```

这样用户能看出第 4 项已经进入 Agent 路径。

### 为什么继续保留第 3 项

第 3 项是离线规则建议：

```text
3. 查看离线规则建议
```

它不依赖 API key、不依赖网络、不依赖本地模型。

当 provider 没配好、模型请求失败或结构化输出不满足校验时，CLI 会提示用户先使用第 3 项。这不是“悄悄降级”，而是明确告诉用户 Agent 暂不可用。

## 5. 代码实现

### 第一步：替换 CLI 的 Agent 入口导入

打开：

```text
ai-learning-assistant/app/cli.py
```

原来导入的是 Stage 4 的普通 LLM 函数：

```python
from app.llm import generate_structured_learning_suggestion
```

现在改成导入 Stage 5.5 的结构化 Agent 入口：

```python
import httpx
from openai import OpenAIError

from app.langchain_agent import run_structured_learning_agent
```

这个改动表示 CLI 第 4 项不再直接和普通 LLM 封装交互。

### 第二步：把格式化函数改成 Agent 命名

原来的函数名是：

```python
def format_ai_suggestion(suggestion: StructuredLearningSuggestion) -> list[str]:
```

改成：

```python
def format_agent_suggestion(suggestion: StructuredLearningSuggestion) -> list[str]:
    lines = [
        "=== Agent 学习建议 ===",
        f"摘要：{suggestion.summary}",
        "",
        "行动建议：",
    ]

    for index, item in enumerate(suggestion.suggestions, start=1):
        lines.append(f"{index}. {item.title}（约 {item.estimated_minutes} 分钟）")
        lines.append(f"   {item.description}")

    lines.extend(["", f"下一检查点：{suggestion.next_checkpoint}"])
    return lines
```

注意：这里不重新定义结构，只继续使用 `StructuredLearningSuggestion`。

格式化函数只是把结构化对象变成 CLI 可读文本。

### 第三步：把 `suggest_with_ai()` 改成 `suggest_with_agent()`

原来的函数会直接调用：

```python
generate_structured_learning_suggestion(student)
```

现在改成：

```python
def suggest_with_agent() -> None:
    print()

    try:
        save_student(student)
        suggestion = run_structured_learning_agent()
    except RuntimeError as error:
        print("Agent 建议暂不可用。")
        print(f"原因：{error}")
        print("你可以先使用选项 3 获取离线规则建议。")
    except (httpx.HTTPError, OpenAIError):
        print("Agent 建议暂不可用。")
        print("原因：AI provider 请求失败。")
        print("你可以先使用选项 3 获取离线规则建议。")
    except ValueError as error:
        print("Agent 建议暂不可用。")
        print(f"原因：{error}")
        print("你可以先使用选项 3 获取离线规则建议。")
    else:
        for line in format_agent_suggestion(suggestion):
            print(line)
```

这里有三个重点：

- `save_student(student)` 让 Agent 工具读到最新状态。
- `run_structured_learning_agent()` 是唯一 Agent 调用入口。
- `OpenAIError` 用来覆盖 LangChain / OpenAI SDK 真实 provider 调用失败。
- 出错时提示用户使用第 3 项，而不是自动返回离线规则建议。

不自动降级的原因很简单：如果用户选择的是 Agent 建议，就应该知道 Agent 是否真的可用。静默降级会让学习者误以为自己已经跑通了 LangChain Agent。

### 第四步：更新菜单文案和路由

在 `run_cli()` 里，把菜单第 4 项改成：

```python
print("4. 生成 Agent 学习建议")
```

分支也改成：

```python
elif choice == "4":
    suggest_with_agent()
```

完整菜单仍然保持 5 个选项：

```text
1. 添加学习笔记
2. 查看学习信息
3. 查看离线规则建议
4. 生成 Agent 学习建议
5. 退出
```

### 第五步：更新 CLI 测试

打开：

```text
ai-learning-assistant/tests/test_cli.py
```

格式化测试改成验证 Agent 文案：

```python
def test_format_agent_suggestion_returns_readable_lines() -> None:
    ...
    assert cli.format_agent_suggestion(suggestion) == [
        "=== Agent 学习建议 ===",
        ...
    ]
```

成功路径测试不调用真实 provider，而是 monkeypatch：

```python
def fake_run_structured_learning_agent():
    return suggestion

monkeypatch.setattr(
    cli,
    "run_structured_learning_agent",
    fake_run_structured_learning_agent,
)
```

同时验证调用 Agent 前会保存当前状态：

```python
assert saved_students == [dict(cli.student)]
```

菜单路由测试要验证第 4 项调用的是：

```python
suggest_with_agent()
```

而不是旧的 `suggest_with_ai()`。

## 6. 运行方式

进入真实项目目录：

```powershell
cd ai-learning-assistant
```

先运行 CLI 测试：

```powershell
py -3.13 -m pytest tests/test_cli.py
```

再运行全量测试：

```powershell
py -3.13 -m pytest
```

语法检查：

```powershell
py -3.13 -m py_compile app/main.py app/cli.py app/student_state.py app/storage.py app/models.py app/api.py app/suggestions.py app/config.py app/llm.py app/llm_demo.py app/structured_llm_demo.py app/langchain_agent.py app/langchain_agent_demo.py app/langchain_structured_agent_demo.py app/__init__.py tests/test_storage.py tests/test_api.py tests/test_cli.py tests/test_suggestions.py tests/test_config.py tests/test_llm.py tests/test_llm_demo.py tests/test_structured_llm_demo.py tests/test_langchain_agent.py tests/test_langchain_agent_demo.py tests/test_langchain_structured_agent_demo.py
```

手动运行 CLI：

```powershell
py -3.13 -m app.main
```

选择：

```text
4. 生成 Agent 学习建议
```

这条路径需要 provider 配置可用，并且模型支持当前 Agent 工具调用和结构化输出策略。

如果没有配置 provider，或者本地 Ollama 没启动，CLI 应该提示：

```text
Agent 建议暂不可用。
你可以先使用选项 3 获取离线规则建议。
```

## 7. 常见错误

### CLI 仍然调用旧的 LLM 函数

如果 `cli.py` 里还出现：

```python
generate_structured_learning_suggestion(student)
```

说明第 4 项还没有真正进入 LangChain Agent 路径。

Stage 4 的普通 LLM 调用仍然可以保留给 API 和 demo 使用，但 Stage 5.6 的 CLI 应该调用 `run_structured_learning_agent()`。

### 忘记在调用 Agent 前保存状态

Agent 工具读取的是 `data/student.json`。

如果 CLI 内存里的 `student` 没写入文件，Agent 可能读到旧资料或旧笔记。

因此 `save_student(student)` 必须在 `run_structured_learning_agent()` 前执行。

### 在测试里真的调用 provider

CLI 单元测试不应该访问网络，也不应该依赖 `.env`。

正确做法是 monkeypatch：

```python
run_structured_learning_agent
```

这样测试的是 CLI 路由、保存时机、格式化和错误提示，不是 provider 能不能联网。

### 把 Agent 失败静默变成离线建议

不要在第 4 项失败时直接打印离线建议。

用户选择第 4 项，是为了验证 Agent 能力。失败时要明确暴露原因，并提示第 3 项仍然可用。

### 现在就做 streaming

CLI 已经可以调用结构化 Agent，但输出仍然是一次性结果。

Streaming 需要展示 token、工具调用事件和最终结构化结果，复杂度会高很多。当前先把入口层接稳定。

## 8. 练习

练习 1：解释为什么 `suggest_with_agent()` 里要先调用 `save_student(student)`。

练习 2：把测试里的 `fake_run_structured_learning_agent()` 改成抛出 `RuntimeError("missing api key")`，观察 CLI 输出。

练习 3：运行 CLI，先添加一条学习笔记，再选择第 4 项。思考 Agent 工具为什么能读到刚添加的笔记。

练习 4：搜索代码：

```powershell
rg -n "generate_structured_learning_suggestion|run_structured_learning_agent" app tests
```

说明哪些地方仍然使用普通 LLM 函数，哪些地方已经使用 LangChain Agent。

练习 5：解释为什么第 3 项离线规则建议仍然需要保留。

## 9. 验收标准

完成后，你应该能做到：

- 运行 CLI 时看到第 4 项是 `生成 Agent 学习建议`。
- 说明 CLI 第 4 项调用的是 `run_structured_learning_agent()`。
- 说明 Agent 为什么读取 `data/student.json`，而不是直接读取 CLI 内存变量。
- 看懂 `format_agent_suggestion()` 如何展示结构化对象。
- 看懂 `suggest_with_agent()` 的错误处理边界。
- 运行 `py -3.13 -m pytest tests/test_cli.py` 通过。
- 运行 `py -3.13 -m pytest` 通过。
- 解释为什么第 4 项失败时不静默降级成第 3 项。

## 10. 和后续 LangChain / LangGraph / Deep Agents 的关系

CLI 接入 Agent 之后，Stage 5 的能力第一次进入用户日常操作入口。

| 当前内容 | 后续升级 |
| --- | --- |
| `suggest_with_agent()` | 5.7 可以把同样的 Agent 能力接到 FastAPI |
| `save_student(student)` | 后续数据库或 checkpoint 会替换当前 JSON 同步点 |
| `run_structured_learning_agent()` | RAG 阶段可以继续给 Agent 增加资料检索工具 |
| 明确暴露 Agent 失败 | API 层可以转换成明确 HTTP 错误 |
| 非 streaming CLI 输出 | LangGraph streaming 阶段再处理过程事件 |

LangGraph 阶段会进一步把“生成建议”升级为可控流程，比如：

```text
判断水平 -> 教学 -> 出题 -> 批改 -> 下一步建议
```

Deep Agents 阶段会处理更长任务，比如自动拆学习计划、写总结文件、调用子 Agent 审查学习路线。

## 11. 本课变更清单

新增文件：

- `docs/tutorial/lessons/stage-5/05-06-cli-agent-integration.md`

修改文件：

- `README.md`
- `docs/tutorial/README.md`
- `ai-learning-assistant/README.md`
- `ai-learning-assistant/app/cli.py`
- `ai-learning-assistant/tests/test_cli.py`

代码变更：

- CLI 第 4 项从 `生成 AI 学习建议` 改为 `生成 Agent 学习建议`。
- `cli.py` 改为导入 `run_structured_learning_agent()`。
- `format_ai_suggestion()` 改为 `format_agent_suggestion()`。
- `suggest_with_ai()` 改为 `suggest_with_agent()`。
- `suggest_with_agent()` 调用 Agent 前会先保存当前 `student`。
- CLI 测试改为 monkeypatch `run_structured_learning_agent()`。
- CLI 测试覆盖 `httpx.HTTPError` 和 `OpenAIError` 两类 provider 失败。
- CLI 菜单路由测试改为验证第 4 项进入 Agent 分支。

依赖变更：

- 无。

环境变量变更：

- 无。

官方文档核对：

- [LangChain structured output](https://docs.langchain.com/oss/python/langchain/structured-output)

下一步：

- 第 5.7 课：FastAPI 接入 LangChain Agent。
- 让 API 也能调用结构化 Agent，形成 CLI 和 API 的统一 Agent 能力入口。
