from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import OpenAIError

from app import storage
from app import api
from app.api import app
from app.models import MaterialAnswer, StructuredLearningSuggestion


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ai-learning-assistant",
    }


def test_preview_profile_returns_response_model() -> None:
    response = client.post(
        "/profile/preview",
        json={
            "name": "Alice",
            "goal": "Learn FastAPI",
            "python_level": "beginner",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "name": "Alice",
        "goal": "Learn FastAPI",
        "python_level": "beginner",
        "note_count": 0,
    }


def test_preview_profile_rejects_invalid_level() -> None:
    response = client.post(
        "/profile/preview",
        json={
            "name": "Alice",
            "goal": "Learn FastAPI",
            "python_level": "expert",
        },
    )

    assert response.status_code == 422


def use_tmp_storage(tmp_path: Path) -> None:
    storage.DATA_FILE = tmp_path / "student.json"
    storage.BROKEN_DATA_FILE = tmp_path / "student.broken.json"


def test_get_profile_returns_saved_student(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Bob",
            "goal": "Build APIs",
            "python_level": "basic",
            "notes": ["Keep existing notes"],
        }
    )

    response = client.get("/profile")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Bob",
        "goal": "Build APIs",
        "python_level": "basic",
        "note_count": 1,
    }


def test_post_profile_saves_student_and_keeps_notes(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Old",
            "goal": "Old goal",
            "python_level": "beginner",
            "notes": ["Do not remove"],
        }
    )

    response = client.post(
        "/profile",
        json={
            "name": "Carol",
            "goal": "Use profile API",
            "python_level": "intermediate",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "name": "Carol",
        "goal": "Use profile API",
        "python_level": "intermediate",
        "note_count": 1,
    }
    assert storage.load_student() == {
        "name": "Carol",
        "goal": "Use profile API",
        "python_level": "intermediate",
        "notes": ["Do not remove"],
    }


def test_post_profile_rejects_invalid_level(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)

    response = client.post(
        "/profile",
        json={
            "name": "Carol",
            "goal": "Use profile API",
            "python_level": "advanced",
        },
    )

    assert response.status_code == 422


def test_get_notes_returns_saved_notes(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Dana",
            "goal": "Review APIs",
            "python_level": "basic",
            "notes": ["Read FastAPI docs", "Write API tests"],
        }
    )

    response = client.get("/notes")

    assert response.status_code == 200
    assert response.json() == {
        "notes": ["Read FastAPI docs", "Write API tests"],
        "note_count": 2,
    }


def test_get_note_returns_one_saved_note(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Dana",
            "goal": "Review APIs",
            "python_level": "basic",
            "notes": ["Read FastAPI docs", "Write API tests"],
        }
    )

    response = client.get("/notes/2")

    assert response.status_code == 200
    assert response.json() == {
        "index": 2,
        "content": "Write API tests",
    }


def test_get_note_returns_404_when_note_missing(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Dana",
            "goal": "Review APIs",
            "python_level": "basic",
            "notes": ["Read FastAPI docs"],
        }
    )

    response = client.get("/notes/2")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "学习笔记不存在。",
    }


def test_post_notes_appends_note_and_keeps_profile(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Eve",
            "goal": "Build note API",
            "python_level": "intermediate",
            "notes": ["Existing note"],
        }
    )

    response = client.post(
        "/notes",
        json={
            "content": "New API note",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "notes": ["Existing note", "New API note"],
        "note_count": 2,
    }
    assert storage.load_student() == {
        "name": "Eve",
        "goal": "Build note API",
        "python_level": "intermediate",
        "notes": ["Existing note", "New API note"],
    }


def test_post_notes_rejects_empty_note(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)

    response = client.post(
        "/notes",
        json={
            "content": "",
        },
    )

    assert response.status_code == 422


def test_post_notes_rejects_blank_note_with_business_error(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Eve",
            "goal": "Build note API",
            "python_level": "intermediate",
            "notes": ["Existing note"],
        }
    )

    response = client.post(
        "/notes",
        json={
            "content": "   ",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "学习笔记不能为空。",
    }
    assert storage.load_student()["notes"] == ["Existing note"]


def test_get_suggestion_returns_rule_based_suggestion(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Frank",
            "goal": "Review conditionals",
            "python_level": "beginner",
            "notes": ["Need API suggestion"],
        }
    )

    response = client.get("/suggestion")

    assert response.status_code == 200
    assert response.json() == {
        "python_level": "beginner",
        "suggestion": "建议：今天学习变量、函数、字典。",
    }
    assert storage.load_student() == {
        "name": "Frank",
        "goal": "Review conditionals",
        "python_level": "beginner",
        "notes": ["Need API suggestion"],
    }


def test_get_suggestion_uses_fallback_for_missing_level(tmp_path: Path) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Grace",
            "goal": "",
            "python_level": "",
            "notes": [],
        }
    )

    response = client.get("/suggestion")

    assert response.status_code == 200
    assert response.json() == {
        "python_level": "",
        "suggestion": "建议：今天开始学习 LangChain 的 agent。",
    }


