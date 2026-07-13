from collections.abc import Callable, Mapping, Sequence
from typing import Any

from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from app.config import LLMSettings, get_llm_settings, require_llm_api_key
from app.models import StructuredLearningSuggestion, Student
from app.storage import load_student
from app.suggestions import build_suggestion


LEARNING_AGENT_SYSTEM_PROMPT = (
    "你是一个 Python 和 AI Agent 学习助教。"
    "你会根据学员档案、学习目标和笔记，给出清晰、可执行的学习建议。"
    "你现在有多个只读工具，可以查询当前保存在本地 JSON 中的学员档案、最近学习笔记和离线规则建议。"
    "当你需要了解学员姓名、目标、Python 水平、学习笔记或基础建议时，优先调用合适的工具。"
    "不要编造本地文件里的内容。"
    "回答必须使用中文。"
)

DEFAULT_AGENT_QUESTION = "请先查询当前学习档案、最近笔记和离线规则建议，再生成今天的学习建议。"

STRUCTURED_LEARNING_AGENT_SYSTEM_PROMPT = (
    LEARNING_AGENT_SYSTEM_PROMPT
    + "最终结果必须形成结构化学习建议，包括摘要、1 到 3 条行动建议和下一检查点。"
)

STRUCTURED_RESPONSE_TOOL_MESSAGE = "已生成结构化学习建议。"


class VolcengineCompatibleChatOpenAI(ChatOpenAI):
    """ChatOpenAI adapter for Ark coding endpoints that reject required tool choice."""

    def bind_tools(
        self,
        tools: Sequence[dict[str, Any] | type | Callable[..., Any] | BaseTool],
        *,
        tool_choice: dict | str | bool | None = None,
        **kwargs: Any,
    ) -> Any:
        if isinstance(tool_choice, str) and tool_choice in {"any", "required"}:
            tool_choice = None
        return super().bind_tools(tools, tool_choice=tool_choice, **kwargs)


def should_relax_required_tool_choice(settings: LLMSettings) -> bool:
    return settings.provider in {"volcengine_agent_plan", "volcengine_coding"}


def format_student_profile_for_tool(student: Student, *, include_notes: bool = True) -> str:
    name = student["name"] or "未填写"
    goal = student["goal"] or "未填写"
    python_level = student["python_level"] or "未填写"

    lines = [
        f"学员姓名：{name}",
        f"学习目标：{goal}",
        f"Python 水平：{python_level}",
    ]

    if include_notes:
        lines.append("学习笔记：")
        if student["notes"]:
            lines.extend(f"{index}. {note}" for index, note in enumerate(student["notes"], start=1))
        else:
            lines.append("暂无笔记")

    return "\n".join(lines)


def read_current_student_profile(include_notes: bool = True) -> str:
    """Read the current learner profile from local JSON storage."""
    student = load_student()
    return format_student_profile_for_tool(student, include_notes=include_notes)


def normalize_note_limit(limit: int) -> int:
    if limit < 1:
        return 1
    if limit > 10:
        return 10
    return limit


def format_recent_notes_for_tool(notes: list[str], *, limit: int = 5) -> str:
    current_limit = normalize_note_limit(limit)
    if not notes:
        return "最近学习笔记：\n暂无笔记"

    recent_notes = notes[-current_limit:]
    lines = [f"最近学习笔记（最多 {current_limit} 条）："]
    lines.extend(f"{index}. {note}" for index, note in enumerate(recent_notes, start=1))
    return "\n".join(lines)


def read_recent_learning_notes(limit: int = 5) -> str:
    """Read recent learner notes from local JSON storage."""
    student = load_student()
    return format_recent_notes_for_tool(student["notes"], limit=limit)


def build_current_rule_based_suggestion() -> str:
    """Build the current offline rule-based learning suggestion."""
    student = load_student()
    return build_suggestion(student["python_level"])


