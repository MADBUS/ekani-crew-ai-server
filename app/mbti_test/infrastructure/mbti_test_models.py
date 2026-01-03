from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from sqlalchemy.sql import func

# 프로젝트 공용 Base를 사용 (요구사항)
from config.database import Base


def _utcnow() -> datetime:
    # DB default가 아니라 Python default로도 UTC 보장(선택)
    return datetime.now(timezone.utc).replace(tzinfo=None)


class MBTITestSessionModel(Base):
    """
    mbti_test_sessions 테이블 ORM 모델.
    - MBTI-4(Extended 세션 answers/result)를 저장하기 위해 answers/result 컬럼이 포함된다.
    """

    __tablename__ = "mbti_test_sessions"

    # 요구사항: UUID(pk)
    # MySQL에서 UUID를 실제로 어떻게 저장하는지(CHAR(36)/BINARY(16))는 프로젝트 설정에 따라 다를 수 있어
    # 여기서는 호환성 좋은 CHAR(36)로 UUID 문자열 저장 방식을 사용한다.
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    status: Mapped[str] = mapped_column(String(32), nullable=False)

    # Extended answers 리스트 저장
    answers: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # 결과 저장(분리 컬럼)
    result_mbti: Mapped[str | None] = mapped_column(String(8), nullable=True)
    result_dimension_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    result_timestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=_utcnow, onupdate=_utcnow
    )


class SurpriseAnswerModel(Base):
    __tablename__ = "surprise_answers"

    id = Column(String(36), primary_key=True)          # UUID string
    user_id = Column(String(36), nullable=False, index=True)
    question_id = Column(String(64), nullable=False)
    answer_text = Column(String(2000), nullable=False)
    dimension = Column(String(2), nullable=False)      # EI/SN/TF/JP
    score_delta = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())