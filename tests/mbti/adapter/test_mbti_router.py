import uuid
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.auth.domain.session import Session as AuthSession
from config.database import get_db

# This fixture is defined in conftest.py and sets up the test database
@pytest.fixture
def client(db_session: Session):
    """A TestClient that uses a temporary, isolated database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass # The fixture in conftest handles cleanup

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


def mock_auth_session(session: AuthSession):
    """Mocks the session authentication context manager."""
    mock_repo = AsyncMock()
    mock_repo.find_by_session_id.return_value = session
    return patch(
        "app.auth.adapter.input.web.auth_dependency.RedisSessionRepository",
        return_value=mock_repo
    )


def test_start_mbti_test_endpoint(client: TestClient):
    # Given
    user_id = uuid.uuid4()
    session = AuthSession(session_id="valid-session", user_id=str(user_id))

    # When
    with mock_auth_session(session):
        response = client.post(
            "/mbti-test/start",
            cookies={"session_id": "valid-session"},
            params={"test_type": "human"} # Pass test_type as a query param
        )

    # Then
    assert response.status_code == 200
    response_json = response.json()
    assert "session" in response_json
    assert "first_question" in response_json


def test_start_mbti_test_without_auth_returns_401(client: TestClient):
    # When
    response = client.post("/mbti-test/start?test_type=ai")
    # Then
    assert response.status_code == 401

def test_answer_question_chat_endpoint(client: TestClient):
    # Given
    user_id = uuid.uuid4()
    session = AuthSession(session_id="valid-session", user_id=str(user_id))

    with mock_auth_session(session):
        # 1. Start test to get session_id
        start_response = client.post(
            "/mbti-test/start",
            cookies={"session_id": "valid-session"}
        )
        assert start_response.status_code == 200
        session_id = start_response.json()["session"]["id"]

        # 2. Post an answer to the chat endpoint (for the greeting)
        chat_response_1 = client.post(
            f"/mbti-test/{session_id}/answer",
            json={"content": "Hi"},
            cookies={"session_id": "valid-session"}
        )
        assert chat_response_1.status_code == 200
        response_json_1 = chat_response_1.json()
        assert response_json_1["question_number"] == 1

        # 3. Post a second answer (for the first real question)
        chat_response_2 = client.post(
            f"/mbti-test/{session_id}/answer",
            json={"content": "My real answer"},
            cookies={"session_id": "valid-session"}
        )

    # Then
    assert chat_response_2.status_code == 200
    response_json_2 = chat_response_2.json()
    assert "next_question" in response_json_2
    assert response_json_2["question_number"] == 2