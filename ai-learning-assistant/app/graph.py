from operator import add
from typing import Annotated, Literal, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from app.models import Student


PythonLevel = Literal["beginner", "basic", "intermediate"]
AnswerRoute = Literal["recommend_next_topic", "review_current_topic"]
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
TOPIC_LESSONS: dict[str, str] = {
    "python_variables_and_io": (
        "变量可以给数据起名字，输入输出让程序和使用者交换信息。"
        "先把小程序的输入、保存和打印跑通，再进入更大的结构。"
    ),
    "python_functions_and_modules": (
        "函数把一段可复用逻辑收进一个名字里，模块把相关函数放到独立文件。"
        "这样代码更容易测试、复用和继续扩展。"
    ),
    "rag_and_agent_integration": (
        "RAG 先检索资料，再把资料片段交给模型生成有来源的回答。"
        "Agent 可以把资料读取、检索和回答组织成可调用工具。"
    ),
}
TOPIC_QUESTIONS: dict[str, str] = {
    "python_variables_and_io": "变量主要帮我们解决什么问题？",
    "python_functions_and_modules": "函数为什么能让代码更容易维护？",
    "rag_and_agent_integration": "RAG 回答为什么需要保留 sources？",
}
TOPIC_ANSWER_KEYWORDS: dict[str, tuple[str, ...]] = {
    "python_variables_and_io": ("保存", "数据", "值", "名字"),
    "python_functions_and_modules": ("复用", "拆分", "维护", "测试"),
    "rag_and_agent_integration": ("来源", "证据", "追溯", "溯源", "资料", "source", "sources"),
}
NEXT_TOPIC_HINTS: dict[str, str] = {
    "python_variables_and_io": "下一步可以练习把输入、变量和打印组合成一个小脚本。",
    "python_functions_and_modules": "下一步可以练习把重复逻辑拆成函数，并把函数放进独立模块。",
    "rag_and_agent_integration": "下一步可以练习把检索、引用 sources 和回答生成串成一个稳定流程。",
}
REVIEW_TOPIC_HINTS: dict[str, str] = {
    "python_variables_and_io": "先回看变量如何给数据命名，再用自己的话解释变量保存了什么。",
    "python_functions_and_modules": "先回看函数的复用、拆分和测试价值，再重新回答维护性问题。",
    "rag_and_agent_integration": "先回看 sources 如何支撑证据追溯，再重新说明为什么不能丢来源。",
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


def _get_topic(state: LearningState) -> str:
    topic = state["current_topic"].strip()
    if topic not in TOPIC_LESSONS:
        raise ValueError("current_topic is not supported")
    return topic


def teach_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": TOPIC_LESSONS[topic],
        "completed_steps": ["teach_topic"],
    }


def ask_question(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "lesson_question": TOPIC_QUESTIONS[topic],
        "completed_steps": ["ask_question"],
    }


def grade_answer(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)
    answer = state["learner_answer"].strip().lower()
    keywords = TOPIC_ANSWER_KEYWORDS[topic]
    is_correct = answer != "" and any(keyword in answer for keyword in keywords)
    if is_correct:
        feedback = "回答抓住了关键点，可以进入下一步练习。"
    else:
        question = state["lesson_question"] or TOPIC_QUESTIONS[topic]
        feedback = f"这次还没有命中关键点，可以围绕这个问题重答：{question}"

    return {
        "is_correct": is_correct,
        "feedback": feedback,
        "completed_steps": ["grade_answer"],
    }


def route_by_answer(state: LearningState) -> AnswerRoute:
    if state["is_correct"] is True:
        return "recommend_next_topic"
    if state["is_correct"] is False:
        return "review_current_topic"
    raise ValueError("is_correct must be set before routing")


def recommend_next_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": NEXT_TOPIC_HINTS[topic],
        "completed_steps": ["recommend_next_topic"],
    }


def review_current_topic(state: LearningState) -> LearningStateUpdate:
    topic = _get_topic(state)

    return {
        "feedback": REVIEW_TOPIC_HINTS[topic],
        "completed_steps": ["review_current_topic"],
    }


def create_basic_learning_graph():
    builder = StateGraph(LearningState)
    builder.add_node("assess_level", assess_level)
    builder.add_node("teach_topic", teach_topic)
    builder.add_node("ask_question", ask_question)
    builder.add_node("grade_answer", grade_answer)

    builder.add_edge(START, "assess_level")
    builder.add_edge("assess_level", "teach_topic")
    builder.add_edge("teach_topic", "ask_question")
    builder.add_edge("ask_question", "grade_answer")
    builder.add_edge("grade_answer", END)

    return builder.compile()


def create_branching_learning_graph():
    builder = StateGraph(LearningState)
    builder.add_node("assess_level", assess_level)
    builder.add_node("teach_topic", teach_topic)
    builder.add_node("ask_question", ask_question)
    builder.add_node("grade_answer", grade_answer)
    builder.add_node("recommend_next_topic", recommend_next_topic)
    builder.add_node("review_current_topic", review_current_topic)

    builder.add_edge(START, "assess_level")
    builder.add_edge("assess_level", "teach_topic")
    builder.add_edge("teach_topic", "ask_question")
    builder.add_edge("ask_question", "grade_answer")
    builder.add_conditional_edges(
        "grade_answer",
        route_by_answer,
        {
            "recommend_next_topic": "recommend_next_topic",
            "review_current_topic": "review_current_topic",
        },
    )
    builder.add_edge("recommend_next_topic", END)
    builder.add_edge("review_current_topic", END)

    return builder.compile()
