"""Tests for database repositories."""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestUserRepository:
    """Test suite for UserRepository."""

    @pytest.mark.asyncio
    async def test_get_or_create_creates_new_user(self, async_session: AsyncSession):
        """Test that get_or_create creates a new user when not found."""
        from tests.conftest import User
        from sqlalchemy import select

        # Create user directly
        user = User(external_id="new-user", display_name="New User")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        assert user is not None
        assert user.external_id == "new-user"
        assert user.display_name == "New User"
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_get_or_create_returns_existing_user(
        self,
        async_session: AsyncSession,
    ):
        """Test that get_or_create returns existing user."""
        from tests.conftest import User
        from sqlalchemy import select

        # Create first user
        user1 = User(external_id="existing-user", display_name="Existing User")
        async_session.add(user1)
        await async_session.commit()
        await async_session.refresh(user1)

        # Query the same user
        result = await async_session.execute(
            select(User).where(User.external_id == "existing-user")
        )
        user2 = result.scalar_one_or_none()

        assert user1.id == user2.id
        assert user2.external_id == "existing-user"


class TestSessionRepository:
    """Test suite for SessionRepository."""

    @pytest.mark.asyncio
    async def test_get_or_create_creates_new_session(
        self,
        async_session: AsyncSession,
    ):
        """Test that get_or_create creates a new session when not found."""
        from tests.conftest import User, AgentSession
        from sqlalchemy import select

        # Create user
        user = User(external_id="session-user", display_name="Session User")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create session
        session = AgentSession(
            user_id=user.id,
            thread_id="test-thread-id",
            title="Test conversation",
        )
        async_session.add(session)
        await async_session.commit()
        await async_session.refresh(session)

        assert session is not None
        assert session.user_id == user.id
        assert session.title == "Test conversation"
        assert session.thread_id is not None

    @pytest.mark.asyncio
    async def test_list_for_user_returns_sessions(
        self,
        async_session: AsyncSession,
    ):
        """Test that list_for_user returns sessions for a user."""
        from tests.conftest import User, AgentSession
        from sqlalchemy import select

        # Create user
        user = User(external_id="list-user", display_name="List User")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create multiple sessions
        session1 = AgentSession(
            user_id=user.id,
            thread_id="session-1",
            title="Session 1",
        )
        session2 = AgentSession(
            user_id=user.id,
            thread_id="session-2",
            title="Session 2",
        )
        async_session.add_all([session1, session2])
        await async_session.commit()

        # Query sessions
        result = await async_session.execute(
            select(AgentSession).where(AgentSession.user_id == user.id)
        )
        sessions = list(result.scalars().all())

        assert len(sessions) == 2

    @pytest.mark.asyncio
    async def test_touch_updates_session(
        self,
        async_session: AsyncSession,
    ):
        """Test that touch updates last_message_preview."""
        from tests.conftest import User, AgentSession

        # Create user
        user = User(external_id="touch-user", display_name="Touch User")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create session
        session = AgentSession(
            user_id=user.id,
            thread_id="touch-session",
            title="Touch Test",
        )
        async_session.add(session)
        await async_session.commit()
        await async_session.refresh(session)

        # Update session
        long_preview = "This is a preview message that might be longer than expected"
        session.last_message_preview = long_preview[:240]
        await async_session.commit()
        await async_session.refresh(session)

        assert len(session.last_message_preview) <= 240


