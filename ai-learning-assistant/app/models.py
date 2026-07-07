from typing import TypedDict


class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]
