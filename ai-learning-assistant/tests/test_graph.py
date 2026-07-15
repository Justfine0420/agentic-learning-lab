from operator import add
from typing import get_args, get_origin, get_type_hints

import pytest

from app.graph import (
    LearningState,
    LearningStateUpdate,
    ask_question,
    assess_level,
    create_basic_learning_graph,
    create_branching_learning_graph,
    create_initial_learning_state,
    grade_answer,
    recommend_next_topic,
    review_current_topic,
    route_by_answer,
    teach_topic,
)
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


@pytest.mark.parametrize(
    ("python_level", "expected_topic"),
    [
        ("beginner", "python_variables_and_io"),
        ("basic", "python_functions_and_modules"),
        ("intermediate", "rag_and_agent_integration"),
    ],
)
def test_assess_level_recommends_topic_for_python_level(
    python_level: str,
    expected_topic: str,
) -> None:
    student = create_default_student()
    student["python_level"] = python_level
    state = create_initial_learning_state(student)

    update = assess_level(state)

    assert update["current_topic"] == expected_topic
    assert update["feedback"] != ""
    assert update["completed_steps"] == ["assess_level"]


def test_assess_level_does_not_mutate_state() -> None:
    student = create_default_student()
    student["python_level"] = "beginner"
    state = create_initial_learning_state(student)

    update = assess_level(state)

    assert state["current_topic"] == "python_basics"
    assert state["completed_steps"] == []
    assert update["completed_steps"] == ["assess_level"]


def test_assess_level_rejects_unknown_python_level() -> None:
    student = create_default_student()
    student["python_level"] = "beginner"
    state = create_initial_learning_state(student)
    state["python_level"] = "advanced"  # type: ignore[typeddict-item]

    with pytest.raises(ValueError, match="python_level must be beginner"):
        assess_level(state)


def test_teach_topic_returns_topic_feedback() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(
        student,
        current_topic="python_functions_and_modules",
    )

    update = teach_topic(state)

    assert "函数" in update["feedback"]
    assert update["completed_steps"] == ["teach_topic"]


def test_ask_question_returns_topic_question() -> None:
    student = create_default_student()
    student["python_level"] = "intermediate"
    state = create_initial_learning_state(
        student,
        current_topic="rag_and_agent_integration",
    )

    update = ask_question(state)

    assert "sources" in update["lesson_question"]
    assert update["completed_steps"] == ["ask_question"]


def test_grade_answer_marks_correct_answer() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(
        student,
        current_topic="python_functions_and_modules",
    )
    state["lesson_question"] = "函数为什么能让代码更容易维护？"
    state["learner_answer"] = "函数可以复用逻辑，也方便拆分测试。"

    update = grade_answer(state)

    assert update["is_correct"] is True
    assert update["completed_steps"] == ["grade_answer"]


def test_grade_answer_marks_incorrect_answer() -> None:
    student = create_default_student()
    student["python_level"] = "intermediate"
    state = create_initial_learning_state(
        student,
        current_topic="rag_and_agent_integration",
    )
    state["lesson_question"] = "RAG 回答为什么需要保留 sources？"
    state["learner_answer"] = "因为这样比较好看。"

    update = grade_answer(state)

    assert update["is_correct"] is False
    assert "RAG 回答为什么需要保留 sources" in update["feedback"]
    assert update["completed_steps"] == ["grade_answer"]


def test_grade_answer_accepts_sources_keyword_for_rag_topic() -> None:
    student = create_default_student()
    student["python_level"] = "intermediate"
    state = create_initial_learning_state(
        student,
        current_topic="rag_and_agent_integration",
    )
    state["lesson_question"] = "RAG 回答为什么需要保留 sources？"
    state["learner_answer"] = "sources 可以让回答方便溯源。"

    update = grade_answer(state)

    assert update["is_correct"] is True


def test_route_by_answer_sends_correct_answer_to_next_topic() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(student)
    state["is_correct"] = True

    route = route_by_answer(state)

    assert route == "recommend_next_topic"


def test_route_by_answer_sends_wrong_answer_to_review() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(student)
    state["is_correct"] = False

    route = route_by_answer(state)

    assert route == "review_current_topic"


def test_route_by_answer_rejects_missing_grade_result() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(student)

    with pytest.raises(ValueError, match="is_correct must be set before routing"):
        route_by_answer(state)


def test_recommend_next_topic_returns_next_step_feedback() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(
        student,
        current_topic="python_functions_and_modules",
    )

    update = recommend_next_topic(state)

    assert "拆成函数" in update["feedback"]
    assert update["completed_steps"] == ["recommend_next_topic"]


def test_review_current_topic_returns_review_feedback() -> None:
    student = create_default_student()
    student["python_level"] = "intermediate"
    state = create_initial_learning_state(
        student,
        current_topic="rag_and_agent_integration",
    )

    update = review_current_topic(state)

    assert "sources" in update["feedback"]
    assert update["completed_steps"] == ["review_current_topic"]


def test_graph_runs_fixed_multi_node_flow() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(student)
    state["learner_answer"] = "函数可以复用逻辑，也能拆分代码。"

    graph = create_basic_learning_graph()
    result = graph.invoke(state)

    assert result["current_topic"] == "python_functions_and_modules"
    assert result["lesson_question"] == "函数为什么能让代码更容易维护？"
    assert result["is_correct"] is True
    assert result["completed_steps"] == [
        "assess_level",
        "teach_topic",
        "ask_question",
        "grade_answer",
    ]


def test_branching_graph_takes_correct_path() -> None:
    student = create_default_student()
    student["python_level"] = "basic"
    state = create_initial_learning_state(student)
    state["learner_answer"] = "函数可以复用逻辑，也能拆分代码。"

    graph = create_branching_learning_graph()
    result = graph.invoke(state)

    assert result["is_correct"] is True
    assert result["feedback"] == "下一步可以练习把重复逻辑拆成函数，并把函数放进独立模块。"
    assert result["completed_steps"] == [
        "assess_level",
        "teach_topic",
        "ask_question",
        "grade_answer",
        "recommend_next_topic",
    ]


def test_branching_graph_takes_incorrect_path() -> None:
    student = create_default_student()
    student["python_level"] = "intermediate"
    state = create_initial_learning_state(student)
    state["learner_answer"] = "因为这样比较好看。"

    graph = create_branching_learning_graph()
    result = graph.invoke(state)

    assert result["is_correct"] is False
    assert result["feedback"] == "先回看 sources 如何支撑证据追溯，再重新说明为什么不能丢来源。"
    assert result["completed_steps"] == [
        "assess_level",
        "teach_topic",
        "ask_question",
        "grade_answer",
        "review_current_topic",
    ]


def test_graph_rejects_unsupported_topic_from_node() -> None:
    student = create_default_student()
    student["python_level"] = "beginner"
    state = create_initial_learning_state(student, current_topic="unknown_topic")

    with pytest.raises(ValueError, match="current_topic is not supported"):
        teach_topic(state)
