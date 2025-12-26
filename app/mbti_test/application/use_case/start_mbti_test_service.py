import uuid
from datetime import datetime

from app.mbti_test.application.port.input.start_mbti_test_use_case import (
    StartMBTITestUseCase,
    StartMBTITestCommand,
    StartMBTITestResponse,
)
from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestStatus


class StartMBTITestService(StartMBTITestUseCase):
    def __init__(
        self,
        mbti_test_session_repository: MBTITestSessionRepositoryPort,
        human_question_provider: HumanQuestionProvider,
    ):
        self._mbti_test_session_repository = mbti_test_session_repository
        self._human_question_provider = human_question_provider

    def execute(self, command: StartMBTITestCommand) -> StartMBTITestResponse:
        # 1. 차원별 3개씩 랜덤 선택 (총 12개)
        selected_questions = self._human_question_provider.select_random_questions()

        # 2. 눈치 인사 메시지 가져오기
        greeting = self._human_question_provider.get_greeting()

        # 3. 세션 생성 (선택된 질문 저장, greeting_completed=False)
        session = MBTITestSession(
            id=uuid.uuid4(),
            user_id=command.user_id,
            test_type=command.test_type,
            status=TestStatus.IN_PROGRESS,
            created_at=datetime.now(),
            selected_human_questions=selected_questions,  # 랜덤 선택된 12개 질문
            greeting_completed=False,  # 아직 인사 응답 안 받음
        )

        self._mbti_test_session_repository.save(session)

        return StartMBTITestResponse(
            session=session,
            first_question=greeting,  # greeting을 first_question으로 반환
        )