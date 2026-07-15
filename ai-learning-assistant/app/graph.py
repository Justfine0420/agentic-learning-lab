from operator import add
from typing import Annotated, Literal, TypedDict, cast

from app.models import Student


PythonLevel = Literal["beginner", "basic", "intermediate"]
VALID_PYTHON_LEVELS: tuple[PythonLevel, ...] = ("beginner", "basic", "intermediate")


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
