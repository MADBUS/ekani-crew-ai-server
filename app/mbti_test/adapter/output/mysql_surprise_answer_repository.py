from __future__ import annotations

from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.mbti_test.application.port.output.surprise_answer_repository import SurpriseAnswerRepository
from app.mbti_test.domain.surprise_answer import SurpriseAnswer
from app.mbti_test.infrastructure.mbti_test_models import SurpriseAnswerModel


class MySQLSurpriseAnswerRepository(SurpriseAnswerRepository):
    def __init__(self, db: Session):
        self._db = db

    def save(self, answer: SurpriseAnswer) -> None:
        row = SurpriseAnswerModel(
            id=str(answer.id),
            user_id=str(answer.user_id),
            question_id=str(answer.question_id),
            answer_text=answer.answer_text,
            dimension=answer.dimension,
            score_delta=int(answer.score_delta),
        )
        self._db.add(row)
        self._db.commit()

    def find_by_user(self, user_id: UUID) -> List[SurpriseAnswer]:
        rows = (
            self._db.query(SurpriseAnswerModel)
            .filter(SurpriseAnswerModel.user_id == str(user_id))
            .order_by(SurpriseAnswerModel.created_at.asc())
            .all()
        )

        result: List[SurpriseAnswer] = []
        for r in rows:
            result.append(
                SurpriseAnswer(
                    id=UUID(r.id),
                    user_id=UUID(r.user_id),
                    question_id=r.question_id,
                    answer_text=r.answer_text,
                    dimension=r.dimension,  # type: ignore
                    score_delta=int(r.score_delta),
                    created_at=r.created_at,
                )
            )
        return result