read_current_student_profile_tool = tool(
    "read_current_student_profile",
    description=(
        "读取当前保存在本地 JSON 文件中的学员档案，包括姓名、学习目标、Python 水平，"
        "并可按需包含学习笔记。这个工具只读，不会修改任何文件。"
    ),
)(read_current_student_profile)


read_recent_learning_notes_tool = tool(
    "read_recent_learning_notes",
    description=(
        "读取当前保存在本地 JSON 文件中的最近学习笔记。参数 limit 表示最多返回几条，"
        "会被限制在 1 到 10 之间。这个工具只读，不会修改任何文件。"
    ),
)(read_recent_learning_notes)


build_current_rule_based_suggestion_tool = tool(
    "build_current_rule_based_suggestion",
    description=(
        "根据当前学员的 Python 水平生成离线规则学习建议。这个工具只使用本地规则，"
        "不会调用大模型，也不会修改任何文件。"
    ),
)(build_current_rule_based_suggestion)


def build_learning_agent_tools() -> list[Any]:
    return [
        read_current_student_profile_tool,
        read_recent_learning_notes_tool,
        build_current_rule_based_suggestion_tool,
    ]


def build_langchain_chat_model(settings: LLMSettings | None = None) -> ChatOpenAI:
    current_settings = require_llm_api_key(settings or get_llm_settings())
    model_class = VolcengineCompatibleChatOpenAI if should_relax_required_tool_choice(current_settings) else ChatOpenAI

    return model_class(
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
    tools: list[Any] | None = None,
) -> Any:
    current_model = model or build_langchain_chat_model(settings)
    current_tools = tools if tools is not None else build_learning_agent_tools()

    return create_agent(
        model=current_model,
        tools=current_tools,
        system_prompt=LEARNING_AGENT_SYSTEM_PROMPT,
    )


def build_learning_agent_response_format() -> Any:
    return ToolStrategy(
        StructuredLearningSuggestion,
        tool_message_content=STRUCTURED_RESPONSE_TOOL_MESSAGE,
    )


def create_structured_learning_agent(
    *,
    settings: LLMSettings | None = None,
    model: Any | None = None,
    tools: list[Any] | None = None,
    response_format: Any | None = None,
) -> Any:
    current_model = model or build_langchain_chat_model(settings)
    current_tools = tools if tools is not None else build_learning_agent_tools()
    current_response_format = (
        response_format if response_format is not None else build_learning_agent_response_format()
    )

    return create_agent(
        model=current_model,
        tools=current_tools,
        system_prompt=STRUCTURED_LEARNING_AGENT_SYSTEM_PROMPT,
        response_format=current_response_format,
    )


def build_learning_agent_messages(
    question: str = DEFAULT_AGENT_QUESTION,
) -> list[dict[str, str]]:
    return [{"role": "user", "content": f"用户问题：{question}"}]


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


def extract_structured_agent_response(agent_result: Mapping[str, Any]) -> StructuredLearningSuggestion:
    structured_response = agent_result.get("structured_response")

    if isinstance(structured_response, StructuredLearningSuggestion):
        return structured_response

    if isinstance(structured_response, Mapping):
        return StructuredLearningSuggestion.model_validate(structured_response)

    raise ValueError("LangChain agent result did not contain structured_response.")


def run_learning_agent(
    question: str = DEFAULT_AGENT_QUESTION,
    *,
    settings: LLMSettings | None = None,
    agent: Any | None = None,
) -> str:
    current_agent = agent or create_learning_agent(settings=settings)
    result = current_agent.invoke({"messages": build_learning_agent_messages(question)})
    return extract_agent_text(result)


def run_structured_learning_agent(
    question: str = DEFAULT_AGENT_QUESTION,
    *,
    settings: LLMSettings | None = None,
    agent: Any | None = None,
) -> StructuredLearningSuggestion:
    current_agent = agent or create_structured_learning_agent(settings=settings)
    result = current_agent.invoke({"messages": build_learning_agent_messages(question)})
    return extract_structured_agent_response(result)
