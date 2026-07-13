import pytest
from langchain.agents.middleware import ModelRequest
from langchain.agents.structured_output import ToolStrategy
from langchain.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest

from app import langchain_agent
from app.config import LLMSettings
from app.models import StructuredLearningSuggestion


def build_settings(*, api_key: str = "test-key", requires_api_key: bool = True) -> LLMSettings:
    return LLMSettings(
        provider="deepseek",
        api_key=api_key,
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com",
        model="deepseek-v4-flash",
        requires_api_key=requires_api_key,
    )


def test_build_langchain_chat_model_uses_llm_settings() -> None:
    model = langchain_agent.build_langchain_chat_model(build_settings())

    assert model.model_name == "deepseek-v4-flash"
    assert str(model.openai_api_base) == "https://api.deepseek.com"
    assert model.temperature == 0.2
    assert model.max_retries == 1


def test_build_langchain_chat_model_uses_volcengine_compatible_wrapper() -> None:
    settings = LLMSettings(
        provider="volcengine_agent_plan",
        api_key="test-key",
        api_key_env="VOLCENGINE_AGENT_PLAN_API_KEY",
        base_url="https://ark.cn-beijing.volces.com/api/coding/v3",
        model="ark-code-latest",
        requires_api_key=True,
    )

    model = langchain_agent.build_langchain_chat_model(settings)

    assert isinstance(model, langchain_agent.VolcengineCompatibleChatOpenAI)


def test_volcengine_wrapper_relaxes_required_tool_choice(monkeypatch) -> None:
    calls = {}

    def fake_bind_tools(self, tools, *, tool_choice=None, **kwargs):
        calls["tools"] = tools
        calls["tool_choice"] = tool_choice
        calls["kwargs"] = kwargs
        return "bound-model"

    monkeypatch.setattr(langchain_agent.ChatOpenAI, "bind_tools", fake_bind_tools)

    model = langchain_agent.VolcengineCompatibleChatOpenAI(
        model="ark-code-latest",
        api_key="test-key",
        base_url="https://ark.cn-beijing.volces.com/api/coding/v3",
    )

    result = model.bind_tools([], tool_choice="any")

    assert result == "bound-model"
    assert calls["tool_choice"] is None


def test_build_langchain_chat_model_requires_api_key() -> None:
    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        langchain_agent.build_langchain_chat_model(build_settings(api_key=""))


def test_format_student_profile_for_tool_includes_notes() -> None:
    student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["FastAPI route 是普通函数加装饰器"],
    }

    text = langchain_agent.format_student_profile_for_tool(student)

    assert text == (
        "学员姓名：Alice\n"
        "学习目标：学习 LangChain\n"
        "Python 水平：basic\n"
        "学习笔记：\n"
        "1. FastAPI route 是普通函数加装饰器"
    )


def test_format_student_profile_for_tool_can_hide_notes() -> None:
    student = {
        "name": "",
        "goal": "",
        "python_level": "",
        "notes": ["隐藏笔记"],
    }

    text = langchain_agent.format_student_profile_for_tool(student, include_notes=False)

    assert text == "学员姓名：未填写\n学习目标：未填写\nPython 水平：未填写"


def test_read_current_student_profile_uses_storage(monkeypatch) -> None:
    student = {
        "name": "Bob",
        "goal": "理解 tool calling",
        "python_level": "intermediate",
        "notes": ["工具应该只读"],
    }

    monkeypatch.setattr(langchain_agent, "load_student", lambda: student)

    assert langchain_agent.read_current_student_profile.invoke({}) == (
        "学员姓名：Bob\n"
        "学习目标：理解 tool calling\n"
        "Python 水平：intermediate\n"
        "学习笔记：\n"
        "1. 工具应该只读"
    )


def test_normalize_note_limit_keeps_tool_bounds() -> None:
    assert langchain_agent.normalize_note_limit(-1) == 1
    assert langchain_agent.normalize_note_limit(0) == 1
    assert langchain_agent.normalize_note_limit(3) == 3
    assert langchain_agent.normalize_note_limit(99) == 10


def test_format_recent_notes_for_tool_returns_recent_notes() -> None:
    notes = ["note 1", "note 2", "note 3", "note 4"]

    assert langchain_agent.format_recent_notes_for_tool(notes, limit=2) == (
        "最近学习笔记（最多 2 条）：\n"
        "1. note 3\n"
        "2. note 4"
    )


def test_format_recent_notes_for_tool_handles_empty_notes() -> None:
    assert langchain_agent.format_recent_notes_for_tool([], limit=5) == "最近学习笔记：\n暂无笔记"


def test_read_recent_learning_notes_uses_storage(monkeypatch) -> None:
    monkeypatch.setattr(
        langchain_agent,
        "load_student",
        lambda: {
            "name": "Dana",
            "goal": "多工具调用",
            "python_level": "basic",
            "notes": ["笔记 1", "笔记 2", "笔记 3"],
        },
    )

    assert langchain_agent.read_recent_learning_notes.invoke({"limit": 2}) == (
        "最近学习笔记（最多 2 条）：\n"
        "1. 笔记 2\n"
        "2. 笔记 3"
    )


