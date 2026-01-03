import uuid
from typing import Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session
from config.database import SessionLocal
from app.auth.adapter.input.web.auth_dependency import get_current_user_id
from app.mbti_test.application.port.input.start_mbti_test_use_case import StartMBTITestCommand
from app.mbti_test.application.port.input.answer_question_use_case import AnswerQuestionCommand
from app.mbti_test.application.use_case.start_mbti_test_service import StartMBTITestService
from app.mbti_test.application.use_case.answer_question_service import AnswerQuestionService
from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.application.port.ai_question_provider_port import AIQuestionProviderPort
from app.mbti_test.infrastructure.repository.mysql_mbti_test_session_repository import MySQLMBTITestSessionRepository
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
from app.mbti_test.adapter.output.openai_ai_question_provider import create_openai_question_provider_from_settings
from app.mbti_test.adapter.output.mysql_user_repository import MySQLUserRepository

# 결과 조회용 DI + UseCase + Exceptions
from app.mbti_test.application.use_case.calculate_final_mbti_usecase import CalculateFinalMBTIUseCase
from app.mbti_test.domain.exceptions import SessionNotFound, SessionNotCompleted
from app.mbti_test.application.port.output.user_repository_port import UserRepositoryPort

#응답보정용
from app.mbti_test.domain.surprise_answer import MBTIDimension, SurpriseAnswer
from app.mbti_test.adapter.output.mysql_surprise_answer_repository import MySQLSurpriseAnswerRepository
from app.mbti_test.application.use_case.adjust_mbti_usecase import AdjustMBTIUseCase

mbti_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def get_session_repository(db: Session = Depends(get_db)) -> MBTITestSessionRepositoryPort:
    return MySQLMBTITestSessionRepository(db=db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryPort:
    return MySQLUserRepository(db=db)

def get_human_question_provider() -> HumanQuestionProvider:
    return HumanQuestionProvider()

def get_ai_question_provider() -> AIQuestionProviderPort:
    return create_openai_question_provider_from_settings()

def get_calculate_final_mbti_usecase_mysql(
    db: Session = Depends(get_db),
) -> CalculateFinalMBTIUseCase:
    return CalculateFinalMBTIUseCase(
        session_repo=MySQLMBTITestSessionRepository(db=db),
        user_repo=MySQLUserRepository(db=db),
        required_answers=12,  # 필요 시 24로 조정
    )
class SurpriseAnswerRequest(BaseModel):
    question_id: str = Field(..., min_length=1, max_length=64)
    answer_text: str = Field(..., min_length=1, max_length=2000)
    dimension: MBTIDimension
    score_delta: int = Field(..., ge=-100, le=100)


class SurpriseAnswerResponse(BaseModel):
    before_mbti: str
    after_mbti: str
    before_scores: Dict[str, int]
    after_scores: Dict[str, int]
    changed: bool

# ... /start, /chat은 동일하게 _session_repository 사용 ...
class ChatRequest(BaseModel):
    content: str

class MBTIResultResponse(BaseModel):
    mbti: str
    dimension_scores: Dict[str, int]
    timestamp: str

@mbti_router.post("/start")
async def start_mbti_test(
    user_id: str = Depends(get_current_user_id),
    session_repository: MBTITestSessionRepositoryPort = Depends(get_session_repository),
    human_question_provider: HumanQuestionProvider = Depends(get_human_question_provider),
):
    use_case = StartMBTITestService(session_repository, human_question_provider)
    command = StartMBTITestCommand(user_id=uuid.UUID(user_id))
    result = use_case.execute(command)
    return jsonable_encoder({"session": result.session, "first_question": result.first_question})

@mbti_router.post("/{mbti_session_id}/answer")
async def answer_question(
    mbti_session_id: str,
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session_repository: MBTITestSessionRepositoryPort = Depends(get_session_repository),
    human_question_provider: HumanQuestionProvider = Depends(get_human_question_provider),
    ai_question_provider: AIQuestionProviderPort = Depends(get_ai_question_provider),
):
    use_case = AnswerQuestionService(
        session_repository=session_repository,
        human_question_provider=human_question_provider,
        ai_question_provider=ai_question_provider,
    )
    try:
        command = AnswerQuestionCommand(session_id=mbti_session_id, answer=request.content)
        result = use_case.execute(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return jsonable_encoder({
        "question_number": result.question_number,
        "total_questions": result.total_questions,
        "next_question": result.next_question,
        "is_completed": result.is_completed,
        "analysis_result": result.analysis_result,
        "partial_analysis_result": result.partial_analysis_result,
    })


@mbti_router.post("/{mbti_session_id}/chat")
async def answer_question_chat(
    mbti_session_id: str,
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    session_repository: MBTITestSessionRepositoryPort = Depends(get_session_repository),
    human_question_provider: HumanQuestionProvider = Depends(get_human_question_provider),
    ai_question_provider: AIQuestionProviderPort = Depends(get_ai_question_provider),
):
    use_case = AnswerQuestionService(
        session_repository=session_repository,
        human_question_provider=human_question_provider,
        ai_question_provider=ai_question_provider,
    )
    try:
        command = AnswerQuestionCommand(session_id=mbti_session_id, answer=request.content)
        result = use_case.execute(command)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return jsonable_encoder({
        "question_number": result.question_number,
        "total_questions": result.total_questions,
        "next_question": result.next_question,
        "is_completed": result.is_completed,
        "analysis_result": result.analysis_result,
        "partial_analysis_result": result.partial_analysis_result,
    })


@mbti_router.get("/result/{mbti_session_id}", response_model=MBTIResultResponse)
def get_result(
    mbti_session_id: uuid.UUID,
    use_case: CalculateFinalMBTIUseCase = Depends(get_calculate_final_mbti_usecase_mysql),  # ⬅️ 인메모리 DI로 교체
):
    try:
        result = use_case.execute(session_id=mbti_session_id)
        return MBTIResultResponse(
            mbti=result.mbti,
            dimension_scores=result.dimension_scores,
            timestamp=result.timestamp.isoformat(),
        )
    except SessionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SessionNotCompleted as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@mbti_router.post("/mbti/surprise/answer", response_model=SurpriseAnswerResponse)
def post_surprise_answer(
    body: SurpriseAnswerRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user_repo = MySQLUserRepository(db)  # update_mbti only
    surprise_repo = MySQLSurpriseAnswerRepository(db)
    usecase = AdjustMBTIUseCase(
        db=db,
        user_repository=user_repo,
        surprise_answer_repository=surprise_repo,
        change_threshold_pp=10,
    )

    answer = SurpriseAnswer.create(
        user_id=user_id,
        question_id=body.question_id,
        answer_text=body.answer_text,
        dimension=body.dimension,
        score_delta=body.score_delta,
    )

    result = usecase.execute(user_id=user_id, answers=[answer])

    return SurpriseAnswerResponse(
        before_mbti=result.before_mbti,
        after_mbti=result.after_mbti,
        before_scores=result.before_scores,
        after_scores=result.after_scores,
        changed=result.changed,
    )