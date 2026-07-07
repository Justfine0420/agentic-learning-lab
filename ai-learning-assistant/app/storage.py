import json
from pathlib import Path

from app.models import Student

DATA_FILE = Path("data/student.json")
BROKEN_DATA_FILE = Path("data/student.broken.json")
DEFAULT_STUDENT: Student = {
    "name": "",
    "goal": "",
    "python_level": "",
    "notes": [],
}


def create_default_student() -> Student:
    return {
        "name": DEFAULT_STUDENT["name"],
        "goal": DEFAULT_STUDENT["goal"],
        "python_level": DEFAULT_STUDENT["python_level"],
        "notes": list(DEFAULT_STUDENT["notes"]),
    }


def is_valid_student(data: object) -> bool:
    if not isinstance(data, dict):
        return False

    required_keys = ("name", "goal", "python_level", "notes")
    if not all(key in data for key in required_keys):
        return False

    return (
        isinstance(data["name"], str)
        and isinstance(data["goal"], str)
        and isinstance(data["python_level"], str)
        and isinstance(data["notes"], list)
        and all(isinstance(note, str) for note in data["notes"])
    )


def normalize_student(data: object) -> Student:
    if not isinstance(data, dict):
        return create_default_student()

    student = create_default_student()

    if isinstance(data.get("name"), str):
        student["name"] = data["name"]
    if isinstance(data.get("goal"), str):
        student["goal"] = data["goal"]
    if isinstance(data.get("python_level"), str):
        student["python_level"] = data["python_level"]
    if isinstance(data.get("notes"), list):
        student["notes"] = [note for note in data["notes"] if isinstance(note, str)]

    return student


def backup_broken_data() -> None:
    if DATA_FILE.exists():
        DATA_FILE.replace(BROKEN_DATA_FILE)


def load_student() -> Student:
    if not DATA_FILE.exists():
        return create_default_student()

    try:
        with DATA_FILE.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        backup_broken_data()
        return create_default_student()
    except OSError:
        return create_default_student()

    if is_valid_student(data):
        return data

    return normalize_student(data)


def save_student(student: Student) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(student, file, ensure_ascii=False, indent=2)
