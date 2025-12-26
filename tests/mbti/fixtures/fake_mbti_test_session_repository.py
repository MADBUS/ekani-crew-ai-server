import uuid
from typing import Dict

from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.domain.mbti_test_session import MBTITestSession, TestStatus
from app.mbti_test.domain.mbti_result import MBTIResult, MBTITestSessionExtended, SessionStatus


class FakeMBTITestSessionRepository(MBTITestSessionRepositoryPort):
    def __init__(self):
        self._sessions: Dict[uuid.UUID, MBTITestSession] = {}

    def save(self, session: MBTITestSession) -> MBTITestSession:
        self._sessions[session.id] = session
        return session

    def find_by_id(self, session_id: uuid.UUID) -> MBTITestSession | None:
        return self._sessions.get(session_id)

    def find_all(self) -> list[MBTITestSession]:
        return list(self._sessions.values())

    def add_answer(self, session_id: uuid.UUID, answer: dict) -> None:
        session = self._sessions.get(session_id)
        if session:
            # Note: This method is deprecated with the new Turn-based structure
            pass

    def find_extended_by_id(self, session_id: uuid.UUID) -> MBTITestSessionExtended | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        status = SessionStatus.COMPLETED if session.status == TestStatus.COMPLETED else SessionStatus.IN_PROGRESS
        return MBTITestSessionExtended(
            id=str(session.id),
            user_id=str(session.user_id),
            status=status,
            answers=list(session.answers),
            result=None
        )

    def save_result_and_complete(self, session_id: uuid.UUID, result: MBTIResult) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.status = TestStatus.COMPLETED
