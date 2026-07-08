from fastapi.testclient import TestClient

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
