from app.llm import generate_learning_suggestion
from app.storage import load_student


def main() -> None:
    student = load_student()
    suggestion = generate_learning_suggestion(student)
    print(suggestion)


if __name__ == "__main__":
    main()
