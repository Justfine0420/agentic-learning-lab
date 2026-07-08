from app import llm_demo


def test_llm_demo_loads_student_and_prints_suggestion(monkeypatch, capsys):
    student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["FastAPI route 是普通函数加装饰器"],
    }

    monkeypatch.setattr(llm_demo, "load_student", lambda: student)
    monkeypatch.setattr(llm_demo, "generate_learning_suggestion", lambda loaded_student: "建议：复习 FastAPI。")

    llm_demo.main()

    output = capsys.readouterr().out
    assert output == "建议：复习 FastAPI。\n"
