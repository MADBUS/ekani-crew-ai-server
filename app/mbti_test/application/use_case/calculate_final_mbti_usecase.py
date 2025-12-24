from __future__ import annotations

import uuid

from app.mbti_test.application.port.output.mbti_test_session_repository import (
    MBTITestSessionRepositoryPort,
)
from app.mbti_test.application.port.output.user_repository_port import UserRepositoryPort
from app.mbti_test.domain.exceptions import SessionNotCompleted, SessionNotFound
from app.mbti_test.domain.mbti_result import MBTIResult

# 차원별 양쪽 선택지 정의
DIM_SIDES: dict[str, tuple[str, str]] = {
    "EI": ("E", "I"),
    "SN": ("S", "N"),
    "TF": ("T", "F"),
    "JP": ("J", "P"),
}


class CalculateFinalMBTIUseCase:
    """
    MBTI-4: 12개 답변 누적 세션을 기반으로 최종 MBTI 결과를 계산하고 저장한다.
    - DB/ORM을 모르기 위해 Port(Repository 인터페이스)에만 의존한다.
    """

    def __init__(
        self,
        session_repo: MBTITestSessionRepositoryPort,
        user_repo: UserRepositoryPort,
        required_answers: int = 12,
    ) -> None:
        self._session_repo = session_repo
        self._user_repo = user_repo
        self._required_answers = required_answers

    def execute(self, session_id: uuid.UUID) -> MBTIResult:
        # a) 확장 세션 조회
        session = self._session_repo.find_extended_by_id(session_id)
        if session is None:
            raise SessionNotFound(f"session not found: {session_id}")

        # b) 답변 수 검증
        if len(session.answers) < self._required_answers:
            raise SessionNotCompleted(
                f"need {self._required_answers} answers, got {len(session.answers)}"
            )

        # c) 점수 합산 (잘못된 dimension/side는 skip)
        scores: dict[str, int] = {}
        for dim, (a, b) in DIM_SIDES.items():
            scores[a] = 0
            scores[b] = 0

        for ans in session.answers:
            # 기대 형태: {"dimension":"EI","side":"E","score":1}
            dim = ans.get("dimension")
            side = ans.get("side")
            score_raw = ans.get("score", 1)

            if dim not in DIM_SIDES:
                continue

            a, b = DIM_SIDES[dim]
            if side not in (a, b):
                continue

            try:
                score = int(score_raw)
            except (TypeError, ValueError):
                continue

            scores[side] += score

        # d) 퍼센트 변환 + 4글자 결정
        dimension_scores: dict[str, int] = {}
        letters: list[str] = []

        for dim, (a, b) in DIM_SIDES.items():
            sa = scores.get(a, 0)
            sb = scores.get(b, 0)
            total = sa + sb

            if total == 0:
                pa, pb = 50, 50
            else:
                pa = round(sa * 100 / total)
                pb = 100 - pa

            dimension_scores[a] = pa
            dimension_scores[b] = pb
            letters.append(a if pa >= pb else b)

        # e) 결과 생성
        result = MBTIResult(
            mbti="".join(letters),
            dimension_scores=dimension_scores,
        )

        # f) 세션 결과 저장 + COMPLETED 처리
        self._session_repo.save_result_and_complete(session_id, result)

        # g) 유저 mbti 업데이트
        self._user_repo.update_mbti(session.user_id, result.mbti)

        # h) 결과 반환
        return result
