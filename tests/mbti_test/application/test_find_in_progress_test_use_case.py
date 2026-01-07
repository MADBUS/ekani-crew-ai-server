import pytest
from app.mbti_test.application.use_case.find_in_progress_test_use_case import FindInProgressTestUseCase
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType, TestStatus
from app.mbti_test.application.port.out.mbti_test_session_repository import MBTITestSessionRepository
import uuid
from datetime import datetime

class MockMBTITestSessionRepository(MBTITestSessionRepository):
    def __init__(self):
        self.sessions = {}

    def find_by_user_id_and_status(self, user_id: str, status: str) -> MBTITestSession:
        # Convert user_id to UUID for comparison
        for (stored_user_id, stored_status), session in self.sessions.items():
            if str(stored_user_id) == str(user_id) and str(stored_status) == status:
                return session
        return None

    def save(self, session: MBTITestSession) -> MBTITestSession:
        self.sessions[(session.user_id, str(session.status.value) if hasattr(session.status, 'value') else str(session.status))] = session
        return session

    def delete(self, session: MBTITestSession):
        status_str = str(session.status.value) if hasattr(session.status, 'value') else str(session.status)
        key = (session.user_id, status_str)
        if key in self.sessions:
            del self.sessions[key]

def test_find_in_progress_mbti_test():
    # given
    repo = MockMBTITestSessionRepository()
    use_case = FindInProgressTestUseCase(repo)
    user_id = uuid.uuid4()
    session = MBTITestSession(
        id=uuid.uuid4(),
        user_id=user_id,
        status=TestStatus.IN_PROGRESS,
        test_type=TestType.HUMAN,
        created_at=datetime.now()
    )
    repo.save(session)

    # when
    result = use_case.execute(str(user_id))

    # then
    assert result is not None
    assert result.user_id == user_id
    assert result.status == TestStatus.IN_PROGRESS
