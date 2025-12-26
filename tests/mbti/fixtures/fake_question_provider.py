from typing import List

from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource


class FakeQuestionProvider:
    """Fake HumanQuestionProvider for testing"""

    def get_greeting(self) -> MBTIMessage:
        return MBTIMessage(
            role=MessageRole.ASSISTANT,
            content=(
                "혹시... 너도 가끔 네 MBTI가 헷갈리지 않아? 🤔\n\n"
                "검사할 때마다 바뀌는 것 같기도 하고 말이야.\n\n"
                "그래서 내가 왔어! 난 **Nunchi(눈치)**야. 👀\n\n"
                "네가 무심코 던진 말속에 숨겨진 0.1%의 성향까지 내가 싹 다 캐치해 줄게.\n\n"
                "얼마나 정확한지 궁금하지? 지금 바로 확인해 봐! 👇"
            ),
            source=MessageSource.HUMAN,
        )

    def select_random_questions(self, questions_per_dimension: int = 3) -> List[str]:
        """Returns fake questions for testing (3 per dimension = 12 total)"""
        return [
            # E/I
            "테스트 E/I 질문 1",
            "테스트 E/I 질문 2",
            "테스트 E/I 질문 3",
            # S/N
            "테스트 S/N 질문 1",
            "테스트 S/N 질문 2",
            "테스트 S/N 질문 3",
            # T/F
            "테스트 T/F 질문 1",
            "테스트 T/F 질문 2",
            "테스트 T/F 질문 3",
            # J/P
            "테스트 J/P 질문 1",
            "테스트 J/P 질문 2",
            "테스트 J/P 질문 3",
        ]

    def get_question_from_list(
        self, question_index: int, selected_questions: List[str]
    ) -> MBTIMessage | None:
        if question_index < 0 or question_index >= len(selected_questions):
            return None

        return MBTIMessage(
            role=MessageRole.ASSISTANT,
            content=selected_questions[question_index],
            source=MessageSource.HUMAN,
        )

    def get_total_questions(self) -> int:
        return 12
