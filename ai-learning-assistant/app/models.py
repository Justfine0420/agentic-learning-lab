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


class StudentProfileResponse(BaseModel):
    name: str = ""
    goal: str = ""
    python_level: str = ""
    note_count: int = 0


class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class NotesResponse(BaseModel):
    notes: list[str] = Field(default_factory=list)
    note_count: int = 0


class NoteResponse(BaseModel):
    index: int
    content: str


class SuggestionResponse(BaseModel):
    python_level: str = ""
    suggestion: str
