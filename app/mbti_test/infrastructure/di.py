from __future__ import annotations

"""
MBTI-4용 DI.
- UseCase는 DB/ORM을 모르므로, 여기서 SessionLocal로 repo를 구성해 주입한다.
- Router는 이 함수를 Depends로 호출할 수 있다(단, Router 수정은 이번 단계에서 하지 않음).
"""

from typing import Generator

from config.database import SessionLocal

from app.mbti_test.infrastructure.repository.mysql_mbti_test_session_repository import (
    MySQLMBTITestSessionRepository,
)
from app.user.infrastructure.repository.mysql_user_repository import MySQLUserRepository
from app.mbti_test.application.use_case.calculate_final_mbti_usecase import (
    CalculateFinalMBTIUseCase,
)


def _get_db():
    """
    세션 생명주기 관리용 헬퍼.
    - FastAPI에 직접 의존하진 않지만, 동일한 패턴(try/finally)을 사용한다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_calculate_final_mbti_usecase() -> CalculateFinalMBTIUseCase:
    """
    왜 필요?
    - CalculateFinalMBTIUseCase 실행 시점에 MySQL Repository를 주입하기 위해.
    - Router/Service 계층은 UseCase 생성 디테일을 몰라도 된다.
    """
    # generator를 직접 소비(프레임워크 비의존으로 세션 종료 보장)
    gen = _get_db()
    db = next(gen)
    try:
        session_repo = MySQLMBTITestSessionRepository(db=db)
        user_repo = MySQLUserRepository(db=db)
        return CalculateFinalMBTIUseCase(
            session_repo=session_repo,
            user_repo=user_repo,
            required_answers=24,
        )
    finally:
        # _get_db()의 finally를 실행
        try:
            next(gen)
        except StopIteration:
            pass
