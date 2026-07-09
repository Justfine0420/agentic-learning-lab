from app.langchain_agent import DEFAULT_AGENT_QUESTION, run_learning_agent
from app.storage import load_student


def main() -> None:
    student = load_student()
    answer = run_learning_agent(student, DEFAULT_AGENT_QUESTION)
    print(answer)


if __name__ == "__main__":
    main()
