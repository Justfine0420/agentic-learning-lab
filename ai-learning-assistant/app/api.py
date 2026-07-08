from fastapi import FastAPI

from app.models import (
    NoteCreate,
    NotesResponse,
    Student,
    StudentProfile,
    StudentProfileResponse,
)
from app.storage import load_student, save_student


app = FastAPI(title="AI Learning Assistant")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "ai-learning-assistant",
    }


@app.post("/profile/preview", response_model=StudentProfileResponse)
def preview_profile(profile: StudentProfile) -> StudentProfileResponse:
    return StudentProfileResponse(**profile.model_dump(), note_count=0)


@app.get("/profile", response_model=StudentProfileResponse)
def get_profile() -> StudentProfileResponse:
    student = load_student()

    return StudentProfileResponse(
        name=student["name"],
        goal=student["goal"],
        python_level=student["python_level"],
        note_count=len(student["notes"]),
    )


@app.post("/profile", response_model=StudentProfileResponse)
def update_profile(profile: StudentProfile) -> StudentProfileResponse:
    current_student = load_student()
    updated_student: Student = {
        "name": profile.name,
        "goal": profile.goal,
        "python_level": profile.python_level,
        "notes": current_student["notes"],
    }
    save_student(updated_student)

    return StudentProfileResponse(
        name=updated_student["name"],
        goal=updated_student["goal"],
        python_level=updated_student["python_level"],
        note_count=len(updated_student["notes"]),
    )


@app.get("/notes", response_model=NotesResponse)
def get_notes() -> NotesResponse:
    student = load_student()

    return NotesResponse(
        notes=student["notes"],
        note_count=len(student["notes"]),
    )


@app.post("/notes", response_model=NotesResponse)
def add_note(note: NoteCreate) -> NotesResponse:
    student = load_student()
    student["notes"].append(note.content)
    save_student(student)

    return NotesResponse(
        notes=student["notes"],
        note_count=len(student["notes"]),
    )
