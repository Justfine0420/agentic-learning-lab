from app import langchain_agent_demo


def test_langchain_agent_demo_prints_agent_answer(monkeypatch, capsys) -> None:
    def fake_run_learning_agent(question):
        assert question == langchain_agent_demo.DEFAULT_AGENT_QUESTION
        return "建议：先运行 LangChain Agent demo。"

    monkeypatch.setattr(langchain_agent_demo, "run_learning_agent", fake_run_learning_agent)

    langchain_agent_demo.main()

    output = capsys.readouterr().out
    assert output == "建议：先运行 LangChain Agent demo。\n"
