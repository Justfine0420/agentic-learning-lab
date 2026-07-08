import httpx
import pytest

from app.config import LLMSettings
from app.llm import (
    build_chat_completions_url,
    build_learning_suggestion_input,
    build_learning_suggestion_messages,
    call_chat_completion,
    generate_learning_suggestion,
    parse_chat_completion_text,
)
from app.models import Student


class FakeLLMClient:
    def __init__(self, response_data: dict):
        self.response_data = response_data
        self.request: dict | None = None

    def post(self, url: str, *, headers: dict[str, str], json: dict) -> httpx.Response:
        self.request = {
            "url": url,
            "headers": headers,
            "json": json,
        }
        request = httpx.Request("POST", url)
        return httpx.Response(200, json=self.response_data, request=request)


def make_settings() -> LLMSettings:
    return LLMSettings(
        provider="ollama",
        api_key="ollama",
        api_key_env="OLLAMA_API_KEY",
        base_url="http://localhost:11434/v1",
        model="qwen3:8b",
        requires_api_key=False,
    )


def make_student() -> Student:
    return {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["FastAPI route 是普通函数加装饰器", "Pydantic 可以校验请求体"],
    }


def test_build_chat_completions_url_strips_trailing_slash():
    assert build_chat_completions_url("http://localhost:11434/v1/") == (
        "http://localhost:11434/v1/chat/completions"
    )


def test_build_learning_suggestion_input_contains_student_context():
    text = build_learning_suggestion_input(make_student())

    assert "Alice" in text
    assert "学习 LangChain" in text
    assert "basic" in text
    assert "FastAPI route 是普通函数加装饰器" in text
    assert "Pydantic 可以校验请求体" in text


def test_build_learning_suggestion_input_limits_notes_to_recent_five():
    student: Student = {
        "name": "Bob",
        "goal": "学习 FastAPI",
        "python_level": "beginner",
        "notes": [f"note-{index}" for index in range(1, 8)],
    }

    text = build_learning_suggestion_input(student)

    assert "note-1" not in text
    assert "note-2" not in text
    assert "note-3" in text
    assert "note-7" in text


def test_build_learning_suggestion_messages_uses_system_and_user_roles():
    messages = build_learning_suggestion_messages(make_student())

    assert messages[0]["role"] == "system"
    assert "学习助教" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "Alice" in messages[1]["content"]


def test_parse_chat_completion_text_returns_content():
    data = {"choices": [{"message": {"content": " 今天复习 Pydantic。 "}}]}

    assert parse_chat_completion_text(data) == "今天复习 Pydantic。"


def test_parse_chat_completion_text_rejects_missing_content():
    with pytest.raises(ValueError, match="message content"):
        parse_chat_completion_text({"choices": []})


def test_call_chat_completion_posts_openai_compatible_payload():
    client = FakeLLMClient({"choices": [{"message": {"content": "建议：复习 FastAPI。"}}]})
    messages = [{"role": "user", "content": "hello"}]

    result = call_chat_completion(messages, settings=make_settings(), client=client)

    assert result == "建议：复习 FastAPI。"
    assert client.request is not None
    assert client.request["url"] == "http://localhost:11434/v1/chat/completions"
    assert client.request["headers"]["Authorization"] == "Bearer ollama"
    assert client.request["json"]["model"] == "qwen3:8b"
    assert client.request["json"]["messages"] == messages
    assert client.request["json"]["temperature"] == 0.2


def test_generate_learning_suggestion_uses_student_context():
    client = FakeLLMClient({"choices": [{"message": {"content": "建议：完成一个 LangChain 小练习。"}}]})

    result = generate_learning_suggestion(make_student(), settings=make_settings(), client=client)

    assert result == "建议：完成一个 LangChain 小练习。"
    assert client.request is not None
    user_message = client.request["json"]["messages"][1]["content"]
    assert "学习 LangChain" in user_message
    assert "Pydantic 可以校验请求体" in user_message
