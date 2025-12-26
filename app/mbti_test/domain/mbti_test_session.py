
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional


class TestType(Enum):
    HUMAN = "human"
    AI = "ai"


class TestStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


@dataclass
class Turn:
    """MBTI 테스트의 한 턴 (질문 + 답변 + 점수)"""
    turn_number: int
    question: str
    answer: str
    dimension: str  # "EI", "SN", "TF", "JP"
    scores: Dict[str, int]  # {"E": 5, "I": 3} - 양쪽 점수
    side: str  # 우세한 쪽 ("E", "I", "S", "N", "T", "F", "J", "P")
    score: int  # 우세한 쪽의 점수


@dataclass
class MBTITestSession:
    id: uuid.UUID
    user_id: uuid.UUID
    test_type: TestType
    status: TestStatus
    created_at: datetime
    turns: List[Turn] = field(default_factory=list)  # 턴 히스토리 (질문+답변+점수)
    current_question_index: int = 0
    selected_human_questions: List[str] = field(default_factory=list)  # 세션 시작 시 랜덤 선택된 12개 질문
    greeting_completed: bool = False  # 인사 응답 완료 여부
    human_test_result: Dict | None = None  # 사람 기반 테스트 결과
    pending_question: Optional[str] = None  # 다음 턴에 저장될 질문 (아직 답변 안 받음)

    @property
    def questions(self) -> List[str]:
        """하위 호환성을 위한 질문 리스트"""
        return [turn.question for turn in self.turns]

    @property
    def answers(self) -> List[Dict]:
        """하위 호환성을 위한 답변 리스트 (CalculateFinalMBTIUseCase 호환)"""
        return [
            {
                "content": turn.answer,
                "dimension": turn.dimension,
                "side": turn.side,
                "score": turn.score,
            }
            for turn in self.turns
        ]
