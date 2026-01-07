import pytest
import uuid
from datetime import datetime
from app.mbti_test.application.use_case.resume_test_use_case import ResumeTestUseCase
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestType, TestStatus, Turn
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
from tests.mbti_test.application.test_find_in_progress_test_use_case import MockMBTITestSessionRepository


class MockAIQuestionProvider:
    def generate_questions(self, command):
        from app.mbti_test.domain.models import AIQuestionResponse, AIQuestion
        return AIQuestionResponse(
            questions=[AIQuestion(text="AI 질문입니다", dimension="EI")]
        )


def test_resume_in_progress_test_returns_next_question():
    """진행 중인 테스트를 재개하면 다음 질문을 반환한다"""
    # given
    repo = MockMBTITestSessionRepository()
    human_provider = HumanQuestionProvider()
    ai_provider = MockAIQuestionProvider()
    use_case = ResumeTestUseCase(repo, human_provider, ai_provider)

    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    session = MBTITestSession(
        id=session_id,
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

    # when
    result = use_case.execute(str(user_id))

    # then
    assert result is not None
    assert result.session.id == session_id
    assert result.next_question is not None
    assert len(result.next_question.content) > 0


def test_resume_with_no_in_progress_test_returns_none():
    """진행 중인 테스트가 없으면 None을 반환한다"""
    # given
    repo = MockMBTITestSessionRepository()
    human_provider = HumanQuestionProvider()
    ai_provider = MockAIQuestionProvider()
    use_case = ResumeTestUseCase(repo, human_provider, ai_provider)

    user_id = uuid.uuid4()

    # when
    result = use_case.execute(str(user_id))

    # then
    assert result is None


def test_resume_test_without_greeting_returns_greeting():
    """인사 응답이 완료되지 않은 세션을 재개하면 인사를 반환한다"""
    # given
    repo = MockMBTITestSessionRepository()
    human_provider = HumanQuestionProvider()
    ai_provider = MockAIQuestionProvider()
    use_case = ResumeTestUseCase(repo, human_provider, ai_provider)

    user_id = uuid.uuid4()
    session_id = uuid.uuid4()
    session = MBTITestSession(
        id=session_id,
        user_id=user_id,
        status=TestStatus.IN_PROGRESS,
        test_type=TestType.HUMAN,
        created_at=datetime.now(),
        turns=[],
        greeting_completed=False,
    )
    repo.save(session)

    # when
    result = use_case.execute(str(user_id))

    # then
    assert result is not None
    assert result.next_question is not None
    assert "안녕" in result.next_question.content or "MBTI" in result.next_question.content
