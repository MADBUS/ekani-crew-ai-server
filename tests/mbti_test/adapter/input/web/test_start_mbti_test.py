from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
import uuid
from app.auth.adapter.input.web.auth_dependency import get_current_user_id

client = TestClient(app)

def mock_get_current_user_id():
    return str(uuid.uuid4())

app.dependency_overrides[get_current_user_id] = mock_get_current_user_id

def test_start_new_mbti_test_when_no_session_exists():
    with patch("app.mbti_test.application.use_case.find_in_progress_test_use_case.FindInProgressTestUseCase.execute") as mock_find_execute:
        mock_find_execute.return_value = None
        with patch("app.mbti_test.application.use_case.start_mbti_test_service.StartMBTITestService") as mock_start_use_case:
            mock_session = MagicMock()
            mock_session.id = uuid.uuid4()
            mock_first_question = MagicMock()
            mock_start_use_case.return_value.execute.return_value = MagicMock(session=mock_session, first_question=mock_first_question)

            response = client.post("/mbti-test/start")
            assert response.status_code == 200
            assert "session" in response.json()


def test_start_mbti_test_when_session_exists():
    """진행 중인 테스트가 있으면 409 Conflict를 반환한다"""
    with patch("app.mbti_test.application.use_case.find_in_progress_test_use_case.FindInProgressTestUseCase.execute") as mock_find_execute:
        mock_find_execute.return_value = MagicMock()

        response = client.post("/mbti-test/start")
        assert response.status_code == 409
        assert "detail" in response.json()
        assert "in-progress test already exists" in response.json()["detail"].lower()


def test_start_new_mbti_test_with_force_new():
    with patch("app.mbti_test.application.use_case.find_in_progress_test_use_case.FindInProgressTestUseCase.execute") as mock_find_execute:
        mock_find_execute.return_value = MagicMock()
        with patch("app.mbti_test.application.use_case.delete_in_progress_test_use_case.DeleteInProgressTestUseCase.execute") as mock_delete_execute:
            with patch("app.mbti_test.application.use_case.start_mbti_test_service.StartMBTITestService") as mock_start_use_case:
                mock_session = MagicMock()
                mock_session.id = uuid.uuid4()
                mock_first_question = MagicMock()
                mock_start_use_case.return_value.execute.return_value = MagicMock(session=mock_session, first_question=mock_first_question)

                response = client.post("/mbti-test/start?force_new=true")
                assert response.status_code == 200
                assert "session" in response.json()
                mock_delete_execute.assert_called_once()

def test_delete_in_progress_mbti_test():
    with patch("app.mbti_test.application.use_case.delete_in_progress_test_use_case.DeleteInProgressTestUseCase.execute") as mock_delete_execute:
        response = client.delete("/mbti-test/session")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_delete_execute.assert_called_once()
