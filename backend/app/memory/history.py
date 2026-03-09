from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from app.core.config import Settings


class MongoChatHistoryStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client: AsyncIOMotorClient | None = None
        self.collection: AsyncIOMotorCollection | None = None

    async def connect(self) -> None:
        if self.collection is not None:
            return

        self.client = AsyncIOMotorClient(self.settings.mongo_uri)
        database = self.client[self.settings.mongo_db]
        self.collection = database[self.settings.mongo_history_collection]
        await self.collection.create_index("session_id")
        await self.collection.create_index("thread_id")
        await self.collection.create_index("created_at")

    async def close(self) -> None:
        if self.client is not None:
            self.client.close()
        self.client = None
        self.collection = None

    async def append_message(
        self,
        *,
        session_id: str,
        thread_id: str,
        role: str,
        content: str,
        user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        if self.collection is None:
            raise RuntimeError("Mongo history collection is not initialized.")

        message_id = str(uuid4())
        await self.collection.insert_one(
            {
                "_id": message_id,
                "session_id": session_id,
                "thread_id": thread_id,
                "user_id": user_id,
                "role": role,
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.now(timezone.utc),
            }
        )
        return message_id

    async def list_messages(self, session_id: str) -> list[dict[str, Any]]:
        if self.collection is None:
            raise RuntimeError("Mongo history collection is not initialized.")

        cursor = self.collection.find({"session_id": session_id}).sort("created_at", 1)
        documents = await cursor.to_list(length=500)
        return [
            {
                "id": document["_id"],
                "role": document["role"],
                "content": document["content"],
                "created_at": document["created_at"].isoformat(),
            }
            for document in documents
        ]
