from typing import Any

import httpx

from app.config import LLMSettings, get_llm_settings, require_llm_api_key
from app.models import Student


SYSTEM_INSTRUCTIONS = (
    "你是一个 Python 和 AI Agent 学习助教。"
    "你会根据学员目标、Python 水平和最近笔记，给出简短、可执行的今日学习建议。"
    "回答必须使用中文，最多 3 条建议。"
)


def build_chat_completions_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}/chat/completions"


def build_learning_suggestion_input(student: Student) -> str:
    notes = student.get("notes", [])

    if notes:
        note_lines = "\n".join(f"{index}. {note}" for index, note in enumerate(notes[-5:], start=1))
    else:
        note_lines = "暂无笔记"

    return "\n".join(
        [
            f"学员姓名：{student.get('name') or '未填写'}",
            f"学习目标：{student.get('goal') or '未填写'}",
            f"Python 水平：{student.get('python_level') or '未填写'}",
            "最近学习笔记：",
            note_lines,
            "请生成今天的学习建议。",
        ]
    )


def build_learning_suggestion_messages(student: Student) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {"role": "user", "content": build_learning_suggestion_input(student)},
    ]


def parse_chat_completion_text(response_data: dict[str, Any]) -> str:
    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError("LLM response did not contain message content.") from error

    if not isinstance(content, str) or not content.strip():
        raise ValueError("LLM response message content is empty.")

    return content.strip()


def call_chat_completion(
    messages: list[dict[str, str]],
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
    timeout: float = 30.0,
) -> str:
    current_settings = require_llm_api_key(settings or get_llm_settings())
    url = build_chat_completions_url(current_settings.base_url)
    payload = {
        "model": current_settings.model,
        "messages": messages,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {current_settings.api_key}",
        "Content-Type": "application/json",
    }

    if client is not None:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return parse_chat_completion_text(response.json())

    with httpx.Client(timeout=timeout) as default_client:
        response = default_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return parse_chat_completion_text(response.json())


def generate_learning_suggestion(
    student: Student,
    *,
    settings: LLMSettings | None = None,
    client: httpx.Client | None = None,
) -> str:
    messages = build_learning_suggestion_messages(student)
    return call_chat_completion(messages, settings=settings, client=client)
