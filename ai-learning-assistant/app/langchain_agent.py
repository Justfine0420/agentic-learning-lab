from collections.abc import Mapping
from typing import Any

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.config import LLMSettings, get_llm_settings, require_llm_api_key
from app.llm import build_learning_suggestion_input
from app.models import Student


LEARNING_AGENT_SYSTEM_PROMPT = (
    "你是一个 Python 和 AI Agent 学习助教。"
    "你会根据学员档案、学习目标和笔记，给出清晰、可执行的学习建议。"
    "当前阶段你还没有工具，只能基于输入里的学员资料回答。"
    "回答必须使用中文。"
)

DEFAULT_AGENT_QUESTION = "请根据当前学习档案，生成今天的学习建议。"


def build_langchain_chat_model(settings: LLMSettings | None = None) -> ChatOpenAI:
    current_settings = require_llm_api_key(settings or get_llm_settings())

    return ChatOpenAI(
        model=current_settings.model,
        api_key=current_settings.api_key,
        base_url=current_settings.base_url,
        temperature=0.2,
        timeout=30.0,
        max_retries=1,
    )


def create_learning_agent(
    *,
    settings: LLMSettings | None = None,
    model: Any | None = None,
) -> Any:
    current_model = model or build_langchain_chat_model(settings)

    return create_agent(
        model=current_model,
        tools=[],
        system_prompt=LEARNING_AGENT_SYSTEM_PROMPT,
    )


def build_learning_agent_messages(
    student: Student,
    question: str = DEFAULT_AGENT_QUESTION,
) -> list[dict[str, str]]:
    content = "\n\n".join(
        [
            build_learning_suggestion_input(student),
            f"用户问题：{question}",
        ]
    )
    return [{"role": "user", "content": content}]


def content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, Mapping):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(part.strip() for part in parts if part.strip()).strip()

    return ""


def extract_agent_text(agent_result: Mapping[str, Any]) -> str:
    messages = agent_result.get("messages")
    if not isinstance(messages, list) or len(messages) == 0:
        raise ValueError("LangChain agent result did not contain messages.")

    last_message = messages[-1]

    if isinstance(last_message, Mapping):
        text = content_to_text(last_message.get("content"))
        if text:
            return text
        text = content_to_text(last_message.get("content_blocks"))
        if text:
            return text
    else:
        text = content_to_text(getattr(last_message, "content", None))
        if text:
            return text
        text = content_to_text(getattr(last_message, "content_blocks", None))
        if text:
            return text

    raise ValueError("LangChain agent response message content is empty.")


def run_learning_agent(
    student: Student,
    question: str = DEFAULT_AGENT_QUESTION,
    *,
    settings: LLMSettings | None = None,
    agent: Any | None = None,
) -> str:
    current_agent = agent or create_learning_agent(settings=settings)
    result = current_agent.invoke({"messages": build_learning_agent_messages(student, question)})
    return extract_agent_text(result)
