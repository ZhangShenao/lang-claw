from fastapi import APIRouter, HTTPException, Request

from app.db.repositories import SessionRepository, UserRepository
from app.db.session import get_session_factory
from app.schemas.chat import ChatMessage, SessionSummary

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionSummary])
async def list_sessions(request: Request, user_id: str | None = None):
    settings = request.app.state.settings
    session_factory = get_session_factory()
    resolved_user_id = user_id or settings.default_user_id

    async with session_factory() as session:
        user_repo = UserRepository(session)
        session_repo = SessionRepository(session)
        user = await user_repo.get_or_create(resolved_user_id, display_name=resolved_user_id)
        sessions = await session_repo.list_for_user(user.id)

    return [
        SessionSummary(
            session_id=item.thread_id,
            title=item.title,
            last_message_preview=item.last_message_preview,
            updated_at=item.updated_at.isoformat() if item.updated_at else None,
        )
        for item in sessions
    ]


@router.get("/{session_id}/messages", response_model=list[ChatMessage])
async def list_session_messages(request: Request, session_id: str):
    history_store = request.app.state.history_store
    messages = await history_store.list_messages(session_id)
    if not messages:
        return []
    return [ChatMessage.model_validate(message) for message in messages]
