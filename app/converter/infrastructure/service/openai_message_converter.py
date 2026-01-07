"""OpenAI 기반 메시지 변환 어댑터 (Hybrid Version)"""

import json
from openai import OpenAI

from app.converter.application.port.message_converter_port import MessageConverterPort
from app.converter.domain.tone_message import ToneMessage
from app.shared.vo.mbti import MBTI
from config.settings import get_settings


# -----------------------------------------------------------------------------
# MBTI 성향별 페르소나 데이터 (수신자 맞춤 화법 가이드)
# -----------------------------------------------------------------------------
MBTI_PROFILES = {
    # 1. 분석가형 (NT)
    "INTJ": "용의주도한 전략가. 미사여구와 감정 호소를 싫어함. '본론', '논리적 근거', '이득(Benefit)' 위주로 건조하고 명확하게 서술해.",
    "INTP": "논리적인 사색가. 무조건적인 강요 대신 '왜(Why)'인지 인과관계를 설명해. 흥미로운 정보나 새로운 관점을 던지는 게 효과적이야.",
    "ENTJ": "대담한 통솔자. 결론부터(두괄식) 말해. 필요한 리소스와 데드라인을 명확히 제시하고 자신감 있는 어조를 유지해.",
    "ENTP": "뜨거운 논쟁을 즐기는 변론가. 너무 격식 차리지 말고 위트 있게 표현해. 호기심을 자극하거나 살짝 도전적인 뉘앙스도 좋아.",

    # 2. 외교관형 (NF)
    "INFJ": "선의의 옹호자. 예의를 갖추되 가식적이지 않게, 상대방의 가치를 인정해 주는 따뜻한 표현을 써. 직설적 비판보다는 완곡한 표현 사용.",
    "INFP": "열정적인 중재자. 명령조 금지. '혹시 괜찮다면~' 같은 쿠션어를 듬뿍 넣고, 팩트보다는 공감과 지지를 먼저 보내서 마음을 열게 해.",
    "ENFJ": "정의로운 사회운동가. '우리(We)'라는 단어를 자주 사용해. 공동체의 목표나 성장을 강조하고, 칭찬과 감사를 아끼지 마.",
    "ENFP": "재기발랄한 활동가. 딱딱하게 말하면 숨 막혀 함. 느낌표(!), 물결(~), 이모지를 섞어서 생동감 있게 표현해. 긍정적인 리액션 필수.",

    # 3. 관리자형 (SJ)
    "ISTJ": "청렴결백한 논리주의자. 육하원칙(누가, 언제, 어디서, 무엇을, 어떻게)을 정확히 지켜. 감정 빼고 구체적인 데이터와 사실만 전달해.",
    "ISFJ": "용감한 수호자. 조심스럽고 다정하게 말해. 상대방이 부담을 느끼지 않도록 배려하는 문구를 넣고, 구체적인 가이드라인을 주면 좋아해.",
    "ESTJ": "엄격한 관리자. 서론 빼고 본론만 말해. '확인 부탁드립니다', '진행하겠습니다' 처럼 군더더기 없이 깔끔하게 끝맺어.",
    "ESFJ": "사교적인 외교관. 친근하게 안부를 먼저 묻고(스몰토크) 시작해. 딱딱한 업무 얘기만 하기보다 관계를 중요하게 생각한다는 뉘앙스를 풍겨.",

    # 4. 탐험가형 (SP)
    "ISTP": "만능 재주꾼. 최대한 짧고 간결하게(Simple & Short). 구구절절 설명하지 말고 핵심 용건만 툭 던져. 쿨한 말투 유지.",
    "ISFP": "호기심 많은 예술가. 부드럽고 상냥한 말투로 다가가. 재촉하지 말고 여유를 줘. 감성적인 포인트나 취향을 존중해 줘.",
    "ESTP": "모험을 즐기는 사업가. 돌려 말하지 말고 시원시원하게 말해. 당장 할 수 있는 행동이나 즐거움에 초점을 맞춰.",
    "ESFP": "자유로운 영혼의 연예인. 파티 초대장처럼 신나게 말해. '완전 대박' 같은 호응을 해주고, 복잡한 논리보다는 당장의 즐거움을 강조해."
}


