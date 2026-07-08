from app import structured_llm_demo
from app.models import StructuredLearningSuggestion


def test_structured_llm_demo_loads_student_and_prints_json(monkeypatch, capsys):
    student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["Pydantic 可以校验模型输出"],
    }
    suggestion = StructuredLearningSuggestion(
        summary="今天做结构化输出练习。",
        suggestions=[
            {
                "title": "写 schema",
                "description": "用 Pydantic 描述返回结构。",
                "estimated_minutes": 20,
            }
        ],
        next_checkpoint="能解释 model_validate_json。",
    )

    def fake_generate_structured_learning_suggestion(loaded_student):
        assert loaded_student == student
        return suggestion

    monkeypatch.setattr(structured_llm_demo, "load_student", lambda: student)
    monkeypatch.setattr(
        structured_llm_demo,
        "generate_structured_learning_suggestion",
        fake_generate_structured_learning_suggestion,
    )

    structured_llm_demo.main()

    output = capsys.readouterr().out
    assert '"summary": "今天做结构化输出练习。"' in output
    assert '"estimated_minutes": 20' in output
    assert output.endswith("}\n")
