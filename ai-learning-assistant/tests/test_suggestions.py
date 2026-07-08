from app.suggestions import build_suggestion


def test_build_suggestion_for_beginner() -> None:
    assert build_suggestion("beginner") == "建议：今天学习变量、函数、字典。"


def test_build_suggestion_for_basic() -> None:
    assert build_suggestion("basic") == "建议：今天学习类、文件读写、异常处理。"


def test_build_suggestion_for_intermediate() -> None:
    assert build_suggestion("intermediate") == "建议：今天开始学习 LangChain 的 agent。"


def test_build_suggestion_falls_back_to_agent_suggestion() -> None:
    assert build_suggestion("") == "建议：今天开始学习 LangChain 的 agent。"
