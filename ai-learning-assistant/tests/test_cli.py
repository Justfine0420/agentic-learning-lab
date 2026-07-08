import httpx
import pytest

from app import cli
from app.models import StructuredLearningSuggestion
from app.storage import create_default_student


@pytest.fixture(autouse=True)
def reset_cli_student() -> None:
    cli.replace_student(create_default_student())


def test_format_ai_suggestion_returns_readable_lines() -> None:
    suggestion = StructuredLearningSuggestion(
        summary="今天练习 AI 建议入口。",
        suggestions=[
            {
                "title": "补 CLI 入口",
                "description": "让 CLI 复用结构化 AI 建议能力。",
                "estimated_minutes": 20,
            }
        ],
        next_checkpoint="能说明 CLI 为什么不需要 HTTP 调本地 API。",
    )

    assert cli.format_ai_suggestion(suggestion) == [
        "=== AI 学习建议 ===",
        "摘要：今天练习 AI 建议入口。",
        "",
        "行动建议：",
        "1. 补 CLI 入口（约 20 分钟）",
        "   让 CLI 复用结构化 AI 建议能力。",
        "",
        "下一检查点：能说明 CLI 为什么不需要 HTTP 调本地 API。",
    ]


def test_suggest_with_ai_prints_structured_suggestion(monkeypatch, capsys) -> None:
    cli.student["name"] = "Alice"
    cli.student["goal"] = "学习 LangChain"
    cli.student["python_level"] = "basic"
    cli.student["notes"] = ["FastAPI route 可以复用 service 函数"]

    suggestion = StructuredLearningSuggestion(
        summary="今天把 CLI 和 API 能力对齐。",
        suggestions=[
            {
                "title": "复用 LLM 函数",
                "description": "CLI 直接调用 generate_structured_learning_suggestion。",
                "estimated_minutes": 25,
            }
        ],
        next_checkpoint="能区分 API route 和业务函数。",
    )

    def fake_generate_structured_learning_suggestion(loaded_student):
        assert loaded_student == cli.student
        return suggestion

    monkeypatch.setattr(
        cli,
        "generate_structured_learning_suggestion",
        fake_generate_structured_learning_suggestion,
    )

    cli.suggest_with_ai()

    output = capsys.readouterr().out
    assert "=== AI 学习建议 ===" in output
    assert "摘要：今天把 CLI 和 API 能力对齐。" in output
    assert "1. 复用 LLM 函数（约 25 分钟）" in output
    assert "下一检查点：能区分 API route 和业务函数。" in output


def test_suggest_with_ai_prints_provider_failure(monkeypatch, capsys) -> None:
    def fake_generate_structured_learning_suggestion(_student):
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(
        cli,
        "generate_structured_learning_suggestion",
        fake_generate_structured_learning_suggestion,
    )

    cli.suggest_with_ai()

    output = capsys.readouterr().out
    assert "AI 建议暂不可用。" in output
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


def test_run_cli_routes_choice_4_to_ai_suggestion(monkeypatch, capsys) -> None:
    saved_students = []
    calls = {"ai_suggestion": 0}
    loaded_student = {
        "name": "Alice",
        "goal": "学习 LangChain",
        "python_level": "basic",
        "notes": ["CLI menu should expose AI suggestions"],
    }
    choices = iter(["4", "5"])

    def fake_suggest_with_ai() -> None:
        calls["ai_suggestion"] += 1
        print("AI suggestion branch called")

    monkeypatch.setattr(cli, "load_student", lambda: loaded_student)
    monkeypatch.setattr(cli, "save_student", lambda current_student: saved_students.append(dict(current_student)))
    monkeypatch.setattr(cli, "suggest_with_ai", fake_suggest_with_ai)
    monkeypatch.setattr("builtins.input", lambda _prompt: next(choices))

    cli.run_cli()

    output = capsys.readouterr().out
    assert "3. 查看离线规则建议" in output
    assert "4. 生成 AI 学习建议" in output
    assert "5. 退出" in output
    assert "AI suggestion branch called" in output
    assert calls["ai_suggestion"] == 1
    assert saved_students[-1]["name"] == "Alice"
