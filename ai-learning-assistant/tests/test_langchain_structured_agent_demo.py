from app import langchain_structured_agent_demo
from app.models import StructuredLearningSuggestion


def test_langchain_structured_agent_demo_prints_structured_json(monkeypatch, capsys) -> None:
    suggestion = StructuredLearningSuggestion(
        summary="今天做结构化 Agent 输出练习。",
        suggestions=[
            {
                "title": "运行结构化 demo",
                "description": "确认 LangChain Agent 返回可解析结果。",
                "estimated_minutes": 20,
            }
        ],
        next_checkpoint="能解释 structured_response。",
    )

    def fake_run_structured_learning_agent(question):
        assert question == langchain_structured_agent_demo.DEFAULT_AGENT_QUESTION
        return suggestion

    monkeypatch.setattr(
        langchain_structured_agent_demo,
        "run_structured_learning_agent",
        fake_run_structured_learning_agent,
    )

    langchain_structured_agent_demo.main()

    output = capsys.readouterr().out
    assert '"summary": "今天做结构化 Agent 输出练习。"' in output
    assert '"estimated_minutes": 20' in output
    assert output.endswith("}\n")
