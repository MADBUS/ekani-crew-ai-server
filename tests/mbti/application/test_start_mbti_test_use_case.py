import uuid

from app.mbti_test.application.port.input.start_mbti_test_use_case import StartMBTITestCommand
from app.mbti_test.application.use_case.start_mbti_test_service import StartMBTITestService
from app.mbti_test.domain.mbti_test_session import TestType, TestStatus
from app.mbti_test.domain.mbti_message import MessageRole, MessageSource
from tests.mbti.fixtures.fake_mbti_test_session_repository import FakeMBTITestSessionRepository
from tests.mbti.fixtures.fake_question_provider import FakeQuestionProvider


def test_start_mbti_test_should_create_session_and_return_first_question():
    # Given
    user_id = uuid.uuid4()
    repository = FakeMBTITestSessionRepository()
    question_provider = FakeQuestionProvider()
    service = StartMBTITestService(
        mbti_test_session_repository=repository,
        human_question_provider=question_provider,
    )
    command = StartMBTITestCommand(user_id=user_id, test_type=TestType.AI)

    # When
    response = service.execute(command)

    # Then
    # Check that a session was created and saved
    saved_sessions = repository.find_all()
    assert len(saved_sessions) == 1
    session_in_db = saved_sessions[0]
    assert session_in_db.user_id == user_id
    assert session_in_db.status == TestStatus.IN_PROGRESS
    assert session_in_db.test_type == TestType.AI

    # Check the response
    assert response.session.id == session_in_db.id
    assert response.first_question.role == MessageRole.ASSISTANT
    assert response.first_question.source == MessageSource.HUMAN