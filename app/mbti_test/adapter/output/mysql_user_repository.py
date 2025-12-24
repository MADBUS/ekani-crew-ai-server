from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.mbti_test.application.port.output.user_repository_port import UserRepositoryPort


class MySQLUserRepository(UserRepositoryPort):
    """
    MySQL(SQLAlchemy) 기반 UserRepository.
    - 프로젝트의 User ORM 모델 경로/필드가 확정되지 않았으므로,
      가능한 경로를 시도하고 실패하면 no-op를 허용한다(요구사항).
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def update_mbti(self, user_id: uuid.UUID, mbti: str) -> None:
        """
        User 모델이 있으면 mbti를 업데이트하고, 없으면 no-op.
        """
        user_id_str = str(user_id)

        UserModel = self._try_import_user_model()
        if UserModel is None:
            # 요구사항: 모델/필드가 없으면 no-op 허용
            return

        # id 타입이 str/uuid 무엇이든 비교 가능하도록 우선 문자열로 시도
        user = self._db.get(UserModel, user_id_str)
        if user is None:
            # pk가 uuid로 저장된 프로젝트면 여기서 한 번 더 시도
            try:
                user = self._db.get(UserModel, user_id)
            except Exception:
                user = None

        if user is None:
            return

        # 필드명이 mbti가 아닐 수도 있으니 최소 안전 처리
        if hasattr(user, "mbti"):
            setattr(user, "mbti", mbti)
            self._db.commit()

    def _try_import_user_model(self) -> type[Any] | None:
        """
        프로젝트마다 User ORM 모델 경로가 다를 수 있어, 대표적인 후보를 순서대로 시도한다.
        - 실패해도 no-op 허용이므로 None 반환.
        """
        candidates = [
            ("app.user.infrastructure.model.user_model", "UserModel"),
        ]

        for module_path, attr in candidates:
            try:
                module = __import__(module_path, fromlist=[attr])
                model = getattr(module, attr, None)
                if model is not None:
                    return model
            except Exception:
                continue

        return None
