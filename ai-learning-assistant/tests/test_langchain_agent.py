import pytest

from app import langchain_agent
from app.config import LLMSettings


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

    assert langchain_agent.read_current_student_profile() == (
        "学员姓名：Bob\n"
        "学习目标：理解 tool calling\n"
        "Python 水平：intermediate\n"
        "学习笔记：\n"
        "1. 工具应该只读"
    )


def test_build_learning_agent_tools_contains_profile_tool() -> None:
    tools = langchain_agent.build_learning_agent_tools()

    assert len(tools) == 1
    assert tools[0].name == "read_current_student_profile"
    assert "只读" in tools[0].description


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

    text = langchain_agent.read_current_student_profile_tool.invoke({"include_notes": True})

    assert "学员姓名：Carol" in text
    assert "暂无笔记" in text


def test_create_learning_agent_uses_model_prompt_and_default_tools(monkeypatch) -> None:
    calls = {}
    fake_model = object()
    fake_agent = object()

    def fake_create_agent(*, model, tools, system_prompt):
        calls["model"] = model
        calls["tools"] = tools
        calls["system_prompt"] = system_prompt
        return fake_agent

    monkeypatch.setattr(langchain_agent, "create_agent", fake_create_agent)

    agent = langchain_agent.create_learning_agent(model=fake_model)

    assert agent is fake_agent
    assert calls["model"] is fake_model
    assert len(calls["tools"]) == 1
    assert calls["tools"][0].name == "read_current_student_profile"
    assert "只读工具" in calls["system_prompt"]


def test_create_learning_agent_accepts_explicit_tools(monkeypatch) -> None:
    calls = {}
    fake_model = object()
    fake_tools = [object()]
    fake_agent = object()

    def fake_create_agent(*, model, tools, system_prompt):
        calls["model"] = model
        calls["tools"] = tools
        calls["system_prompt"] = system_prompt
        return fake_agent

    monkeypatch.setattr(langchain_agent, "create_agent", fake_create_agent)

    agent = langchain_agent.create_learning_agent(model=fake_model, tools=fake_tools)

    assert agent is fake_agent
    assert calls["tools"] is fake_tools


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
