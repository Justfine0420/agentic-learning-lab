PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 1"

student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}


def main() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")

    student["name"] = input("请输入你的名字：")
    student["goal"] = input("请输入你的学习目标：")
    student["python_level"] = input("请输入你的 Python 水平 beginner / basic / intermediate：")
    note = input("请输入一条学习笔记：")
    student["notes"].append(note)

    print()
    print("=== 学习档案 ===")
    print(f"名字：{student['name']}")
    print(f"目标：{student['goal']}")
    print(f"Python 水平：{student['python_level']}")

    print()
    print("=== 学习笔记 ===")
    for index, saved_note in enumerate(student["notes"], start=1):
        print(f"{index}. {saved_note}")

    print(f"{student['name']}，欢迎开始你的 AI 学习助教项目。")


if __name__ == "__main__":
    main()
