from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.mbti_test.application.port.output.mbti_test_session_repository import (
    MBTITestSessionRepositoryPort,
)
from app.mbti_test.domain.mbti_result import MBTIResult, MBTITestSessionExtended, SessionStatus
from app.mbti_test.domain.mbti_test_session import MBTITestSession
from app.mbti_test.infrastructure.mbti_test_models import MBTITestSessionModel


class MySQLMBTITestSessionRepository(MBTITestSessionRepositoryPort):
    """
    MySQL(SQLAlchemy) 기반 세션 레포지토리.
    - Port(인터페이스) 시그니처를 그대로 구현한다.
    - pydantic MBTITestSession은 '가능하면' 매핑해서 유지하고,
      MBTI-4는 Extended 타입을 중심으로 읽고/쓴다.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    # -------------------------
    # 내부 유틸
    # -------------------------

    @staticmethod
    def _uuid_to_str(value: uuid.UUID) -> str:
        return str(value)

    @staticmethod
    def _str_to_uuid(value: str) -> uuid.UUID:
        return uuid.UUID(value)

    def _row_to_extended(self, row: MBTITestSessionModel) -> MBTITestSessionExtended:
        result_obj: MBTIResult | None = None
        if row.result_mbti and row.result_dimension_scores and row.result_timestamp:
            result_obj = MBTIResult(
                mbti=row.result_mbti,
                dimension_scores=row.result_dimension_scores,
                timestamp=row.result_timestamp,
            )

        return MBTITestSessionExtended(
            id=row.id,
            user_id=row.user_id,
            status=SessionStatus(row.status),
            answers=row.answers or [],
            result=result_obj,
        )

    def _row_to_pydantic_session(self, row: MBTITestSessionModel) -> MBTITestSession:
        """
        기존 pydantic MBTITestSession으로 최대한 매핑한다.
        - MBTITestSession의 실제 필드 구조를 완전히 모르는 상태이므로,
          최소한의 공통 필드(id/user_id/status/answers/result*)만 시도한다.
        """
        payload: dict[str, Any] = {
            "id": row.id,
            "user_id": row.user_id,
            "status": row.status,
            # 기존 세션에 answers 필드가 없을 수도 있으므로 일단 포함
            "answers": row.answers or [],
            # 결과도 포함(없으면 None)
            "result_mbti": row.result_mbti,
            "result_dimension_scores": row.result_dimension_scores,
            "result_timestamp": row.result_timestamp,
        }

        # pydantic v2: model_validate / v1: parse_obj 대응
        if hasattr(MBTITestSession, "model_validate"):
            return MBTITestSession.model_validate(payload)  # type: ignore[attr-defined]
        if hasattr(MBTITestSession, "parse_obj"):
            return MBTITestSession.parse_obj(payload)  # type: ignore[attr-defined]

        # 최후 fallback: 생성자 호출(필드가 다르면 에러 날 수 있음)
        return MBTITestSession(**payload)  # type: ignore[call-arg]

    def _get_row(self, session_id: uuid.UUID) -> MBTITestSessionModel | None:
        return (
            self._db.query(MBTITestSessionModel)
            .filter(MBTITestSessionModel.id == self._uuid_to_str(session_id))
            .one_or_none()
        )

    # -------------------------
    # Port 구현 (기존 메서드)
    # -------------------------

    def save(self, session: MBTITestSession) -> MBTITestSession:
        """
        기존 pydantic MBTITestSession 저장.
        - 가능하면 row upsert로 저장하고, 저장된 pydantic 세션을 반환한다.
        """
        # pydantic 객체에서 dict 꺼내기(v1/v2 대응)
        if hasattr(session, "model_dump"):
            data = session.model_dump()  # type: ignore[attr-defined]
        elif hasattr(session, "dict"):
            data = session.dict()  # type: ignore[attr-defined]
        else:
            data = session.__dict__

        session_id = data.get("id")
        user_id = data.get("user_id")

        # UUID/str 어느 쪽이든 문자열로 통일해서 저장
        sid_str = str(session_id) if session_id is not None else None
        uid_str = str(user_id) if user_id is not None else None

        if sid_str is None or uid_str is None:
            # 기존 도메인 설계상 id/user_id는 있어야 정상이라, 없으면 그대로 예외가 나도록 둔다.
            raise ValueError("MBTITestSession must contain id and user_id")

        row = self._db.get(MBTITestSessionModel, sid_str)
        if row is None:
            row = MBTITestSessionModel(
                id=sid_str,
                user_id=uid_str,
                status=str(data.get("status", SessionStatus.IN_PROGRESS.value)),
                answers=list(data.get("answers", [])) if data.get("answers") is not None else [],
                result_mbti=data.get("result_mbti"),
                result_dimension_scores=data.get("result_dimension_scores"),
                result_timestamp=data.get("result_timestamp"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self._db.add(row)
        else:
            # 업데이트(존재하는 키만 반영)
            if "user_id" in data and uid_str:
                row.user_id = uid_str
            if "status" in data and data["status"] is not None:
                row.status = str(data["status"])
            if "answers" in data and data["answers"] is not None:
                row.answers = list(data["answers"])
            if "result_mbti" in data:
                row.result_mbti = data.get("result_mbti")
            if "result_dimension_scores" in data:
                row.result_dimension_scores = data.get("result_dimension_scores")
            if "result_timestamp" in data:
                row.result_timestamp = data.get("result_timestamp")
            row.updated_at = datetime.utcnow()

        self._db.commit()
        self._db.refresh(row)
        return self._row_to_pydantic_session(row)

    def find_by_id(self, session_id: uuid.UUID) -> MBTITestSession | None:
        """
        기존 pydantic MBTITestSession 조회.
        """
        row = self._get_row(session_id)
        if row is None:
            return None
        return self._row_to_pydantic_session(row)

    # -------------------------
    # Port 구현 (MBTI-4 확장 메서드)
    # -------------------------

    def find_extended_by_id(self, session_id: uuid.UUID) -> MBTITestSessionExtended | None:
        row = self._get_row(session_id)
        if row is None:
            return None
        return self._row_to_extended(row)

    def add_answer(self, session_id: uuid.UUID, answer: dict) -> None:
        """
        세션 조회 -> answers append -> 저장.
        - 잘못된 answer 구조 검증은 UseCase/도메인에서 하도록 두고,
          여기서는 단순 저장에 집중한다.
        """
        row = self._get_row(session_id)
        if row is None:
            # 포트 시그니처 상 예외는 UseCase에서 처리(여긴 단순 구현)
            raise ValueError(f"session not found: {session_id}")

        current = row.answers or []
        current.append(answer)
        row.answers = current
        row.updated_at = datetime.utcnow()

        self._db.commit()

    def save_result_and_complete(self, session_id: uuid.UUID, result: MBTIResult) -> None:
        """
        결과 저장 + 상태 COMPLETED 처리.
        """
        row = self._get_row(session_id)
        if row is None:
            raise ValueError(f"session not found: {session_id}")

        row.status = SessionStatus.COMPLETED.value
        row.result_mbti = result.mbti
        row.result_dimension_scores = result.dimension_scores
        # timestamp는 dataclass에서 UTC now로 생성되므로 그대로 저장
        row.result_timestamp = result.timestamp.replace(tzinfo=None)
        row.updated_at = datetime.utcnow()

        self._db.commit()
