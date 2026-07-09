import pytest

from app.config import LLMSettings
from app import langchain_agent


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


def test_create_learning_agent_uses_model_prompt_and_empty_tools(monkeypatch) -> None:
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
    assert calls["tools"] == []
    assert "当前阶段你还没有工具" in calls["system_prompt"]


def test_build_learning_agent_messages_contains_profile_and_question() -> None:
    student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["FastAPI route 是普通函数加装饰器"],
    }

    messages = langchain_agent.build_learning_agent_messages(student, "我今天应该学什么？")

    assert messages == [
        {
            "role": "user",
            "content": (
                "学员姓名：Alice\n"
                "学习目标：学习 LangChain\n"
                "Python 水平：basic\n"
                "最近学习笔记：\n"
                "1. FastAPI route 是普通函数加装饰器\n"
                "请生成今天的学习建议。\n\n"
                "用户问题：我今天应该学什么？"
            ),
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
    student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["Agent 会组合 model 和 prompt"],
    }

    class FakeAgent:
        def invoke(self, payload):
            assert payload["messages"][0]["role"] == "user"
            assert "学习 LangChain" in payload["messages"][0]["content"]
            assert "请给一个简短建议。" in payload["messages"][0]["content"]
            return {"messages": [{"role": "assistant", "content": "建议：创建第一个 Agent。"}]}

    answer = langchain_agent.run_learning_agent(
        student,
        "请给一个简短建议。",
        agent=FakeAgent(),
    )

    assert answer == "建议：创建第一个 Agent。"
