from datetime import datetime

from langchain_core.tools import tool

from app.db.repositories import ProfileRepository, TaskRepository
from app.db.session import get_session_factory


def build_personal_tools(user_id: str) -> list:
    session_factory = get_session_factory()

    @tool
    async def get_profile_summary() -> dict:
        """Return the current user's saved profile and preferences."""
        async with session_factory() as session:
            repo = ProfileRepository(session)
            profile = await repo.get_or_create(user_id)
            return {
                "bio": profile.bio,
                "preferences": profile.preferences,
            }

    @tool
    async def remember_preference(key: str, value: str) -> dict:
        """Store a user preference for future use."""
        async with session_factory() as session:
            repo = ProfileRepository(session)
            profile = await repo.remember_preference(user_id, key, value)
            return {
                "stored": True,
                "preferences": profile.preferences,
            }

    @tool
    async def create_task(title: str, details: str = "", due_at_iso: str = "") -> dict:
        """Create a task for the current user."""
        due_at = datetime.fromisoformat(due_at_iso) if due_at_iso else None
        async with session_factory() as session:
            repo = TaskRepository(session)
            task = await repo.create(
                user_id=user_id,
                title=title,
                details=details,
                due_at=due_at,
            )
            return {
                "task_id": task.id,
                "title": task.title,
                "status": task.status,
            }

    @tool
    async def list_tasks(status: str = "open") -> list[dict]:
        """List tasks for the current user."""
        async with session_factory() as session:
            repo = TaskRepository(session)
            tasks = await repo.list_for_user(user_id, status=status)
            return [
                {
                    "task_id": task.id,
                    "title": task.title,
                    "details": task.details,
                    "status": task.status,
                    "due_at": task.due_at.isoformat() if task.due_at else None,
                }
                for task in tasks
            ]

    @tool
    def get_current_time() -> dict:
        """Return the current UTC time."""
        return {"utc_now": datetime.utcnow().isoformat() + "Z"}

    return [
        get_profile_summary,
        remember_preference,
        create_task,
        list_tasks,
        get_current_time,
    ]
