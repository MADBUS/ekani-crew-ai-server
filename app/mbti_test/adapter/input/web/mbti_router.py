import uuid
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.mbti_test.adapter.input.web.router_ai_question import router as ai_question_router
from app.mbti_test.application.port.input.start_mbti_test_use_case import (
    StartMBTITestUseCase,
    StartMBTITestCommand,
    StartMBTITestResponse as StartMBTITestUseCaseResponse,
)
from app.mbti_test.application.use_case.start_mbti_test_service import StartMBTITestService
from app.mbti_test.application.port.output.mbti_test_session_repository import (
    MBTITestSessionRepositoryPort,
)
from app.mbti_test.application.port.output.question_provider_port import QuestionProviderPort
from app.mbti_test.adapter.output.mysql_mbti_test_session_repository import (
    MySQLMBTITestSessionRepository,
)
from app.mbti_test.adapter.output.openai_ai_question_provider import (
    create_openai_question_provider_from_settings,
)
from config.database import SessionLocal

# 결과 조회용 DI + UseCase + Exceptions
from app.mbti_test.infrastructure.di import get_calculate_final_mbti_usecase
from app.mbti_test.application.use_case.calculate_final_mbti_usecase import CalculateFinalMBTIUseCase
from app.mbti_test.domain.exceptions import SessionNotFound, SessionNotCompleted


mbti_router = APIRouter()
# 기존 /ai-question 라우터 포함
mbti_router.include_router(ai_question_router)

# -----------------------------------------------------------------------------
# Dependencies (실 DI: MySQL Repo + OpenAI Question Provider)
# -----------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mbti_test_session_repository(
    db: Session = Depends(get_db),
) -> MBTITestSessionRepositoryPort:
    return MySQLMBTITestSessionRepository(db=db)


def get_question_provider() -> QuestionProviderPort:
    return create_openai_question_provider_from_settings()


def get_start_mbti_test_use_case(
    repository: MBTITestSessionRepositoryPort = Depends(get_mbti_test_session_repository),
    question_provider: QuestionProviderPort = Depends(get_question_provider),
) -> StartMBTITestUseCase:
    return StartMBTITestService(
        mbti_test_session_repository=repository,
        question_provider=question_provider,
    )


# -----------------------------------------------------------------------------
# API Models
# -----------------------------------------------------------------------------
class StartTestRequest(BaseModel):
    user_id: uuid.UUID


class StartTestResponse(BaseModel):
    session_id: uuid.UUID
    first_question: str


class MBTIResultResponse(BaseModel):
    mbti: str
    dimension_scores: Dict[str, int]
    timestamp: str


# -----------------------------------------------------------------------------
# Router - /start
# -----------------------------------------------------------------------------
@mbti_router.post("/start", response_model=StartTestResponse)
def start_test(
    request: StartTestRequest,
    use_case: StartMBTITestUseCase = Depends(get_start_mbti_test_use_case),
):
    """
    MBTI 테스트 세션을 시작하고 첫 번째 질문을 반환한다.
    """
    command = StartMBTITestCommand(user_id=request.user_id)
    result: StartMBTITestUseCaseResponse = use_case.execute(command)

    return StartTestResponse(
        session_id=result.session.id,
        first_question=result.first_question.content,
    )


# -----------------------------------------------------------------------------
# Router - GET /result/{session_id}
# -----------------------------------------------------------------------------
@mbti_router.get("/result/{session_id}", response_model=MBTIResultResponse)
def get_result(
    session_id: uuid.UUID,
    use_case: CalculateFinalMBTIUseCase = Depends(get_calculate_final_mbti_usecase),
):
    """
    MBTI-4: 결과 조회/계산 엔드포인트
    - SessionNotFound -> 404
    - SessionNotCompleted -> 409
    """
    try:
        result = use_case.execute(session_id=session_id)
        return MBTIResultResponse(
            mbti=result.mbti,
            dimension_scores=result.dimension_scores,
            timestamp=result.timestamp.isoformat(),
        )
    except SessionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SessionNotCompleted as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
