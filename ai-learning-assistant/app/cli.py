from app.student_state import student


PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 2"


def show_header() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")


def ask_profile() -> None:
    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")


def add_note() -> None:
    note = input("请输入一条学习笔记：")
    student["notes"].append(note)
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


def suggest_next_step() -> None:
    print()
    print("=== 今日学习建议 ===")

    if student["python_level"] == "beginner":
        print("建议：今天学习变量、函数、字典。")
    elif student["python_level"] == "basic":
        print("建议：今天学习类、文件读写、异常处理。")
    else:
        print("建议：今天开始学习 LangChain 的 agent。")


def run_cli() -> None:
    show_header()
    ask_profile()

    while True:
        print()
        print("请选择操作：")
        print("1. 添加学习笔记")
        print("2. 查看学习信息")
        print("3. 生成今日学习建议")
        print("4. 退出")

        choice = input("输入选项：")

        if choice == "1":
            add_note()
        elif choice == "2":
            show_profile()
        elif choice == "3":
            suggest_next_step()
        elif choice == "4":
            print(f"{student['name']}，下次继续学习。")
            break
        else:
            print("无效选项，请重新输入。")
