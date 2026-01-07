from dataclasses import dataclass
from typing import Optional

from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.application.port.ai_question_provider_port import AIQuestionProviderPort
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
from app.mbti_test.domain.mbti_test_session import MBTITestSession
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource


HUMAN_QUESTION_COUNT = 12


@dataclass
class ResumeTestResult:
    session: MBTITestSession
    next_question: MBTIMessage


class ResumeTestUseCase:
    def __init__(
        self,
        session_repository: MBTITestSessionRepositoryPort,
        human_question_provider: HumanQuestionProvider,
        ai_question_provider: AIQuestionProviderPort,
    ):
        self._session_repository = session_repository
        self._human_question_provider = human_question_provider
        self._ai_question_provider = ai_question_provider

    def execute(self, user_id: str) -> Optional[ResumeTestResult]:
        session = self._session_repository.find_by_user_id_and_status(user_id, "IN_PROGRESS")
        if not session:
            return None

        session.selected_human_questions = self._human_question_provider.select_random_questions(
            seed=str(session.id)
        )
        session.current_question_index = len(session.turns)

        current_index = session.current_question_index

        if not session.greeting_completed:
            next_question = self._human_question_provider.get_greeting()
        elif current_index < HUMAN_QUESTION_COUNT:
            next_question = self._human_question_provider.get_question_from_list(
                current_index, session.selected_human_questions
            )
        else:
            next_question = MBTIMessage(
                role=MessageRole.ASSISTANT,
                content=session.pending_question or "",
                source=MessageSource.AI,
            )

        return ResumeTestResult(session=session, next_question=next_question)