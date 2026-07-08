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
