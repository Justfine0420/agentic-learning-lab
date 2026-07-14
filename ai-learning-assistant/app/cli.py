import httpx
from openai import OpenAIError

from app.langchain_agent import run_structured_learning_agent
from app.models import StructuredLearningSuggestion
from app.storage import load_student, save_student
from app.student_state import replace_student, student
from app.suggestions import build_suggestion


PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 6"


def show_header() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")


def ask_profile() -> None:
    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")
    save_student(student)


def add_note() -> None:
    note = input("请输入一条学习笔记：")
    student["notes"].append(note)
    save_student(student)
    print("已保存。")


def show_profile() -> None:
    print()
    print("=== 学习档案 ===")
    print(f"名字：{student['name']}")
    print(f"目标：{student['goal']}")
    print(f"Python 水平：{student['python_level']}")

    print()
    print("=== 学习笔记 ===")
    if len(student["notes"]) == 0:
        print("暂无笔记")
    else:
        for index, saved_note in enumerate(student["notes"], start=1):
            print(f"{index}. {saved_note}")


def show_rule_suggestion() -> None:
    print()
    print("=== 离线规则学习建议 ===")
    print(build_suggestion(student["python_level"]))


def format_agent_suggestion(suggestion: StructuredLearningSuggestion) -> list[str]:
    lines = [
        "=== Agent 学习建议 ===",
        f"摘要：{suggestion.summary}",
        "",
        "行动建议：",
    ]

    for index, item in enumerate(suggestion.suggestions, start=1):
        lines.append(f"{index}. {item.title}（约 {item.estimated_minutes} 分钟）")
        lines.append(f"   {item.description}")

    lines.extend(["", f"下一检查点：{suggestion.next_checkpoint}"])
    return lines


def suggest_with_agent() -> None:
    print()

    try:
        save_student(student)
        suggestion = run_structured_learning_agent()
    except RuntimeError as error:
        print("Agent 建议暂不可用。")
        print(f"原因：{error}")
        print("你可以先使用选项 3 获取离线规则建议。")
    except (httpx.HTTPError, OpenAIError):
        print("Agent 建议暂不可用。")
        print("原因：AI provider 请求失败。")
        print("你可以先使用选项 3 获取离线规则建议。")
    except ValueError as error:
        print("Agent 建议暂不可用。")
        print(f"原因：{error}")
        print("你可以先使用选项 3 获取离线规则建议。")
    else:
        for line in format_agent_suggestion(suggestion):
            print(line)


def run_cli() -> None:
    show_header()
    replace_student(load_student())

    if student["name"] == "":
        ask_profile()
    else:
        print(f"已加载学习档案：{student['name']}")

    while True:
        print()
        print("请选择操作：")
        print("1. 添加学习笔记")
        print("2. 查看学习信息")
        print("3. 查看离线规则建议")
        print("4. 生成 Agent 学习建议")
        print("5. 退出")

        choice = input("输入选项：")

        if choice == "1":
            add_note()
        elif choice == "2":
            show_profile()
        elif choice == "3":
            show_rule_suggestion()
        elif choice == "4":
            suggest_with_agent()
        elif choice == "5":
            save_student(student)
            print(f"{student['name']}，下次继续学习。")
            break
        else:
            print("无效选项，请重新输入。")
