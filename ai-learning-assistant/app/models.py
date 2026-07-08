from typing import TypedDict

from pydantic import BaseModel, Field


class Student(TypedDict):
    name: str
    goal: str
    python_level: str
    notes: list[str]


class StudentProfile(BaseModel):
    name: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    python_level: str = Field(pattern="^(beginner|basic|intermediate)$")


class StudentProfileResponse(StudentProfile):
    note_count: int = 0
