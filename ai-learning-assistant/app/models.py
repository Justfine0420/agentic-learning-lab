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


class LearningSuggestionItem(BaseModel):
    title: str = Field(min_length=1, description="学习建议标题")
    description: str = Field(min_length=1, description="具体要做什么")
    estimated_minutes: int = Field(ge=5, le=180, description="预计学习分钟数")


class StructuredLearningSuggestion(BaseModel):
    summary: str = Field(min_length=1, description="今日学习建议摘要")
    suggestions: list[LearningSuggestionItem] = Field(
        min_length=1,
        max_length=3,
        description="1 到 3 条可执行学习建议",
    )
    next_checkpoint: str = Field(min_length=1, description="下一次学习前要确认的检查点")


class AISuggestionResponse(BaseModel):
    source: str = "ai"
    suggestion: StructuredLearningSuggestion


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, description="学员希望向学习助教提出的问题")


class AgentChatResponse(BaseModel):
    source: str = "agent"
    suggestion: StructuredLearningSuggestion


class AskMaterialsRequest(BaseModel):
    question: str = Field(min_length=1, description="学员希望基于本地学习资料提出的问题")
    k: int = Field(default=3, ge=1, le=10, description="用于回答的候选资料片段数量")


class MaterialAnswer(BaseModel):
    answer: str = Field(min_length=1, description="基于学习资料生成的回答")
    sources: list[str] = Field(default_factory=list, description="回答引用的资料来源路径")