class OpenAIMessageConverter(MessageConverterPort):
    """OpenAI API를 사용한 메시지 변환 구현체"""

    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def convert(
        self,
        original_message: str,
        sender_mbti: MBTI,
        receiver_mbti: MBTI,
        tone: str,
    ) -> ToneMessage:
        """메시지를 특정 톤으로 변환

        Args:
            original_message: 원본 메시지
            sender_mbti: 발신자 MBTI
            receiver_mbti: 수신자 MBTI
            tone: 변환할 톤

        Returns:
            ToneMessage: 변환된 메시지
        """
        prompt = self._build_prompt(original_message, sender_mbti, receiver_mbti, tone)

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 MBTI 심리 분석 및 커뮤니케이션 코칭 전문가입니다. 상대방의 성향(MBTI)에 맞춰 가장 효과적이고 기분 좋은 화법으로 메시지를 '번역'합니다.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        result = json.loads(content)

        return ToneMessage(
            tone=tone, content=result["content"], explanation=result["explanation"]
        )

    def _build_prompt(
        self, original_message: str, sender_mbti: MBTI, receiver_mbti: MBTI, tone: str
    ) -> str:
        """프롬프트 생성 (Hybrid Approach)"""

        # 1. 수신자 페르소나 (Target Profile) - 절대적 성향
        receiver_profile = MBTI_PROFILES.get(
            receiver_mbti.value, "일반적인 공감 대화법을 사용하세요."
        )

        # 2. 관계 기반 전략 (Gap Analysis) - 상대적 차이 극복
        strategy = self._get_communication_strategy(receiver_mbti)

        # 3. 톤 가이드라인
        tone_guidelines = self._get_tone_guidelines(tone)

        return f"""
# 역할
너는 **'{sender_mbti.value}'** 성향의 발신자가 쓴 메시지를, **'{receiver_mbti.value}'** 성향의 수신자가 가장 듣기 좋고 이해하기 편한 방식으로 다듬어주는 전문 에디터야.

# 입력 데이터
1. 발신자: {sender_mbti.value}
2. 수신자: {receiver_mbti.value}
3. 원본 메시지: "{original_message}"
4. 변환 톤: {tone}

# 타겟 페르소나 분석 ({receiver_mbti.value})
수신자는 아래와 같은 특징을 가지고 있어. 이 스타일에 맞춰서 글을 써줘.
>>> {receiver_profile}

# 맞춤 변환 전략 (Communication Strategy)
발신자와 수신자의 성향 차이를 고려하여 다음 전략을 반드시 적용해.
{strategy}

# ⚠️ 변환 절대 원칙 (Critical Rules)
1. **Fact 보존**: 날짜, 시간, 장소, 금액, 약속 등 핵심 정보는 절대 삭제하거나 변경하지 마.
2. **의도 유지**: 원본의 목적(요청, 거절, 사과, 정보 공유 등)은 그대로 유지해야 해.
3. **발신자 고려**: 발신자가 {sender_mbti.value}임을 감안하여, 발신자의 본래 의도가 왜곡되지 않도록 주의해.

# 톤 앤 매너 가이드 ({tone})
{tone_guidelines}

# 출력 형식 (JSON)
{{
    "content": "변환된 메시지 내용",
    "explanation": "{receiver_mbti.value}의 특성 중 [구체적인 특징]을 고려하여 [어떻게] 표현했어. (1문장 요약)"
}}
"""

    def _get_communication_strategy(self, receiver: MBTI) -> str:
        """모든 상황에 적용 가능한 범용 전략 생성 (Sender vs Receiver 차이 분석)"""
        strategies = []

        # 1. 정보 전달 방식 (S vs N)
        if receiver.information == 'N':
            strategies.append("👉 **수신자가 N형 (직관)**: 너무 자잘한 사실 나열은 줄이고, **'그래서 이게 무슨 의미인지(Big Picture)'**나 **'앞으로의 방향성'**을 먼저 언급해줘.")
        elif receiver.information == 'S':
            strategies.append("👉 **수신자가 S형 (감각)**: 추상적인 표현이나 비유는 빼고, **'지금 당장 무엇을 해야 하는지'**, **'눈에 보이는 구체적 예시'**로 바꿔서 말해줘.")

        # 2. 의사결정 및 피드백 방식 (T vs F)
        if receiver.decision == 'F':
            strategies.append("👉 **수신자가 F형 (감정)**: 지적이나 해결책부터 던지지 마. **'공감하는 멘트'**나 **'상대방의 노력에 대한 인정'**을 먼저 표현한 뒤 본론을 꺼내.")
        elif receiver.decision == 'T':
            strategies.append("👉 **수신자가 T형 (사고)**: 감정적인 서술은 줄이고, **'원인과 결과(In-Ga)'**, **'핵심 용건'**, **'객관적 근거'** 위주로 드라이하게 정리해.")

        # 3. 생활 양식 및 업무 방식
        if receiver.lifestyle == 'P':
            strategies.append("👉 **수신자가 P형 (인식)**: 분 단위 계획표는 P에게 '읽기 싫은 텍스트'일 뿐이야. **중간 과정(기상, 씻기, 이동 등)은 싹 다 지워버려.**")
            strategies.append("대신 다음 두 가지 중 하나로 변환해:")
            strategies.append("1. **선택권 부여**: 'A, B, C 중에 어디가 젤 땡겨? 하나만 골라 대충 가자.'")
            strategies.append("2. **단순 통보**: '복잡한 건 내가 챙길 테니까, 넌 12시까지 OO으로 몸만 와.'")
        elif receiver.lifestyle == 'J':
            strategies.append("👉 **수신자가 J형 (판단)**: 모호한 표현('글쎄', '대충')을 없애고, **'확실한 결론'**과 **'명확한 계획/단계'**를 보여줘서 불확실성을 제거해.")

        # 4. 동일 성향일 때
        if not strategies:
            strategies.append("👉 **동일 성향 전략**: 발신자의 원래 의도와 뉘앙스가 아주 잘 맞으니, 예의만 갖춰서 다듬어줘.")

        return "\n".join(strategies)

    def _get_tone_guidelines(self, tone: str) -> str:
        """톤별 변환 가이드라인을 반환

        Args:
            tone: 톤 ("공손한", "캐주얼한", "간결한")

        Returns:
            str: 톤별 구체적인 가이드라인
        """
        guidelines = {
            "공손한": """
• 원본 말투 유지! (반말→반말로 공손하게, 존댓말→존댓말로 공손하게)
• 배려있고 부드러운 표현
• 반말 예시: "혹시 이거 어려우면 도와줄까?", "시간 될 때 봐줄 수 있어?"
• 존댓말 예시: "혹시 시간 되실 때 봐주실 수 있을까요?"
            """,
            "캐주얼한": """
• 친구한테 말하듯 편하게
• 원본 말투 유지
• 반말 예시: "야 이거 봐봐", "어 그래 알겠어"
• 존댓말 예시: "아 네 알겠어요~", "그거 한번 봐주세요"
            """,
            "간결한": """
• 핵심만 짧게, 군더더기 제거
• 원본 말투 유지
• 반말 예시: "이거 확인해줘", "알겠어"
• 존댓말 예시: "확인 부탁드려요", "네 알겠습니다"
            """,
        }

        return guidelines.get(
            tone,
            "• 메시지의 의미를 유지하면서 자연스럽게 변환해주세요.",
        )