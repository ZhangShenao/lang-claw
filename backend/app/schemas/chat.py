from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str | None = None
    user_id: str | None = None


class ChatMessage(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class SessionSummary(BaseModel):
    session_id: str
    title: str
    last_message_preview: str
    updated_at: str | None
