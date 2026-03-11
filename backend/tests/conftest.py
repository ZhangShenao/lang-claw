"""Pytest configuration and fixtures for lang-claw backend tests."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import JSON, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings() -> Settings:
    """Create mock settings for testing."""
    return Settings(
        app_name="Test App",
        app_env="test",
        zhipu_api_key="test-key",
        zhipu_base_url="https://test.example.com",
        mongo_uri="mongodb://localhost:27017",
        mongo_db="test_db",
        postgres_dsn="sqlite+aiosqlite:///:memory:",
    )


# Create test-specific base and models to avoid JSONB issues with SQLite
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import uuid4
from datetime import datetime


class TestBase:
    """Test base class for SQLite compatibility."""
    pass


# Use JSON instead of JSONB for SQLite compatibility
JSONType = JSON


class TestUser(TestBase):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    external_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TestUserProfile(TestBase):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    preferences: Mapped[dict] = mapped_column(JSONType, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class TestAgentSession(TestBase):
    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    thread_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), default="New Chat")
    last_message_preview: Mapped[str] = mapped_column(String(240), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class TestTask(TestBase):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    details: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# Create a combined base for test models
from sqlalchemy.orm import DeclarativeBase


class TestModelBase(DeclarativeBase):
    pass


# Re-define models with the test base
class User(TestModelBase):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    external_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserProfile(TestModelBase):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    preferences: Mapped[dict] = mapped_column(JSONType, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class AgentSession(TestModelBase):
    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    thread_id: Mapped[str] = mapped_column(String(36), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), default="New Chat")
    last_message_preview: Mapped[str] = mapped_column(String(240), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Task(TestModelBase):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    details: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


@pytest.fixture
async def async_engine(mock_settings: Settings):
    """Create an async SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(TestModelBase.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create an async session for testing."""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def mock_user() -> User:
    """Create a mock user for testing."""
    return User(
        id="test-user-id",
        external_id="test-external-id",
        display_name="Test User",
    )


@pytest.fixture
def mock_session(mock_user: User) -> AgentSession:
    """Create a mock agent session for testing."""
    return AgentSession(
        id="test-session-id",
        user_id=mock_user.id,
        thread_id="test-thread-id",
        title="Test Session",
        last_message_preview="Test message",
    )


@pytest.fixture
def mock_task(mock_user: User) -> Task:
    """Create a mock task for testing."""
    return Task(
        id="test-task-id",
        user_id=mock_user.id,
        title="Test Task",
        details="Test task details",
        status="open",
    )


@pytest.fixture
def mock_profile(mock_user: User) -> UserProfile:
    """Create a mock user profile for testing."""
    return UserProfile(
        id="test-profile-id",
        user_id=mock_user.id,
        bio="Test bio",
        preferences={"theme": "dark"},
    )


@pytest.fixture
def mock_history_store():
    """Create a mock chat history store."""
    store = AsyncMock()
    store.append_message = AsyncMock(return_value="test-message-id")
    store.list_messages = AsyncMock(return_value=[])
    return store


@pytest.fixture
def mock_checkpoint_manager():
    """Create a mock checkpoint manager."""
    manager = MagicMock()
    manager.checkpointer = MagicMock()
    return manager


@pytest.fixture
def mock_agent_runtime():
    """Create a mock agent runtime."""
    runtime = AsyncMock()
    runtime.astream_reply = AsyncMock()
    return runtime


@pytest.fixture
def mock_session_factory():
    """Create a mock session factory for tools tests."""
    mock_session = AsyncMock()
    factory = MagicMock()
    factory.return_value = MagicMock()
    factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    factory.return_value.__aexit__ = AsyncMock(return_value=None)
    return factory, mock_session