def test_build_current_rule_based_suggestion_uses_storage(monkeypatch) -> None:
    monkeypatch.setattr(
        langchain_agent,
        "load_student",
        lambda: {
            "name": "Eve",
            "goal": "复习 Python",
            "python_level": "beginner",
            "notes": [],
        },
    )

    assert "变量" in langchain_agent.build_current_rule_based_suggestion.invoke({})


def test_build_learning_agent_tools_contains_multiple_tools() -> None:
    tools = langchain_agent.build_learning_agent_tools()
    tool_names = [item.name for item in tools]

    assert tool_names == [
        "read_current_student_profile",
        "read_recent_learning_notes",
        "build_current_rule_based_suggestion",
    ]
    assert all("只读" in item.description or "不会修改" in item.description for item in tools)


def test_profile_tool_invokes_profile_reader(monkeypatch) -> None:
    monkeypatch.setattr(
        langchain_agent,
        "load_student",
        lambda: {
            "name": "Carol",
            "goal": "让 Agent 查询档案",
            "python_level": "basic",
            "notes": [],
        },
    )

    text = langchain_agent.read_current_student_profile.invoke({"include_notes": True})

    assert "学员姓名：Carol" in text
    assert "暂无笔记" in text


def test_recent_notes_tool_invokes_note_reader(monkeypatch) -> None:
    monkeypatch.setattr(
        langchain_agent,
        "load_student",
        lambda: {
            "name": "Frank",
            "goal": "测试多工具",
            "python_level": "basic",
            "notes": ["A", "B", "C"],
        },
    )

    text = langchain_agent.read_recent_learning_notes.invoke({"limit": 2})

    assert "1. B" in text
    assert "2. C" in text


def test_rule_suggestion_tool_invokes_rule_suggestion(monkeypatch) -> None:
    monkeypatch.setattr(
        langchain_agent,
        "load_student",
        lambda: {
            "name": "Grace",
            "goal": "测试规则建议",
            "python_level": "basic",
            "notes": [],
        },
    )

    text = langchain_agent.build_current_rule_based_suggestion.invoke({})

    assert "类" in text


def test_create_learning_agent_uses_model_prompt_and_default_tools(monkeypatch) -> None:
    calls = {}
    fake_model = object()
    fake_agent = object()

    def fake_create_agent(*, model, tools, middleware):
        calls["model"] = model
        calls["tools"] = tools
        calls["middleware"] = middleware
        return fake_agent

    monkeypatch.setattr(langchain_agent, "create_agent", fake_create_agent)

    agent = langchain_agent.create_learning_agent(model=fake_model)

    assert agent is fake_agent
    assert calls["model"] is fake_model
    assert len(calls["tools"]) == 3
    assert calls["tools"][0].name == "read_current_student_profile"
    assert calls["tools"][1].name == "read_recent_learning_notes"
    assert calls["tools"][2].name == "build_current_rule_based_suggestion"
    assert calls["middleware"] is langchain_agent.LEARNING_AGENT_MIDDLEWARE


def test_create_learning_agent_accepts_explicit_tools(monkeypatch) -> None:
    calls = {}
    fake_model = object()
    fake_tools = [object()]
    fake_agent = object()

    def fake_create_agent(*, model, tools, middleware):
        calls["model"] = model
        calls["tools"] = tools
        calls["middleware"] = middleware
        return fake_agent

    monkeypatch.setattr(langchain_agent, "create_agent", fake_create_agent)

    agent = langchain_agent.create_learning_agent(model=fake_model, tools=fake_tools)

    assert agent is fake_agent
    assert calls["tools"] is fake_tools


def test_build_learning_agent_response_format_uses_structured_suggestion_schema() -> None:
    response_format = langchain_agent.build_learning_agent_response_format()

    assert isinstance(response_format, ToolStrategy)
    assert response_format.schema is StructuredLearningSuggestion
    assert response_format.tool_message_content == langchain_agent.STRUCTURED_RESPONSE_TOOL_MESSAGE


def test_create_structured_learning_agent_uses_response_format(monkeypatch) -> None:
    calls = {}
    fake_model = object()
    fake_agent = object()
    fake_response_format = object()

    def fake_create_agent(*, model, tools, middleware, response_format):
        calls["model"] = model
        calls["tools"] = tools
        calls["middleware"] = middleware
        calls["response_format"] = response_format
        return fake_agent

    monkeypatch.setattr(langchain_agent, "create_agent", fake_create_agent)

    agent = langchain_agent.create_structured_learning_agent(
        model=fake_model,
        response_format=fake_response_format,
    )

    assert agent is fake_agent
    assert calls["model"] is fake_model
    assert len(calls["tools"]) == 3
    assert calls["response_format"] is fake_response_format
    assert calls["middleware"] is langchain_agent.LEARNING_AGENT_MIDDLEWARE