def test_post_ai_suggestion_returns_structured_result(tmp_path: Path, monkeypatch) -> None:
    use_tmp_storage(tmp_path)
    student = {
        "name": "Hank",
        "goal": "Use AI suggestions",
        "python_level": "basic",
        "notes": ["Structured output should be validated"],
    }
    storage.save_student(student)
    suggestion = StructuredLearningSuggestion(
        summary="今天先复习 FastAPI 和 Pydantic。",
        suggestions=[
            {
                "title": "复习接口边界",
                "description": "区分规则建议接口和 AI 建议接口。",
                "estimated_minutes": 20,
            }
        ],
        next_checkpoint="能说明 provider 不可用时为什么返回 503。",
    )

    def fake_generate_structured_learning_suggestion(loaded_student):
        assert loaded_student == student
        return suggestion

    monkeypatch.setattr(
        api,
        "generate_structured_learning_suggestion",
        fake_generate_structured_learning_suggestion,
    )

    response = client.post("/ai/suggestion")

    assert response.status_code == 200
    assert response.json() == {
        "source": "ai",
        "suggestion": {
            "summary": "今天先复习 FastAPI 和 Pydantic。",
            "suggestions": [
                {
                    "title": "复习接口边界",
                    "description": "区分规则建议接口和 AI 建议接口。",
                    "estimated_minutes": 20,
                }
            ],
            "next_checkpoint": "能说明 provider 不可用时为什么返回 503。",
        },
    }
    assert storage.load_student() == student


def test_post_ai_suggestion_returns_503_when_provider_config_missing(tmp_path: Path, monkeypatch) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Ivy",
            "goal": "Use AI suggestions",
            "python_level": "basic",
            "notes": [],
        }
    )

    def fake_generate_structured_learning_suggestion(_student):
        raise RuntimeError("Missing required environment variable: DEEPSEEK_API_KEY.")

    monkeypatch.setattr(
        api,
        "generate_structured_learning_suggestion",
        fake_generate_structured_learning_suggestion,
    )

    response = client.post("/ai/suggestion")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Missing required environment variable: DEEPSEEK_API_KEY.",
    }


def test_post_ai_suggestion_returns_503_when_model_output_is_invalid(tmp_path: Path, monkeypatch) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Jill",
            "goal": "Use AI suggestions",
            "python_level": "basic",
            "notes": [],
        }
    )

    def fake_generate_structured_learning_suggestion(_student):
        raise ValueError("LLM response was not a valid structured learning suggestion.")

    monkeypatch.setattr(
        api,
        "generate_structured_learning_suggestion",
        fake_generate_structured_learning_suggestion,
    )

    response = client.post("/ai/suggestion")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "LLM response was not a valid structured learning suggestion.",
    }


def test_post_ai_suggestion_returns_503_when_provider_request_fails(tmp_path: Path, monkeypatch) -> None:
    use_tmp_storage(tmp_path)
    storage.save_student(
        {
            "name": "Kim",
            "goal": "Use AI suggestions",
            "python_level": "basic",
            "notes": [],
        }
    )

    def fake_generate_structured_learning_suggestion(_student):
        raise httpx.RequestError("network failed")

    monkeypatch.setattr(
        api,
        "generate_structured_learning_suggestion",
        fake_generate_structured_learning_suggestion,
    )

    response = client.post("/ai/suggestion")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "AI provider request failed.",
    }


def test_post_chat_returns_structured_agent_result(monkeypatch) -> None:
    suggestion = StructuredLearningSuggestion(
        summary="今天用 FastAPI 调用结构化 Agent。",
        suggestions=[
            {
                "title": "调用只读工具",
                "description": "让 Agent 读取当前学习档案和笔记。",
                "estimated_minutes": 25,
            }
        ],
        next_checkpoint="能区分 /chat 和 /ai/suggestion。",
    )

    def fake_run_structured_learning_agent(question: str) -> StructuredLearningSuggestion:
        assert question == "我今天应该先练什么？"
        return suggestion

    monkeypatch.setattr(
        api,
        "run_structured_learning_agent",
        fake_run_structured_learning_agent,
    )

    response = client.post("/chat", json={"question": "我今天应该先练什么？"})

    assert response.status_code == 200
    assert response.json() == {
        "source": "agent",
        "suggestion": {
            "summary": "今天用 FastAPI 调用结构化 Agent。",
            "suggestions": [
                {
                    "title": "调用只读工具",
                    "description": "让 Agent 读取当前学习档案和笔记。",
                    "estimated_minutes": 25,
                }
            ],
            "next_checkpoint": "能区分 /chat 和 /ai/suggestion。",
        },
    }


