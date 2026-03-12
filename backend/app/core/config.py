import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        enable_decoding=False,
    )

    app_name: str = "Lang Claw Backend"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    default_user_id: str = "local-user"

    zhipu_api_key: str = ""
    zhipu_base_url: str = "https://open.bigmodel.cn/api/paas/v4/"
    llm_model: str = "glm-5"
    llm_temperature: float = 0.2

    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db: str = "lang_claw"
    mongo_history_collection: str = "chat_history"

    postgres_dsn: str = (
        "postgresql+asyncpg://langclaw:langclaw@postgres:5432/lang_claw"
    )

    langsmith_api_key: str = ""
    langsmith_project: str = "lang-claw"
    langsmith_tracing: bool = True
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    tavily_api_key: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            raw = value.strip()
            if raw.startswith("["):
                parsed = json.loads(raw)
                return [str(item).strip() for item in parsed if str(item).strip()]
            parts = [item.strip() for item in value.split(",")]
            return [item for item in parts if item]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
