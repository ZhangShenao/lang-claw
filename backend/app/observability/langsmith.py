import os

from app.core.config import Settings


def configure_langsmith(settings: Settings) -> None:
    if not settings.langsmith_api_key:
        return

    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGSMITH_TRACING"] = "true" if settings.langsmith_tracing else "false"


def build_run_config(
    *,
    thread_id: str,
    user_id: str,
    session_id: str,
    model_name: str,
) -> dict:
    return {
        "run_name": "lang-claw-chat",
        "tags": ["lang-claw", "web-chat"],
        "metadata": {
            "thread_id": thread_id,
            "user_id": user_id,
            "session_id": session_id,
            "model": model_name,
        },
        "configurable": {
            "thread_id": thread_id,
        },
    }
