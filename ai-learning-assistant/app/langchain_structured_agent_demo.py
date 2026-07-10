from app.langchain_agent import DEFAULT_AGENT_QUESTION, run_structured_learning_agent


def main() -> None:
    suggestion = run_structured_learning_agent(DEFAULT_AGENT_QUESTION)
    print(suggestion.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
