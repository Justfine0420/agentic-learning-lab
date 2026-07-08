from pathlib import Path

from fastapi.testclient import TestClient

from app import storage
from app.api import app


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
