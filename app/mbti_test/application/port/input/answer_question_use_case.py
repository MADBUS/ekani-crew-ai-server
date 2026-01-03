from abc import ABC, abstractmethod
from pydantic import BaseModel, ConfigDict

from app.mbti_test.domain.mbti_message import MBTIMessage


class AnswerQuestionCommand(BaseModel):
    session_id: str
    answer: str


class AnswerQuestionResponse(BaseModel):
    question_number: int
    total_questions: int
    next_question: MBTIMessage | None
    is_completed: bool
    analysis_result: dict | None = None
    partial_analysis_result: dict | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class AnswerQuestionUseCase(ABC):
    @abstractmethod
    def execute(self, command: AnswerQuestionCommand) -> AnswerQuestionResponse:
        pass