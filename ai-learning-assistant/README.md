# AI 学习助教

这是 Agentic Learning Lab 的贯穿教学项目。

当前阶段：阶段 3，FastAPI 基础。

## 当前能力

- 项目目录已创建。
- 可以通过命令行收集学员名字、学习目标和 Python 水平。
- 使用 `student` 字典保存当前学员资料。
- 可以添加一条学习笔记，并保存在 `student["notes"]` 列表中。
- 已把标题展示、资料收集、笔记添加和档案展示拆成独立函数。
- 可以根据 Python 水平输出今日学习建议。
- 提供循环菜单，可以反复添加笔记、查看资料、生成建议和退出。
- 已把入口、CLI 交互和学习状态拆分到不同模块：`main.py`、`cli.py`、`student_state.py`。
- 可以把学员资料和学习笔记保存到 `data/student.json`，下次运行时自动加载。
- 可以处理文件不存在、JSON 损坏和字段缺失等基础存储异常。
- 使用 `TypedDict` 描述 `Student` 数据结构，为后续 Pydantic 和 LangGraph State 铺路。
- 已为存储模块添加第一批 pytest 单元测试。
- 已补充 Stage 2 学习资料：`materials/stage-2.md`。
- 已新增最小 FastAPI 应用：`app/api.py`。
- 已提供健康检查接口：`GET /health`。
- 已为 `/health` 添加 API 测试：`tests/test_api.py`。

## 推荐运行方式

后续课程优先使用 Python 3.13：

```powershell
py -3.13 -m app.main
```

## 目录说明

```text
app/        Python 应用代码
data/       本地学习数据
materials/  学习资料
outputs/    生成的学习计划和总结
tests/      测试代码
```

## 学习资料

- `materials/stage-2.md`：阶段 2 补充学习资料，覆盖模块导入、`Path`、JSON 文件读写、异常处理、pytest 基础和当前数据流。

## 依赖说明

阶段 2.5 引入 pytest 作为测试依赖。
阶段 3.1 引入 FastAPI 作为 Web API 框架，并固定到本课已验证版本。
同时引入 `fastapi-cli`、`uvicorn[standard]` 和 `httpx`，用于开发服务器和 API 测试。

后续课程会逐步把依赖写入 `requirements.txt`。

安装依赖：

```powershell
py -3.13 -m pip install -r requirements.txt
```

运行测试：

```powershell
py -3.13 -m pytest
```

启动 API：

```powershell
py -3.13 -m uvicorn app.api:app --reload
```

健康检查：

```text
GET http://127.0.0.1:8000/health
```
