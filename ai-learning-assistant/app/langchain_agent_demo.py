from app.langchain_agent import DEFAULT_AGENT_QUESTION, run_learning_agent


def main() -> None:
    answer = run_learning_agent(DEFAULT_AGENT_QUESTION)
    print(answer)


if __name__ == "__main__":
    main()
