from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import UUID, uuid4


MBTIDimension = Literal["EI", "SN", "TF", "JP"]


@dataclass(frozen=True)
class SurpriseAnswer:
    id: UUID
    user_id: UUID
    question_id: str
    answer_text: str
    dimension: MBTIDimension
    score_delta: int
    created_at: datetime

    @staticmethod
    def create(
        user_id: UUID,
        question_id: str,
        answer_text: str,
        dimension: MBTIDimension,
        score_delta: int,
        created_at: Optional[datetime] = None,
    ) -> "SurpriseAnswer":
        return SurpriseAnswer(
            id=uuid4(),
            user_id=user_id,
            question_id=str(question_id),
            answer_text=answer_text,
            dimension=dimension,
            score_delta=int(score_delta),
            created_at=created_at or datetime.now(timezone.utc),
        )
