from fastapi import APIRouter, Request
from sqlalchemy import text

from app.db.session import get_session_factory

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def healthcheck(request: Request) -> dict:
    mongo_status = "unknown"
    postgres_status = "unknown"

    history_store = request.app.state.history_store
    if history_store.client is not None:
        await history_store.client.admin.command("ping")
        mongo_status = "ok"

    session_factory = get_session_factory()
    async with session_factory() as session:
        await session.execute(text("SELECT 1"))
        postgres_status = "ok"

    return {
        "status": "ok",
        "mongo": mongo_status,
        "postgres": postgres_status,
    }