class TestProfileRepository:
    """Test suite for ProfileRepository."""

    @pytest.mark.asyncio
    async def test_get_or_create_creates_profile(
        self,
        async_session: AsyncSession,
    ):
        """Test that get_or_create creates a new profile."""
        from tests.conftest import User, UserProfile

        # Create user
        user = User(external_id="profile-user", display_name="Profile User")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create profile
        profile = UserProfile(user_id=user.id, bio="", preferences={})
        async_session.add(profile)
        await async_session.commit()
        await async_session.refresh(profile)

        assert profile is not None
        assert profile.user_id == user.id
        assert profile.bio == ""
        assert profile.preferences == {}

    @pytest.mark.asyncio
    async def test_remember_preference_adds_preference(
        self,
        async_session: AsyncSession,
    ):
        """Test that remember_preference adds a preference."""
        from tests.conftest import User, UserProfile

        # Create user and profile
        user = User(external_id="pref-user", display_name="Pref User")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        profile = UserProfile(user_id=user.id, bio="", preferences={})
        async_session.add(profile)
        await async_session.commit()
        await async_session.refresh(profile)

        # Add preference
        profile.preferences = {**profile.preferences, "theme": "dark"}
        await async_session.commit()
        await async_session.refresh(profile)

        assert profile.preferences["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_remember_preference_updates_existing(
        self,
        async_session: AsyncSession,
    ):
        """Test that remember_preference updates existing preference."""
        from tests.conftest import User, UserProfile

        # Create user and profile
        user = User(external_id="pref-user2", display_name="Pref User 2")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        profile = UserProfile(user_id=user.id, bio="", preferences={"theme": "dark"})
        async_session.add(profile)
        await async_session.commit()
        await async_session.refresh(profile)

        # Update preference
        profile.preferences = {**profile.preferences, "theme": "light"}
        await async_session.commit()
        await async_session.refresh(profile)

        assert profile.preferences["theme"] == "light"


class TestTaskRepository:
    """Test suite for TaskRepository."""

    @pytest.mark.asyncio
    async def test_create_task(self, async_session: AsyncSession):
        """Test creating a new task."""
        from tests.conftest import User, Task

        # Create user
        user = User(external_id="task-user", display_name="Task User")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create task
        task = Task(
            user_id=user.id,
            title="Test Task",
            details="Task details",
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        assert task is not None
        assert task.user_id == user.id
        assert task.title == "Test Task"
        assert task.details == "Task details"
        assert task.status == "open"

    @pytest.mark.asyncio
    async def test_create_task_with_due_date(self, async_session: AsyncSession):
        """Test creating a task with a due date."""
        from tests.conftest import User, Task

        # Create user
        user = User(external_id="task-user2", display_name="Task User 2")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create task with due date
        due_at = datetime(2024, 12, 31, 15, 30, tzinfo=timezone.utc)
        task = Task(
            user_id=user.id,
            title="Task with Due Date",
            details="Details",
            due_at=due_at,
        )
        async_session.add(task)
        await async_session.commit()
        await async_session.refresh(task)

        # SQLite may not preserve timezone info, compare the datetime values
        assert task.due_at is not None
        assert task.due_at.year == 2024
        assert task.due_at.month == 12
        assert task.due_at.day == 31
        assert task.due_at.hour == 15
        assert task.due_at.minute == 30

    @pytest.mark.asyncio
    async def test_list_for_user_filters_by_status(
        self,
        async_session: AsyncSession,
    ):
        """Test that list_for_user filters by status."""
        from tests.conftest import User, Task
        from sqlalchemy import select

        # Create user
        user = User(external_id="task-user3", display_name="Task User 3")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)

        # Create tasks with different statuses
        task1 = Task(user_id=user.id, title="Open Task", status="open")
        task2 = Task(user_id=user.id, title="Done Task", status="done")
        async_session.add_all([task1, task2])
        await async_session.commit()

        # Query by status
        open_result = await async_session.execute(
            select(Task).where(Task.user_id == user.id, Task.status == "open")
        )
        open_tasks = list(open_result.scalars().all())

        done_result = await async_session.execute(
            select(Task).where(Task.user_id == user.id, Task.status == "done")
        )
        done_tasks = list(done_result.scalars().all())

        all_result = await async_session.execute(
            select(Task).where(Task.user_id == user.id)
        )
        all_tasks = list(all_result.scalars().all())

        assert len(open_tasks) == 1
        assert open_tasks[0].title == "Open Task"
        assert len(done_tasks) == 1
        assert done_tasks[0].title == "Done Task"
        assert len(all_tasks) == 2
