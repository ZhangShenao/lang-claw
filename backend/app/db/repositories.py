from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentSession, Task, User, UserProfile


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, external_id: str, display_name: str | None = None) -> User:
        result = await self.session.execute(
            select(User).where(User.external_id == external_id)
        )
        user = result.scalar_one_or_none()
        if user is not None:
            return user

        user = User(
            external_id=external_id,
            display_name=display_name or external_id,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(
        self,
        user_id: str,
        session_id: str | None,
        title_seed: str,
    ) -> AgentSession:
        thread_id = session_id or str(uuid4())
        result = await self.session.execute(
            select(AgentSession).where(AgentSession.thread_id == thread_id)
        )
        session_row = result.scalar_one_or_none()
        if session_row is not None:
            return session_row

        session_row = AgentSession(
            user_id=user_id,
            thread_id=thread_id,
            title=title_seed[:80] or "New Chat",
        )
        self.session.add(session_row)
        await self.session.commit()
        await self.session.refresh(session_row)
        return session_row

    async def list_for_user(self, user_id: str) -> list[AgentSession]:
        result = await self.session.execute(
            select(AgentSession)
            .where(AgentSession.user_id == user_id)
            .order_by(AgentSession.updated_at.desc())
        )
        return list(result.scalars().all())

    async def touch(self, session_row: AgentSession, preview: str) -> AgentSession:
        session_row.last_message_preview = preview[:240]
        session_row.updated_at = datetime.now(timezone.utc)
        self.session.add(session_row)
        await self.session.commit()
        await self.session.refresh(session_row)
        return session_row


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: str) -> UserProfile:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if profile is not None:
            return profile

        profile = UserProfile(user_id=user_id, bio="", preferences={})
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def remember_preference(self, user_id: str, key: str, value: str) -> UserProfile:
        profile = await self.get_or_create(user_id)
        profile.preferences = {**profile.preferences, key: value}
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: str,
        title: str,
        details: str = "",
        due_at: datetime | None = None,
    ) -> Task:
        task = Task(
            user_id=user_id,
            title=title,
            details=details,
            due_at=due_at,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def list_for_user(self, user_id: str, status: str = "open") -> list[Task]:
        query = select(Task).where(Task.user_id == user_id)
        if status != "all":
            query = query.where(Task.status == status)
        query = query.order_by(Task.updated_at.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
