import json
from pathlib import Path


DATA_FILE = Path("data/student.json")
DEFAULT_STUDENT = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}


def create_default_student() -> dict:
    return {
        "name": DEFAULT_STUDENT["name"],
        "goal": DEFAULT_STUDENT["goal"],
        "python_level": DEFAULT_STUDENT["python_level"],
        "notes": list(DEFAULT_STUDENT["notes"]),
    }


def load_student() -> dict:
    if not DATA_FILE.exists():
        return create_default_student()

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_student(student: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(student, file, ensure_ascii=False, indent=2)
