from app import langchain_agent_demo


def test_langchain_agent_demo_loads_student_and_prints_answer(monkeypatch, capsys) -> None:
    student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["先创建无工具 Agent"],
    }

    def fake_run_learning_agent(loaded_student, question):
        assert loaded_student == student
        assert question == langchain_agent_demo.DEFAULT_AGENT_QUESTION
        return "建议：先运行 LangChain Agent demo。"

    monkeypatch.setattr(langchain_agent_demo, "load_student", lambda: student)
    monkeypatch.setattr(langchain_agent_demo, "run_learning_agent", fake_run_learning_agent)

    langchain_agent_demo.main()

    output = capsys.readouterr().out
    assert output == "建议：先运行 LangChain Agent demo。\n"
