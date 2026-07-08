from app.llm import generate_structured_learning_suggestion
from app.storage import load_student


def main() -> None:
    student = load_student()
    suggestion = generate_structured_learning_suggestion(student)
    print(suggestion.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
