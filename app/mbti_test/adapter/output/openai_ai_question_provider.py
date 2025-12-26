from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List

from app.mbti_test.application.port.ai_question_provider_port import AIQuestionProviderPort
from app.mbti_test.domain.models import (
    AIQuestion,
    AIQuestionResponse,
    GenerateAIQuestionCommand,
    AnalyzeAnswerCommand,
    AnalyzeAnswerResponse,
    MessageRole,
)

def _turn_target_dimensions(turn: int) -> List[str]:
    # 턴 목표: 1 라포/자가진단, 2 E/I, 3 S/N, 4 T/F, 5 J/P
    if turn == 1:
        return []  # 라포/자가진단은 특정 차원 강제X (다만 질문은 해야 함)
    if turn == 2:
        return ["E/I"]
    if turn == 3:
        return ["S/N"]
    if turn == 4:
        return ["T/F"]
    if turn == 5:
        return ["J/P"]
    return []


def _strip_markdown_fences(text: str) -> str:
    # response_format=json_object 를 쓰더라도 가끔 fence가 섞일 수 있어 방어
    text = text.strip()
    # ```json ... ``` or ``` ... ```
    fence_pattern = r"^```(?:json)?\s*(.*?)\s*```$"
    m = re.match(fence_pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def _parse_json_object(text: str) -> Dict[str, Any]:
    cleaned = _strip_markdown_fences(text)
    return json.loads(cleaned)


def _build_system_prompt() -> str:
    # 사과/AI 자기 언급 금지, 1~2개 질문, 2~3문장, 구체 사례 요청, 부족하면 예시 재요청
    return (
        "너는 MBTI 테스트를 진행하는 질문자다.\n"
        "규칙:\n"
        "- 매 턴 질문은 1~2개만 만든다.\n"
        "- 각 질문은 2~3문장으로, 사용자의 '구체 사례'를 요청한다.\n"
        "- 정보가 부족하면 '구체 예시 한 개 더'를 요청하는 재질문을 포함한다.\n"
        "- 사과하지 말고, AI/모델/시스템 같은 자기 언급을 하지 않는다.\n"
        "- 출력은 반드시 JSON 하나이며, 아래 스키마를 지킨다.\n"
        '  {\"questions\":[{\"text\":\"...\", \"target_dimensions\":[\"E/I\"]}], \"turn\": n}\n'
        "- 질문 외의 설명/장식 문구를 넣지 않는다.\n"
        "톤/스타일:\n"
        "- 한국어 캐주얼 반말, 친근한 말투. 호칭 없이 '너'.\n"
        "- 이모지 1~2개와 감탄사(헐, ㅋㅋ 등) 섞기.\n"
        "- 상황 제시 후 선택/묘사 유도형 질문으로 마무리(물음표 필수).\n"
        "- 생활감 있는 소재(모임, 여행, SNS, 주말 계획 등)를 사용.\n"
        "- target_dimensions에 맞는 상황/어휘 선택(E/I: 사람 많은 자리 vs 혼자 등).\n"
    )


def _build_user_prompt(command: GenerateAIQuestionCommand) -> str:
    targets = _turn_target_dimensions(command.turn)
    mode_line = (
        "질문 모드: 돌발(surprise)\n"
        "- 질문에는 반드시 '예상 밖 상황/제약'을 1개 이상 포함해라. (시간 압박/역할 강제/갑작스런 변수/낯선 사람·환경)\n"
        "- 평범한 MBTI 질문(모임이 좋나, 혼자가 좋나 등)으로 묻지 마라.\n"
        "- 사용자가 둘 중 하나를 선택해야 하는 형태로 묻고, 이유 + 실제 경험 예시 1개를 요구해라.\n"
        if command.question_mode == "surprise"
        else
        "질문 모드: 일반(normal)\n"
        "- 대화 맥락을 이어서 자연스럽게 후속 질문을 해라.\n"
    )

    # 턴 1은 라포/자가진단이지만, 그래도 차원 단서를 살짝 볼 수 있게 설계 가능
    target_line = (
        f"이번 턴 번호: {command.turn}\n"
        f"이번 턴 목표 차원: {targets if targets else '라포/자가진단(특정 차원 강제 없음)'}\n"
    )

    # 히스토리는 최근 메시지 위주로 충분 (세션 담당이 길이 제어 가능)
    history_lines = []
    for msg in command.history:
        role = msg.role.value if isinstance(msg.role, MessageRole) else str(msg.role)
        history_lines.append(f"{role}: {msg.content}")

    history_block = "\n".join(history_lines).strip() or "(히스토리 없음)"

    return (
        f"{mode_line}\n"
        f"{target_line}"
        "대화 히스토리:\n"
        f"{history_block}\n"
        "위 히스토리를 바탕으로 다음 질문 JSON만 출력해라."
    )


def _build_analysis_system_prompt() -> str:
    """답변 분석용 시스템 프롬프트"""
    return (
        "너는 MBTI 전문 분석가다. 사용자의 답변을 분석하여 MBTI 성향 점수를 매긴다.\n"
        "규칙:\n"
        "- 질문과 답변의 맥락을 고려하여 가장 관련 있는 MBTI 차원 1개를 선택한다.\n"
        "- 차원: EI(외향/내향), SN(감각/직관), TF(사고/감정), JP(판단/인식)\n"
        "- 해당 차원의 양쪽에 각각 0~10점 사이의 점수를 부여한다.\n"
        "- 점수는 답변에서 드러난 성향의 강도를 반영한다.\n"
        "- 출력은 반드시 JSON 하나이며, 아래 스키마를 지킨다.\n"
        '  {"dimension": "EI", "scores": {"E": 7, "I": 2}, "reasoning": "분석 근거"}\n'
        "- reasoning은 한국어로 1-2문장으로 간단히 작성한다.\n"
    )


def _build_analysis_user_prompt(command: AnalyzeAnswerCommand) -> str:
    """답변 분석용 유저 프롬프트"""
    # 히스토리 구성
    history_lines = []
    for msg in command.history:
        role = msg.role.value if isinstance(msg.role, MessageRole) else str(msg.role)
        history_lines.append(f"{role}: {msg.content}")

    history_block = "\n".join(history_lines).strip() or "(이전 대화 없음)"

    return (
        "이전 대화 맥락:\n"
        f"{history_block}\n\n"
        f"현재 질문: {command.question}\n"
        f"사용자 답변: {command.answer}\n\n"
        "위 답변을 분석하여 MBTI 점수 JSON을 출력해라."
    )


@dataclass
class OpenAIQuestionProvider(AIQuestionProviderPort):
    """
    OpenAI 클라이언트는 외부에서 주입(테스트에서 모킹)한다.
    settings.py에서 키/모델을 읽는 함수는 create_client 팩토리에서 처리하도록 분리 가능.
    """
    openai_client: Any
    model: str

    def generate_questions(self, command: GenerateAIQuestionCommand) -> AIQuestionResponse:
        system_prompt = _build_system_prompt()
        user_prompt = _build_user_prompt(command)

        resp = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content  # openai python SDK 1.x 형태 가정
        data = _parse_json_object(content)

        turn = int(data.get("turn", command.turn))
        raw_questions = data.get("questions", [])
        questions: List[AIQuestion] = []
        for q in raw_questions:
            questions.append(
                AIQuestion(
                    text=str(q.get("text", "")).strip(),
                    target_dimensions=list(q.get("target_dimensions", [])),
                )
            )

        # 최소 방어: 질문 비어있으면 실패로 처리
        if not questions or any(not q.text for q in questions):
            raise ValueError("LLM returned invalid questions payload")

        return AIQuestionResponse(turn=turn, questions=questions)

    def analyze_answer(self, command: AnalyzeAnswerCommand) -> AnalyzeAnswerResponse:
        """AI를 사용하여 답변을 분석하고 MBTI 점수를 반환한다."""
        system_prompt = _build_analysis_system_prompt()
        user_prompt = _build_analysis_user_prompt(command)

        resp = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        content = resp.choices[0].message.content
        data = _parse_json_object(content)

        dimension = data.get("dimension", "EI")
        scores = data.get("scores", {})
        reasoning = data.get("reasoning", "")

        # 차원 유효성 검사
        valid_dimensions = {"EI", "SN", "TF", "JP"}
        if dimension not in valid_dimensions:
            dimension = "EI"  # fallback

        # 점수 파싱 및 우세한 쪽 결정
        dimension_sides = {
            "EI": ("E", "I"),
            "SN": ("S", "N"),
            "TF": ("T", "F"),
            "JP": ("J", "P"),
        }
        side_a, side_b = dimension_sides[dimension]

        score_a = int(scores.get(side_a, 0))
        score_b = int(scores.get(side_b, 0))

        if score_a >= score_b:
            winning_side = side_a
            winning_score = score_a
        else:
            winning_side = side_b
            winning_score = score_b

        return AnalyzeAnswerResponse(
            dimension=dimension,
            scores={side_a: score_a, side_b: score_b},
            side=winning_side,
            score=winning_score,
            reasoning=reasoning,
        )


# (선택) settings.py 기반 클라이언트 팩토리: 기존 프로젝트 스타일에 맞게 라우터에서 사용
def create_openai_question_provider_from_settings() -> OpenAIQuestionProvider:
    from config.settings import get_settings
    from openai import OpenAI

    settings = get_settings()  # ✅ 인스턴스 가져오기
    api_key = settings.OPENAI_API_KEY
    model = getattr(settings, "OPENAI_MODEL", None) or "gpt-4o-mini"
    client = OpenAI(api_key=api_key)
    return OpenAIQuestionProvider(openai_client=client, model=model)