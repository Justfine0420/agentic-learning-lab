from operator import add
from typing import Annotated, Literal, TypedDict, cast

from app.models import Student


PythonLevel = Literal["beginner", "basic", "intermediate"]
VALID_PYTHON_LEVELS: tuple[PythonLevel, ...] = ("beginner", "basic", "intermediate")
LEVEL_TOPIC_RECOMMENDATIONS: dict[PythonLevel, tuple[str, str]] = {
    "beginner": (
        "python_variables_and_io",
        "你可以先从变量、输入输出和字符串练习开始，先把最小 Python 程序跑顺。",
    ),
    "basic": (
        "python_functions_and_modules",
        "你已经有基础，可以进入函数拆分、模块化和简单测试练习。",
    ),
    "intermediate": (
        "rag_and_agent_integration",
        "你可以开始复盘 RAG、LangChain Agent 和 API 入口如何组合。",
    ),
}


class LearningState(TypedDict):
    student_name: str
    learning_goal: str
    python_level: PythonLevel
    current_topic: str
    lesson_question: str
    learner_answer: str
    is_correct: bool | None
    feedback: str
    material_sources: list[str]
    completed_steps: Annotated[list[str], add]


class LearningStateUpdate(TypedDict, total=False):
    current_topic: str
    lesson_question: str
    learner_answer: str
    is_correct: bool | None
    feedback: str
    material_sources: list[str]
    completed_steps: list[str]


def _validate_python_level(python_level: str) -> PythonLevel:
    if python_level not in VALID_PYTHON_LEVELS:
        raise ValueError("python_level must be beginner, basic, or intermediate")
    return cast(PythonLevel, python_level)


def create_initial_learning_state(
    student: Student,
    *,
    current_topic: str = "python_basics",
) -> LearningState:
    topic = current_topic.strip()
    if topic == "":
        raise ValueError("current_topic must not be empty")

    return {
        "student_name": student["name"],
        "learning_goal": student["goal"],
        "python_level": _validate_python_level(student["python_level"]),
        "current_topic": topic,
        "lesson_question": "",
        "learner_answer": "",
        "is_correct": None,
        "feedback": "",
        "material_sources": [],
        "completed_steps": [],
    }


def assess_level(state: LearningState) -> LearningStateUpdate:
    python_level = _validate_python_level(state["python_level"])
    current_topic, feedback = LEVEL_TOPIC_RECOMMENDATIONS[python_level]

    return {
        "current_topic": current_topic,
        "feedback": feedback,
        "completed_steps": ["assess_level"],
    }
