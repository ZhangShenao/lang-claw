"""Tests for chat API endpoints."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.schemas.chat import ChatRequest


class TestChatStreamEndpoint:
    """Test suite for /api/chat/stream endpoint."""

    @pytest.fixture
    def client(self, mock_settings, mock_history_store, mock_checkpoint_manager):
        """Create a test client with mocked dependencies."""
        app = create_app()

        # Override app state
        app.state.settings = mock_settings
        app.state.history_store = mock_history_store
        app.state.checkpoint_manager = mock_checkpoint_manager
        app.state.agent_runtime = AsyncMock()

        return TestClient(app)

    def test_chat_stream_requires_message(self, client):
        """Test that the endpoint requires a message."""
        response = client.post(
            "/api/chat/stream",
            json={"message": ""},
        )
        assert response.status_code == 422  # Validation error

    def test_chat_stream_message_too_long(self, client):
        """Test that messages over 8000 characters are rejected."""
        response = client.post(
            "/api/chat/stream",
            json={"message": "x" * 8001},
        )
        assert response.status_code == 422  # Validation error

    def test_sse_format(self):
        """Test the SSE formatting function."""
        from app.api.chat import _sse

        result = _sse("test", {"key": "value"})
        assert result.startswith("event: test\n")
        assert "data:" in result
        assert result.endswith("\n\n")

        # Verify JSON encoding
        data_line = result.split("\n")[1]
        data_json = data_line.replace("data: ", "")
        parsed = json.loads(data_json)
        assert parsed == {"key": "value"}

    def test_sse_handles_unicode(self):
        """Test that SSE handles unicode characters."""
        from app.api.chat import _sse

        result = _sse("test", {"message": "你好世界"})
        assert "你好世界" in result


class TestChatRequestSchema:
    """Test suite for ChatRequest schema validation."""

    def test_valid_request(self):
        """Test a valid ChatRequest."""
        request = ChatRequest(message="Hello")
        assert request.message == "Hello"
        assert request.session_id is None
        assert request.user_id is None

    def test_request_with_all_fields(self):
        """Test ChatRequest with all fields."""
        request = ChatRequest(
            message="Hello",
            session_id="session-123",
            user_id="user-456",
        )
        assert request.message == "Hello"
        assert request.session_id == "session-123"
        assert request.user_id == "user-456"

    def test_empty_message_rejected(self):
        """Test that empty message is rejected."""
        with pytest.raises(ValueError):
            ChatRequest(message="")

    def test_message_max_length(self):
        """Test message max length validation."""
        # Should not raise
        ChatRequest(message="x" * 8000)

        # Should raise
        with pytest.raises(ValueError):
            ChatRequest(message="x" * 8001)


class TestSessionsEndpoint:
    """Test suite for /api/sessions endpoints."""

    @pytest.fixture
    def client(self, mock_settings, mock_history_store, mock_checkpoint_manager):
        """Create a test client with mocked dependencies."""
        app = create_app()

        # Override app state
        app.state.settings = mock_settings
        app.state.history_store = mock_history_store
        app.state.checkpoint_manager = mock_checkpoint_manager
        app.state.agent_runtime = AsyncMock()

        return TestClient(app)

    def test_list_sessions_returns_list(self, client):
        """Test that list sessions returns a list."""
        with patch("app.api.sessions.get_session_factory") as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value = MagicMock()
            mock_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_factory.return_value.__aexit__ = AsyncMock(return_value=None)

            with patch("app.api.sessions.UserRepository") as mock_user_repo:
                mock_user = MagicMock()
                mock_user.id = "test-user-id"
                mock_user_repo.return_value.get_or_create = AsyncMock(
                    return_value=mock_user
                )

                with patch("app.api.sessions.SessionRepository") as mock_session_repo:
                    mock_session_repo.return_value.list_for_user = AsyncMock(
                        return_value=[]
                    )

                    response = client.get("/api/sessions")

                    assert response.status_code == 200
                    assert isinstance(response.json(), list)

    def test_get_messages_for_session(self, client, mock_history_store):
        """Test getting messages for a session."""
        mock_history_store.list_messages = AsyncMock(
            return_value=[
                {
                    "id": "msg-1",
                    "role": "user",
                    "content": "Hello",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        )

        response = client.get("/api/sessions/test-session/messages")

        assert response.status_code == 200
        messages = response.json()
        assert len(messages) == 1
        assert messages[0]["role"] == "user"

    def test_get_messages_empty_session(self, client, mock_history_store):
        """Test getting messages for an empty session."""
        mock_history_store.list_messages = AsyncMock(return_value=[])

        response = client.get("/api/sessions/empty-session/messages")

        assert response.status_code == 200
        assert response.json() == []
