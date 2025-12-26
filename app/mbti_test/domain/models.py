from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Literal


MBTIDimension = Literal["E/I", "S/N", "T/F", "J/P"]


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ChatMessage:
    role: MessageRole
    content: str


@dataclass(frozen=True)
class AIQuestion:
    text: str
    target_dimensions: List[MBTIDimension]


@dataclass(frozen=True)
class AIQuestionResponse:
    turn: int
    questions: List[AIQuestion]


@dataclass(frozen=True)
class GenerateAIQuestionCommand:
    """
    다른 팀(세션/히스토리 담당)이 만든 세션 구조를 건드리지 않기 위해
    이 유스케이스는 session_id + (turn, history)를 외부(요청)에서 주입받는다.
    """
    session_id: str
    turn: int
    history: List[ChatMessage]
    question_mode: Literal["normal", "surprise"] = "normal"


@dataclass(frozen=True)
class AnalyzeAnswerCommand:
    """AI 답변 분석을 위한 커맨드"""
    question: str  # 질문 내용
    answer: str  # 유저 답변
    history: List[ChatMessage]  # 이전 대화 맥락


@dataclass(frozen=True)
class AnalyzeAnswerResponse:
    """AI 답변 분석 결과"""
    dimension: str  # "EI", "SN", "TF", "JP"
    scores: dict  # {"E": 5, "I": 3} 등
    side: str  # 우세한 쪽 ("E", "I", "S", "N", "T", "F", "J", "P")
    score: int  # 우세한 쪽 점수
    reasoning: str  # AI의 분석 이유 (선택적)