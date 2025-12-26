from __future__ import annotations

from abc import ABC, abstractmethod

from app.mbti_test.domain.models import (
    AIQuestionResponse,
    GenerateAIQuestionCommand,
    AnalyzeAnswerCommand,
    AnalyzeAnswerResponse,
)


class AIQuestionProviderPort(ABC):
    @abstractmethod
    def generate_questions(self, command: GenerateAIQuestionCommand) -> AIQuestionResponse:
        """
        LLM 기반으로 다음 질문(1~2개)을 생성한다.
        - JSON 스키마 강제
        - Markdown fence 제거/정규화
        """
        raise NotImplementedError

    @abstractmethod
    def analyze_answer(self, command: AnalyzeAnswerCommand) -> AnalyzeAnswerResponse:
        """
        LLM 기반으로 유저 답변을 분석하여 MBTI 점수를 반환한다.
        - 질문 맥락을 고려하여 어떤 차원(EI, SN, TF, JP)에 해당하는지 판단
        - 해당 차원의 양쪽 점수를 계산
        """
        raise NotImplementedError
