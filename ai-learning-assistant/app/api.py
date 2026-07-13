import httpx
from fastapi import FastAPI, HTTPException
from openai import OpenAIError

from app.langchain_agent import run_structured_learning_agent
from app.llm import generate_structured_learning_suggestion
from app.models import (
    AISuggestionResponse,
    AgentChatResponse,
    ChatRequest,
    NoteCreate,
    NoteResponse,
    NotesResponse,
    Student,
    StudentProfile,
    StudentProfileResponse,
    SuggestionResponse,
)
from app.storage import load_student, save_student
from app.suggestions import build_suggestion


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


@app.get("/notes/{note_index}", response_model=NoteResponse)
def get_note(note_index: int) -> NoteResponse:
    student = load_student()
    notes = student["notes"]

    if note_index < 1 or note_index > len(notes):
        raise HTTPException(status_code=404, detail="学习笔记不存在。")

    return NoteResponse(index=note_index, content=notes[note_index - 1])


@app.post("/notes", response_model=NotesResponse)
def add_note(note: NoteCreate) -> NotesResponse:
    if note.content.strip() == "":
        raise HTTPException(status_code=400, detail="学习笔记不能为空。")

    student = load_student()
    student["notes"].append(note.content)
    save_student(student)

    return NotesResponse(
        notes=student["notes"],
        note_count=len(student["notes"]),
    )


@app.get("/suggestion", response_model=SuggestionResponse)
def get_suggestion() -> SuggestionResponse:
    student = load_student()

    return SuggestionResponse(
        python_level=student["python_level"],
        suggestion=build_suggestion(student["python_level"]),
    )


@app.post("/ai/suggestion", response_model=AISuggestionResponse)
def generate_ai_suggestion() -> AISuggestionResponse:
    student = load_student()

    try:
        suggestion = generate_structured_learning_suggestion(student)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=503, detail="AI provider request failed.") from error
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return AISuggestionResponse(suggestion=suggestion)


@app.post(
    "/chat",
    response_model=AgentChatResponse,
    responses={
        400: {"description": "问题不能为空。"},
        503: {"description": "Agent provider 或结构化结果不可用。"},
    },
)
def chat_with_learning_agent(chat: ChatRequest) -> AgentChatResponse:
    question = chat.question.strip()
    if question == "":
        raise HTTPException(status_code=400, detail="问题不能为空。")

    try:
        suggestion = run_structured_learning_agent(question)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (httpx.HTTPError, OpenAIError) as error:
        raise HTTPException(status_code=503, detail="AI provider request failed.") from error
    except ValueError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return AgentChatResponse(suggestion=suggestion)
