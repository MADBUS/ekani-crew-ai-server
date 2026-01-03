from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.mbti_test.domain.surprise_answer import SurpriseAnswer, MBTIDimension
from app.mbti_test.application.port.output.surprise_answer_repository import SurpriseAnswerRepository

# 이 프로젝트에 이미 존재하는 모델들을 import 해서 사용
# 아래 2개는 "있을 가능성이 매우 높은" 이름이라, 실제 파일의 클래스명에 맞춰 수정해줘.
from app.mbti_test.infrastructure.mbti_test_models import MBTITestSessionModel
from app.user.infrastructure.model.user_model import UserModel


LetterScores = Dict[str, int]


@dataclass(frozen=True)
class AdjustMBTIResult:
    before_mbti: str
    after_mbti: str
    before_scores: LetterScores
    after_scores: LetterScores
    changed: bool


class AdjustMBTIUseCase:
    def __init__(
        self,
        db: Session,
        user_repository,  # mysql_user_repository.py (update_mbti only)
        surprise_answer_repository: SurpriseAnswerRepository,
        change_threshold_pp: int = 10,
    ):
        self._db = db
        self._user_repo = user_repository
        self._surprise_repo = surprise_answer_repository
        self._threshold = int(change_threshold_pp)

    def execute(self, user_id: UUID, answers: List[SurpriseAnswer]) -> AdjustMBTIResult:
        before_scores = self._load_latest_session_scores(user_id)
        before_mbti = self._load_user_mbti(user_id) or self._scores_to_mbti(before_scores)

        after_scores = dict(before_scores)
        for a in answers:
            after_scores = self._apply_delta(after_scores, a.dimension, a.score_delta)

        after_mbti = self._scores_to_mbti(after_scores)

        changed = self._is_changed(before_mbti, after_mbti, before_scores, after_scores)

        for a in answers:
            self._surprise_repo.save(a)

        if changed:
            self._user_repo.update_mbti(user_id, after_mbti)

        return AdjustMBTIResult(
            before_mbti=before_mbti,
            after_mbti=after_mbti,
            before_scores=before_scores,
            after_scores=after_scores,
            changed=changed,
        )

    # -------- helpers (합의사항: 세션에서 최신 점수 로딩) --------

    def _load_latest_session_scores(self, user_id: UUID) -> LetterScores:
        row = (
            self._db.query(MBTITestSessionModel)
            .filter(MBTITestSessionModel.user_id == str(user_id))
            .order_by(MBTITestSessionModel.created_at.desc())
            .first()
        )

        if row is None:
            return self._default_scores()

        raw = getattr(row, "result_dimension_scores", None)
        if isinstance(raw, dict) and raw:
            return self._normalize_scores(raw)

        return self._default_scores()

    def _load_user_mbti(self, user_id: UUID) -> Optional[str]:
        u = (
            self._db.query(UserModel)
            .filter(UserModel.id == str(user_id))
            .first()
        )
        if u is None:
            return None
        mbti = getattr(u, "mbti", None)
        if isinstance(mbti, str) and mbti.strip():
            return mbti.strip()
        return None

    # -------- scoring logic --------

    def _apply_delta(self, scores: LetterScores, dimension: MBTIDimension, delta: int) -> LetterScores:
        a, b = self._dimension_letters(dimension)  # e.g. ("E","I")
        base_a = int(scores.get(a, 50))
        new_a = self._clamp(base_a + int(delta), 0, 100)
        new_b = 100 - new_a

        out = dict(scores)
        out[a] = new_a
        out[b] = new_b
        return out

    def _scores_to_mbti(self, scores: LetterScores) -> str:
        e = "E" if scores["E"] >= scores["I"] else "I"
        s = "S" if scores["S"] >= scores["N"] else "N"
        t = "T" if scores["T"] >= scores["F"] else "F"
        j = "J" if scores["J"] >= scores["P"] else "P"
        return f"{e}{s}{t}{j}"

    def _is_changed(
        self,
        before_mbti: str,
        after_mbti: str,
        before_scores: LetterScores,
        after_scores: LetterScores,
    ) -> bool:
        if before_mbti == after_mbti:
            return False

        # 어떤 축에서 글자가 바뀌었는지 보고, 그 축의 "첫 글자" 변화량으로 임계값 판정
        dims: List[Tuple[MBTIDimension, str]] = [
            ("EI", "E"),
            ("SN", "S"),
            ("TF", "T"),
            ("JP", "J"),
        ]

        for i, (dim, first_letter) in enumerate(dims):
            if len(before_mbti) < 4:
                continue
            if before_mbti[i] != after_mbti[i]:
                diff = abs(after_scores[first_letter] - before_scores[first_letter])
                if diff >= self._threshold:
                    return True

        return False

    # -------- utilities --------

    def _dimension_letters(self, dimension: MBTIDimension) -> Tuple[str, str]:
        if dimension == "EI":
            return ("E", "I")
        if dimension == "SN":
            return ("S", "N")
        if dimension == "TF":
            return ("T", "F")
        return ("J", "P")

    def _default_scores(self) -> LetterScores:
        return {"E": 50, "I": 50, "S": 50, "N": 50, "T": 50, "F": 50, "J": 50, "P": 50}

    def _normalize_scores(self, raw: Dict) -> LetterScores:
        # raw may include strings/floats -> int clamp
        def pick(k: str) -> int:
            try:
                return self._clamp(int(raw.get(k, 50)), 0, 100)
            except Exception:
                return 50

        out = {k: pick(k) for k in ["E", "I", "S", "N", "T", "F", "J", "P"]}

        # enforce pair sum=100
        out["I"] = 100 - out["E"]
        out["N"] = 100 - out["S"]
        out["F"] = 100 - out["T"]
        out["P"] = 100 - out["J"]

        return out

    def _clamp(self, v: int, lo: int, hi: int) -> int:
        return max(lo, min(hi, v))
