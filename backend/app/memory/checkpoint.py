from langgraph.checkpoint.mongodb import MongoDBSaver

from app.core.config import Settings


class MongoCheckpointManager:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._context_manager = None
        self.checkpointer = None

    def connect(self) -> None:
        if self.checkpointer is not None:
            return
        self._context_manager = MongoDBSaver.from_conn_string(
            self.settings.mongo_uri,
            db_name=self.settings.mongo_db,
        )
        self.checkpointer = self._context_manager.__enter__()

    def close(self) -> None:
        if self._context_manager is None:
            return
        self._context_manager.__exit__(None, None, None)
        self._context_manager = None
        self.checkpointer = None
