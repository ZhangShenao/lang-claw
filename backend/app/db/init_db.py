from app.db.base import Base
from app.db import session as db_session


async def init_database() -> None:
    if db_session.engine is None:
        raise RuntimeError("Database engine is not initialized.")

    async with db_session.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
