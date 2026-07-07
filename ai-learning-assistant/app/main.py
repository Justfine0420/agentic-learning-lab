PROJECT_NAME = "AI Learning Assistant"
COURSE_STAGE = "Stage 1"


def main() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Current stage: {COURSE_STAGE}")

    student_name = input("请输入你的名字：")
    learning_goal = input("请输入你的学习目标：")

    print()
    print("=== 学习档案 ===")
    print(f"名字：{student_name}")
    print(f"目标：{learning_goal}")
    print(f"{student_name}，欢迎开始你的 AI 学习助教项目。")


if __name__ == "__main__":
    main()
