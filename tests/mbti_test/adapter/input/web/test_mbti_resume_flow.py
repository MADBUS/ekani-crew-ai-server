"""
Integration test for MBTI-7: Resume and restart functionality
Tests the full flow of starting, resuming, and restarting MBTI tests
"""
import pytest
import uuid
from datetime import datetime
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType, TestStatus, Turn
from tests.mbti_test.application.test_find_in_progress_test_use_case import MockMBTITestSessionRepository
from app.mbti_test.application.use_case.find_in_progress_test_use_case import FindInProgressTestUseCase
from app.mbti_test.application.use_case.delete_in_progress_test_use_case import DeleteInProgressTestUseCase
from app.mbti_test.application.use_case.resume_test_use_case import ResumeTestUseCase
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider


class MockAIQuestionProvider:
    def generate_questions(self, command):
        from app.mbti_test.domain.models import AIQuestionResponse, AIQuestion
        return AIQuestionResponse(
            questions=[AIQuestion(text="AI 질문입니다", dimension="EI")]
        )


def test_full_mbti_resume_flow():
    """전체 플로우: 시작 -> 중단 -> 조회 -> 이어하기"""
    # Setup
    repo = MockMBTITestSessionRepository()
    find_use_case = FindInProgressTestUseCase(repo)
    delete_use_case = DeleteInProgressTestUseCase(repo)
    resume_use_case = ResumeTestUseCase(
        repo,
        HumanQuestionProvider(),
        MockAIQuestionProvider()
    )

    user_id = uuid.uuid4()

    # Given: 진행 중인 테스트가 없음
    assert find_use_case.execute(str(user_id)) is None

    # When: 새로운 테스트 세션을 시작하고 1개 답변 완료
    session = MBTITestSession(
        id=uuid.uuid4(),
        user_id=user_id,
        status=TestStatus.IN_PROGRESS,
        test_type=TestType.HUMAN,
        created_at=datetime.now(),
        turns=[
            Turn(
                turn_number=1,
                question="첫 번째 질문",
                answer="첫 번째 답변",
                dimension="EI",
                scores={"E": 5, "I": 3},
                side="E",
                score=5,
            )
        ],
        greeting_completed=True,
    )
    repo.save(session)

    # Then: 진행 중인 테스트를 조회할 수 있음
    in_progress = find_use_case.execute(str(user_id))
    assert in_progress is not None
    assert len(in_progress.turns) == 1

    # When: 테스트를 재개함
    resume_result = resume_use_case.execute(str(user_id))

    # Then: 다음 질문이 반환됨
    assert resume_result is not None
    assert resume_result.session.id == session.id
    assert resume_result.next_question is not None


def test_restart_flow_deletes_and_creates_new():
    """재시작 플로우: 진행 중인 테스트 삭제 후 새로 시작"""
    # Setup
    repo = MockMBTITestSessionRepository()
    find_use_case = FindInProgressTestUseCase(repo)
    delete_use_case = DeleteInProgressTestUseCase(repo)

    user_id = uuid.uuid4()

    # Given: 진행 중인 테스트가 있음
    session = MBTITestSession(
        id=uuid.uuid4(),
        user_id=user_id,
        status=TestStatus.IN_PROGRESS,
        test_type=TestType.HUMAN,
        created_at=datetime.now(),
        turns=[
            Turn(
                turn_number=1,
                question="첫 번째 질문",
                answer="첫 번째 답변",
                dimension="EI",
                scores={"E": 5, "I": 3},
                side="E",
                score=5,
            )
        ],
        greeting_completed=True,
    )
    repo.save(session)
    assert find_use_case.execute(str(user_id)) is not None

    # When: 진행 중인 테스트를 삭제함
    delete_use_case.execute(str(user_id))

    # Then: 진행 중인 테스트가 없음
    assert find_use_case.execute(str(user_id)) is None

    # When: 새로운 테스트를 시작함
    new_session = MBTITestSession(
        id=uuid.uuid4(),
        user_id=user_id,
        status=TestStatus.IN_PROGRESS,
        test_type=TestType.HUMAN,
        created_at=datetime.now(),
        turns=[],
        greeting_completed=False,
    )
    repo.save(new_session)

    # Then: 새로운 세션이 생성됨 (턴이 비어있음)
    in_progress = find_use_case.execute(str(user_id))
    assert in_progress is not None
    assert len(in_progress.turns) == 0
    assert in_progress.id == new_session.id
    assert in_progress.id != session.id


def test_completed_tests_not_returned_as_in_progress():
    """완료된 테스트는 진행 중 목록에 포함되지 않음"""
    # Setup
    repo = MockMBTITestSessionRepository()
    find_use_case = FindInProgressTestUseCase(repo)

    user_id = uuid.uuid4()

    # Given: 완료된 테스트가 있음
    completed_session = MBTITestSession(
        id=uuid.uuid4(),
        user_id=user_id,
        status=TestStatus.COMPLETED,
        test_type=TestType.HUMAN,
        created_at=datetime.now(),
        turns=[],
        greeting_completed=True,
    )
    # Store with COMPLETED status
    repo.sessions[(user_id, "COMPLETED")] = completed_session

    # When: 진행 중인 테스트를 조회함
    in_progress = find_use_case.execute(str(user_id))

    # Then: 진행 중인 테스트가 없음
    assert in_progress is None
