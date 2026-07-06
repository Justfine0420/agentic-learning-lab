import platform
import sys


PROJECT_NAME = "AI Learning Assistant"
RECOMMENDED_PYTHON = "3.13"


def main() -> None:
    print(f"Project: {PROJECT_NAME}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {platform.python_version()}")
    print(f"Recommended baseline: Python {RECOMMENDED_PYTHON}")
    print("Status: environment ready")


if __name__ == "__main__":
    main()
