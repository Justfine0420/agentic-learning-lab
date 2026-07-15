from operator import add
from typing import get_args, get_origin, get_type_hints

import pytest

from app.graph import LearningState, LearningStateUpdate, create_initial_learning_state
from app.storage import create_default_student


def test_create_initial_learning_state_maps_student_fields() -> None:
    student = create_default_student()
    student["name"] = "Alice"
    student["goal"] = "学习 LangGraph"
    student["python_level"] = "basic"

    state = create_initial_learning_state(student, current_topic="state_graph")

    assert state == {
        "student_name": "Alice",
        "learning_goal": "学习 LangGraph",
        "python_level": "basic",
        "current_topic": "state_graph",
        "lesson_question": "",
        "learner_answer": "",
        "is_correct": None,
        "feedback": "",
        "material_sources": [],
        "completed_steps": [],
    }


def test_create_initial_learning_state_rejects_blank_topic() -> None:
    with pytest.raises(ValueError, match="current_topic must not be empty"):
        create_initial_learning_state(create_default_student(), current_topic="   ")


def test_create_initial_learning_state_rejects_unknown_python_level() -> None:
    student = create_default_student()
    student["python_level"] = "advanced"

    with pytest.raises(ValueError, match="python_level must be beginner"):
        create_initial_learning_state(student)


def test_learning_state_marks_completed_steps_with_add_reducer() -> None:
    hints = get_type_hints(LearningState, include_extras=True)

    completed_steps_hint = hints["completed_steps"]

    assert get_origin(completed_steps_hint) is not None
    assert add in get_args(completed_steps_hint)


def test_learning_state_update_can_represent_partial_node_output() -> None:
    update: LearningStateUpdate = {
        "feedback": "答对了，下一步进入函数练习。",
        "completed_steps": ["grade_answer"],
    }

    assert update["feedback"] == "答对了，下一步进入函数练习。"
    assert update["completed_steps"] == ["grade_answer"]
