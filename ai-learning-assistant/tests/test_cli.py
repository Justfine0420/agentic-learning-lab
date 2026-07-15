import httpx
import pytest
from openai import OpenAIError

from app import cli
from app.models import StructuredLearningSuggestion
from app.storage import create_default_student


@pytest.fixture(autouse=True)
def reset_cli_student() -> None:
    cli.replace_student(create_default_student())


def test_show_header_displays_stage_7(capsys) -> None:
    cli.show_header()

    assert capsys.readouterr().out == (
        "Project: AI Learning Assistant\n"
        "Current stage: Stage 7\n"
    )


def test_format_agent_suggestion_returns_readable_lines() -> None:
    suggestion = StructuredLearningSuggestion(
        summary="今天练习 Agent 建议入口。",
        suggestions=[
            {
                "title": "接入 Agent",
                "description": "让 CLI 复用结构化 LangChain Agent 能力。",
                "estimated_minutes": 20,
            }
        ],
        next_checkpoint="能说明 CLI 为什么直接调用 Agent 函数。",
    )

    assert cli.format_agent_suggestion(suggestion) == [
        "=== Agent 学习建议 ===",
        "摘要：今天练习 Agent 建议入口。",
        "",
        "行动建议：",
        "1. 接入 Agent（约 20 分钟）",
        "   让 CLI 复用结构化 LangChain Agent 能力。",
        "",
        "下一检查点：能说明 CLI 为什么直接调用 Agent 函数。",
    ]


def test_suggest_with_agent_prints_structured_suggestion(monkeypatch, capsys) -> None:
    cli.student["name"] = "Alice"
    cli.student["goal"] = "学习 LangChain"
    cli.student["python_level"] = "basic"
    cli.student["notes"] = ["LangChain Agent 可以调用工具"]

    suggestion = StructuredLearningSuggestion(
        summary="今天把 CLI 接到 LangChain Agent。",
        suggestions=[
            {
                "title": "调用结构化 Agent",
                "description": "CLI 直接调用 run_structured_learning_agent。",
                "estimated_minutes": 25,
            }
        ],
        next_checkpoint="能说明 Agent 如何读取本地学习档案。",
    )
    saved_students = []

    def fake_save_student(current_student):
        saved_students.append(dict(current_student))

    def fake_run_structured_learning_agent():
        return suggestion

    monkeypatch.setattr(cli, "save_student", fake_save_student)
    monkeypatch.setattr(
        cli,
        "run_structured_learning_agent",
        fake_run_structured_learning_agent,
    )

    cli.suggest_with_agent()

    output = capsys.readouterr().out
    assert saved_students == [dict(cli.student)]
    assert "=== Agent 学习建议 ===" in output
    assert "摘要：今天把 CLI 接到 LangChain Agent。" in output
    assert "1. 调用结构化 Agent（约 25 分钟）" in output
    assert "下一检查点：能说明 Agent 如何读取本地学习档案。" in output


def test_suggest_with_agent_prints_provider_failure(monkeypatch, capsys) -> None:
    def fake_run_structured_learning_agent():
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(cli, "save_student", lambda _student: None)
    monkeypatch.setattr(
        cli,
        "run_structured_learning_agent",
        fake_run_structured_learning_agent,
    )

    cli.suggest_with_agent()

    output = capsys.readouterr().out
    assert "Agent 建议暂不可用。" in output
    assert "原因：AI provider 请求失败。" in output
    assert "你可以先使用选项 3 获取离线规则建议。" in output


def test_suggest_with_agent_prints_openai_provider_failure(monkeypatch, capsys) -> None:
    def fake_run_structured_learning_agent():
        raise OpenAIError("provider failed")

    monkeypatch.setattr(cli, "save_student", lambda _student: None)
    monkeypatch.setattr(
        cli,
        "run_structured_learning_agent",
        fake_run_structured_learning_agent,
    )

    cli.suggest_with_agent()

    output = capsys.readouterr().out
    assert "Agent 建议暂不可用。" in output
    assert "原因：AI provider 请求失败。" in output
    assert "你可以先使用选项 3 获取离线规则建议。" in output


def test_run_cli_routes_choice_3_to_rule_suggestion(monkeypatch, capsys) -> None:
    saved_students = []
    calls = {"rule_suggestion": 0}
    loaded_student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["Rule suggestion remains available"],
    }
    choices = iter(["3", "5"])

    def fake_show_rule_suggestion() -> None:
        calls["rule_suggestion"] += 1
        print("Rule suggestion branch called")

    monkeypatch.setattr(cli, "load_student", lambda: loaded_student)
    monkeypatch.setattr(cli, "save_student", lambda current_student: saved_students.append(dict(current_student)))
    monkeypatch.setattr(cli, "show_rule_suggestion", fake_show_rule_suggestion)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    cli.run_cli()

    output = capsys.readouterr().out
    assert "3. 查看离线规则建议" in output
    assert "Rule suggestion branch called" in output
    assert calls["rule_suggestion"] == 1
    assert saved_students[-1]["name"] == "Alice"


def test_run_cli_routes_choice_4_to_agent_suggestion(monkeypatch, capsys) -> None:
    saved_students = []
    calls = {"agent_suggestion": 0}
    loaded_student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["CLI menu should expose Agent suggestions"],
    }
    choices = iter(["4", "5"])

    def fake_suggest_with_agent() -> None:
        calls["agent_suggestion"] += 1
        print("Agent suggestion branch called")

    monkeypatch.setattr(cli, "load_student", lambda: loaded_student)
    monkeypatch.setattr(cli, "save_student", lambda current_student: saved_students.append(dict(current_student)))
    monkeypatch.setattr(cli, "suggest_with_agent", fake_suggest_with_agent)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    cli.run_cli()

    output = capsys.readouterr().out
    assert "3. 查看离线规则建议" in output
    assert "4. 生成 Agent 学习建议" in output
    assert "5. 退出" in output
    assert "Agent suggestion branch called" in output
    assert calls["agent_suggestion"] == 1
    assert saved_students[-1]["name"] == "Alice"
