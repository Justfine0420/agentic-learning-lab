# AI 学习助教

这是 Agentic Learning Lab 的贯穿教学项目。

当前阶段：阶段 2，Python 工程化。

## 当前能力

- 项目目录已创建。
- 可以通过命令行收集学员名字、学习目标和 Python 水平。
- 使用 `student` 字典保存当前学员资料。
- 可以添加一条学习笔记，并保存在 `student["notes"]` 列表中。
- 已把标题展示、资料收集、笔记添加和档案展示拆成独立函数。
- 可以根据 Python 水平输出今日学习建议。
- 提供循环菜单，可以反复添加笔记、查看资料、生成建议和退出。
- 已把入口、CLI 交互和学习状态拆分到不同模块：`main.py`、`cli.py`、`student_state.py`。

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

## 依赖说明

阶段 2.1 暂不安装第三方依赖。

后续课程会逐步把依赖写入 `requirements.txt`。
