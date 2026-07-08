def build_suggestion(python_level: str) -> str:
    if python_level == "beginner":
        return "建议：今天学习变量、函数、字典。"
    if python_level == "basic":
        return "建议：今天学习类、文件读写、异常处理。"
    return "建议：今天开始学习 LangChain 的 agent。"
