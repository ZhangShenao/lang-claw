from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.runtime import AgentRuntime
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.init_db import init_database
from app.db.session import close_db, init_db
from app.memory.checkpoint import MongoCheckpointManager
from app.memory.history import MongoChatHistoryStore
from app.observability.langsmith import configure_langsmith


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings)
    configure_langsmith(settings)

    await init_db(settings)
    await init_database()

    history_store = MongoChatHistoryStore(settings)
    await history_store.connect()

    checkpoint_manager = MongoCheckpointManager(settings)
    checkpoint_manager.connect()

    app.state.settings = settings
    app.state.history_store = history_store
    app.state.checkpoint_manager = checkpoint_manager
    app.state.agent_runtime = AgentRuntime(
        settings=settings,
        checkpointer=checkpoint_manager.checkpointer,
    )

    try:
        yield
    finally:
        await history_store.close()
        checkpoint_manager.close()
        await close_db()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(sessions_router)
    return app


app = create_app()
