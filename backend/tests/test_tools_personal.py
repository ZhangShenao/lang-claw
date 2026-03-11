"""Tests for personal tools."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestPersonalTools:
    """Test suite for personal tools."""

    def test_build_personal_tools_returns_list(self):
        """Test that build_personal_tools returns a list of tools."""
        with patch("app.tools.personal_tools.get_session_factory"):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id="test-user")
            assert isinstance(tools, list)
            assert len(tools) == 5

    def test_tool_names(self):
        """Test that tools have expected names."""
        with patch("app.tools.personal_tools.get_session_factory"):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id="test-user")
            tool_names = [tool.name for tool in tools]
            expected_names = [
                "get_profile_summary",
                "remember_preference",
                "create_task",
                "list_tasks",
                "get_current_time",
            ]
            assert tool_names == expected_names


class TestGetProfileSummary:
    """Test suite for get_profile_summary tool."""

    @pytest.mark.asyncio
    async def test_get_profile_summary_returns_dict(self, mock_user):
        """Test that get_profile_summary returns a dictionary."""
        mock_factory = MagicMock()
        mock_session = AsyncMock()
        mock_factory.return_value = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("app.tools.personal_tools.get_session_factory", return_value=mock_factory):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id=mock_user.id)
            get_profile_summary = next(t for t in tools if t.name == "get_profile_summary")

            with patch("app.tools.personal_tools.ProfileRepository") as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.get_or_create = AsyncMock(
                    return_value=MagicMock(bio="Test bio", preferences={"theme": "dark"})
                )
                mock_repo_class.return_value = mock_repo

                result = await get_profile_summary.ainvoke({})
                assert isinstance(result, dict)
                assert "bio" in result
                assert "preferences" in result


class TestCreateTask:
    """Test suite for create_task tool."""

    @pytest.mark.asyncio
    async def test_create_task_with_valid_date(self, mock_user, mock_task):
        """Test creating a task with a valid ISO date."""
        mock_factory = MagicMock()
        mock_session = AsyncMock()
        mock_factory.return_value = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("app.tools.personal_tools.get_session_factory", return_value=mock_factory):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id=mock_user.id)
            create_task = next(t for t in tools if t.name == "create_task")

            valid_iso_date = "2024-12-31T15:30:00"

            with patch("app.tools.personal_tools.TaskRepository") as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.create = AsyncMock(return_value=mock_task)
                mock_repo_class.return_value = mock_repo

                result = await create_task.ainvoke({
                    "title": "Test Task",
                    "details": "Details",
                    "due_at_iso": valid_iso_date,
                })

                assert isinstance(result, dict)
                assert "task_id" in result

    @pytest.mark.asyncio
    async def test_create_task_with_invalid_date(self, mock_user):
        """Test creating a task with an invalid ISO date returns error."""
        with patch("app.tools.personal_tools.get_session_factory"):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id=mock_user.id)
            create_task = next(t for t in tools if t.name == "create_task")

            invalid_date = "not-a-valid-date"

            result = await create_task.ainvoke({
                "title": "Test Task",
                "details": "Details",
                "due_at_iso": invalid_date,
            })

            assert isinstance(result, dict)
            assert "error" in result
            assert result["task_id"] is None
            assert "Invalid date format" in result["error"]

    @pytest.mark.asyncio
    async def test_create_task_without_date(self, mock_user, mock_task):
        """Test creating a task without a due date."""
        mock_factory = MagicMock()
        mock_session = AsyncMock()
        mock_factory.return_value = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("app.tools.personal_tools.get_session_factory", return_value=mock_factory):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id=mock_user.id)
            create_task = next(t for t in tools if t.name == "create_task")

            with patch("app.tools.personal_tools.TaskRepository") as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.create = AsyncMock(return_value=mock_task)
                mock_repo_class.return_value = mock_repo

                result = await create_task.ainvoke({
                    "title": "Test Task",
                    "details": "Details",
                    "due_at_iso": "",
                })

                assert isinstance(result, dict)
                assert "task_id" in result
                assert result["task_id"] == mock_task.id


class TestGetCurrentTime:
    """Test suite for get_current_time tool."""

    def test_get_current_time_returns_dict(self):
        """Test that get_current_time returns a dictionary with utc_now."""
        with patch("app.tools.personal_tools.get_session_factory"):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id="test-user")
            get_current_time = next(t for t in tools if t.name == "get_current_time")

            result = get_current_time.invoke({})

            assert isinstance(result, dict)
            assert "utc_now" in result
            # Verify the format is ISO 8601 with Z suffix
            assert result["utc_now"].endswith("Z")


class TestListTasks:
    """Test suite for list_tasks tool."""

    @pytest.mark.asyncio
    async def test_list_tasks_returns_list(self, mock_user, mock_task):
        """Test that list_tasks returns a list of tasks."""
        mock_factory = MagicMock()
        mock_session = AsyncMock()
        mock_factory.return_value = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("app.tools.personal_tools.get_session_factory", return_value=mock_factory):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id=mock_user.id)
            list_tasks = next(t for t in tools if t.name == "list_tasks")

            with patch("app.tools.personal_tools.TaskRepository") as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.list_for_user = AsyncMock(return_value=[mock_task])
                mock_repo_class.return_value = mock_repo

                result = await list_tasks.ainvoke({"status": "open"})

                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0]["task_id"] == mock_task.id


class TestRememberPreference:
    """Test suite for remember_preference tool."""

    @pytest.mark.asyncio
    async def test_remember_preference_returns_dict(self, mock_user, mock_profile):
        """Test that remember_preference returns a dictionary."""
        mock_factory = MagicMock()
        mock_session = AsyncMock()
        mock_factory.return_value = MagicMock()
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch("app.tools.personal_tools.get_session_factory", return_value=mock_factory):
            from app.tools.personal_tools import build_personal_tools

            tools = build_personal_tools(user_id=mock_user.id)
            remember_preference = next(t for t in tools if t.name == "remember_preference")

            with patch("app.tools.personal_tools.ProfileRepository") as mock_repo_class:
                mock_repo = AsyncMock()
                mock_repo.remember_preference = AsyncMock(return_value=mock_profile)
                mock_repo_class.return_value = mock_repo

                result = await remember_preference.ainvoke({
                    "key": "theme",
                    "value": "light",
                })

                assert isinstance(result, dict)
                assert result["stored"] is True
                assert "preferences" in result