def test_post_chat_rejects_empty_and_blank_questions(monkeypatch) -> None:
    def should_not_run_agent(_question: str) -> StructuredLearningSuggestion:
        raise AssertionError("invalid request should not invoke the agent")

    monkeypatch.setattr(api, "run_structured_learning_agent", should_not_run_agent)

    missing_response = client.post("/chat", json={})
    empty_response = client.post("/chat", json={"question": ""})
    blank_response = client.post("/chat", json={"question": "   "})

    assert missing_response.status_code == 422
    assert empty_response.status_code == 422
    assert blank_response.status_code == 400
    assert blank_response.json() == {"detail": "问题不能为空。"}


def test_post_chat_declares_error_responses_in_openapi() -> None:
    responses = app.openapi()["paths"]["/chat"]["post"]["responses"]

    assert {"200", "400", "422", "503"}.issubset(responses)


@pytest.mark.parametrize(
    ("agent_error", "expected_detail"),
    [
        (
            RuntimeError("Missing required environment variable: DEEPSEEK_API_KEY."),
            "Missing required environment variable: DEEPSEEK_API_KEY.",
        ),
        (httpx.ConnectError("network failed"), "AI provider request failed."),
        (OpenAIError("provider failed"), "AI provider request failed."),
        (
            ValueError("LangChain agent result did not contain structured_response."),
            "LangChain agent result did not contain structured_response.",
        ),
    ],
)
def test_post_chat_returns_503_for_agent_errors(monkeypatch, agent_error, expected_detail) -> None:
    def fake_run_structured_learning_agent(_question: str) -> StructuredLearningSuggestion:
        raise agent_error

    monkeypatch.setattr(
        api,
        "run_structured_learning_agent",
        fake_run_structured_learning_agent,
    )

    response = client.post("/chat", json={"question": "请生成今天的建议。"})

    assert response.status_code == 503
    assert response.json() == {"detail": expected_detail}


def test_post_ask_materials_returns_grounded_answer(monkeypatch) -> None:
    def fake_answer_question_from_local_materials(question: str, *, k: int) -> MaterialAnswer:
        assert question == "Python 类型标注有什么用？"
        assert k == 2
        return MaterialAnswer(
            answer="类型标注能说明函数参数和返回值。",
            sources=["materials/stage-2.md"],
        )

    monkeypatch.setattr(
        api,
        "answer_question_from_local_materials",
        fake_answer_question_from_local_materials,
    )

    response = client.post(
        "/ask-materials",
        json={
            "question": "  Python 类型标注有什么用？  ",
            "k": 2,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "类型标注能说明函数参数和返回值。",
        "sources": ["materials/stage-2.md"],
    }


def test_post_ask_materials_rejects_empty_blank_question_and_invalid_k(monkeypatch) -> None:
    def should_not_answer_materials(_question: str, *, k: int) -> MaterialAnswer:
        raise AssertionError("invalid request should not invoke RAG")

    monkeypatch.setattr(
        api,
        "answer_question_from_local_materials",
        should_not_answer_materials,
    )

    missing_response = client.post("/ask-materials", json={})
    empty_response = client.post("/ask-materials", json={"question": ""})
    blank_response = client.post("/ask-materials", json={"question": "   "})
    invalid_k_response = client.post(
        "/ask-materials",
        json={"question": "Python 类型标注有什么用？", "k": 0},
    )

    assert missing_response.status_code == 422
    assert empty_response.status_code == 422
    assert blank_response.status_code == 400
    assert blank_response.json() == {"detail": "问题不能为空。"}
    assert invalid_k_response.status_code == 422


def test_post_ask_materials_declares_error_responses_in_openapi() -> None:
    responses = app.openapi()["paths"]["/ask-materials"]["post"]["responses"]

    assert {"200", "400", "422", "503"}.issubset(responses)


@pytest.mark.parametrize(
    ("rag_error", "expected_detail"),
    [
        (
            RuntimeError("Missing required environment variable: DEEPSEEK_API_KEY."),
            "Missing required environment variable: DEEPSEEK_API_KEY.",
        ),
        (
            FileNotFoundError("Materials directory does not exist: missing-materials"),
            "Materials directory does not exist: missing-materials",
        ),
        (httpx.ConnectError("network failed"), "AI provider request failed."),
        (
            ValueError("LLM response was not a valid material answer."),
            "LLM response was not a valid material answer.",
        ),
    ],
)
def test_post_ask_materials_returns_503_for_rag_errors(
    monkeypatch,
    rag_error,
    expected_detail,
) -> None:
    def fake_answer_question_from_local_materials(_question: str, *, k: int) -> MaterialAnswer:
        raise rag_error

    monkeypatch.setattr(
        api,
        "answer_question_from_local_materials",
        fake_answer_question_from_local_materials,
    )

    response = client.post("/ask-materials", json={"question": "请根据资料回答。"})

    assert response.status_code == 503
    assert response.json() == {"detail": expected_detail}
