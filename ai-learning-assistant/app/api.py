from fastapi import FastAPI

from app.models import StudentProfile, StudentProfileResponse


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