def test_dynamic_prompt_uses_agent_state() -> None:
    request = ModelRequest(
        model=langchain_agent.build_langchain_chat_model(build_settings()),
        messages=[],
        state={"messages": [{"role": "user"}, {"role": "assistant"}]},
    )

    prompt = langchain_agent.build_learning_agent_system_prompt.wrap_model_call(
        request,
        lambda updated_request: updated_request.system_message,
    )

    assert prompt is not None
    assert "当前会话已有多条消息" in prompt.content


def test_tool_error_middleware_returns_safe_tool_message() -> None:
    request = ToolCallRequest(
        tool_call={
            "name": "read_current_student_profile",
            "args": {},
            "id": "tool-call-1",
            "type": "tool_call",
        },
        tool=None,
        state={},
        runtime=None,
    )

    def raise_storage_error(_: ToolCallRequest) -> ToolMessage:
        raise OSError("student.json is unavailable")

    result = langchain_agent.recover_from_learning_tool_error.wrap_tool_call(request, raise_storage_error)

    assert result.tool_call_id == "tool-call-1"
    assert "无法据此给出可靠建议" in result.content


def test_build_learning_agent_messages_contains_question_only() -> None:
    messages = langchain_agent.build_learning_agent_messages("我今天应该学什么？")

    assert messages == [
        {
            "role": "user",
            "content": "用户问题：我今天应该学什么？",
        }
    ]


def test_extract_agent_text_reads_dict_message_content() -> None:
    result = {"messages": [{"role": "assistant", "content": "  建议：复习 LangChain。  "}]}

    assert langchain_agent.extract_agent_text(result) == "建议：复习 LangChain。"


def test_extract_agent_text_reads_content_blocks() -> None:
    result = {
        "messages": [
            {
                "role": "assistant",
                "content_blocks": [
                    {"type": "text", "text": "第一段。"},
                    {"type": "text", "text": "第二段。"},
                ],
            }
        ]
    }

    assert langchain_agent.extract_agent_text(result) == "第一段。\n第二段。"


def test_extract_agent_text_rejects_empty_messages() -> None:
    with pytest.raises(ValueError, match="did not contain messages"):
        langchain_agent.extract_agent_text({"messages": []})


def test_extract_structured_agent_response_accepts_model_instance() -> None:
    suggestion = StructuredLearningSuggestion(
        summary="今天先稳定结构化输出。",
        suggestions=[
            {
                "title": "阅读 schema",
                "description": "确认结构化字段含义。",
                "estimated_minutes": 15,
            }
        ],
        next_checkpoint="能解释 structured_response。",
    )

    assert langchain_agent.extract_structured_agent_response({"structured_response": suggestion}) is suggestion


def test_extract_structured_agent_response_validates_mapping() -> None:
    response = langchain_agent.extract_structured_agent_response(
        {
            "structured_response": {
                "summary": "用结构化结果承接 Agent 输出。",
                "suggestions": [
                    {
                        "title": "运行 demo",
                        "description": "观察结构化 JSON 输出。",
                        "estimated_minutes": 20,
                    }
                ],
                "next_checkpoint": "能说明为什么 CLI 接入要等结构稳定。",
            }
        }
    )

    assert response.summary == "用结构化结果承接 Agent 输出。"
    assert response.suggestions[0].title == "运行 demo"


def test_extract_structured_agent_response_rejects_missing_response() -> None:
    with pytest.raises(ValueError, match="structured_response"):
        langchain_agent.extract_structured_agent_response({"messages": []})


def test_run_learning_agent_invokes_agent_and_returns_text() -> None:
    class FakeAgent:
        def invoke(self, payload):
            assert payload["messages"][0]["role"] == "user"
            assert "请给一个简短建议。" in payload["messages"][0]["content"]
            assert "学习 LangChain" not in payload["messages"][0]["content"]
            return {"messages": [{"role": "assistant", "content": "建议：先调用工具查询档案。"}]}

    answer = langchain_agent.run_learning_agent(
        "请给一个简短建议。",
        agent=FakeAgent(),
    )

    assert answer == "建议：先调用工具查询档案。"


def test_run_structured_learning_agent_invokes_agent_and_returns_structured_response() -> None:
    suggestion = StructuredLearningSuggestion(
        summary="今天学习结构化 Agent 输出。",
        suggestions=[
            {
                "title": "理解 response_format",
                "description": "确认 Agent 最终 state 中的 structured_response。",
                "estimated_minutes": 25,
            }
        ],
        next_checkpoint="能运行结构化 Agent demo。",
    )

    class FakeAgent:
        def invoke(self, payload):
            assert payload["messages"][0]["role"] == "user"
            assert "请生成结构化建议。" in payload["messages"][0]["content"]
            return {"structured_response": suggestion}

    response = langchain_agent.run_structured_learning_agent(
        "请生成结构化建议。",
        agent=FakeAgent(),
    )

    assert response is suggestion
