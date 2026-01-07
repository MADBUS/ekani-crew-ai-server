import pytest
from app.mbti_test.application.use_case.delete_in_progress_test_use_case import DeleteInProgressTestUseCase
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType, TestStatus
from tests.mbti_test.application.test_find_in_progress_test_use_case import MockMBTITestSessionRepository
import uuid
from datetime import datetime

def test_delete_in_progress_mbti_test():
    # given
    repo = MockMBTITestSessionRepository()
    use_case = DeleteInProgressTestUseCase(repo)
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
    use_case.execute(str(user_id))

    # then
    assert repo.find_by_user_id_and_status(str(user_id), "IN_PROGRESS") is None
