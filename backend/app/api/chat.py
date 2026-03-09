import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.db.repositories import SessionRepository, UserRepository
from app.db.session import get_session_factory
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def stream_chat(request: Request, payload: ChatRequest) -> StreamingResponse:
    settings = request.app.state.settings
    history_store = request.app.state.history_store
    runtime = request.app.state.agent_runtime

    user_external_id = payload.user_id or settings.default_user_id
    session_factory = get_session_factory()
    async with session_factory() as session:
        user_repo = UserRepository(session)
        session_repo = SessionRepository(session)

        user = await user_repo.get_or_create(user_external_id, display_name=user_external_id)
        session_row = await session_repo.get_or_create(
            user_id=user.id,
            session_id=payload.session_id,
            title_seed=payload.message[:80],
        )
        await session_repo.touch(session_row, payload.message)

    await history_store.append_message(
        session_id=session_row.thread_id,
        thread_id=session_row.thread_id,
        role="user",
        content=payload.message,
        user_id=user.id,
    )

    async def event_generator():
        assistant_chunks: list[str] = []
        yield _sse(
            "session",
            {
                "session_id": session_row.thread_id,
                "thread_id": session_row.thread_id,
                "title": session_row.title,
            },
        )
        try:
            async for chunk in runtime.astream_reply(
                user_id=user.id,
                session_id=session_row.thread_id,
                thread_id=session_row.thread_id,
                message=payload.message,
            ):
                assistant_chunks.append(chunk)
                yield _sse("token", {"content": chunk})
        except Exception as exc:
            yield _sse("error", {"message": str(exc)})
            return

        final_text = "".join(assistant_chunks).strip()
        if not final_text:
            final_text = "抱歉，我暂时没有生成有效回复。"

        await history_store.append_message(
            session_id=session_row.thread_id,
            thread_id=session_row.thread_id,
            role="assistant",
            content=final_text,
            user_id=user.id,
        )

        async with session_factory() as session:
            session_repo = SessionRepository(session)
            refreshed = await session_repo.get_or_create(
                user_id=user.id,
                session_id=session_row.thread_id,
                title_seed=session_row.title,
            )
            await session_repo.touch(refreshed, final_text)

        yield _sse("done", {"content": final_text})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
