import uuid
from typing import List

from app.mbti_test.application.port.input.answer_question_use_case import (
    AnswerQuestionCommand,
    AnswerQuestionResponse,
    AnswerQuestionUseCase,
)
from app.mbti_test.application.port.output.mbti_test_session_repository import MBTITestSessionRepositoryPort
from app.mbti_test.application.port.ai_question_provider_port import AIQuestionProviderPort
from app.mbti_test.domain.analyzer import (
    run_analysis,
    calculate_partial_mbti,
    analyze_single_answer,
    get_dimension_for_question,
)
from app.mbti_test.infrastructure.service.human_question_provider import HumanQuestionProvider
from app.mbti_test.domain.mbti_message import MBTIMessage, MessageRole, MessageSource
from app.mbti_test.domain.mbti_test_session import TestStatus, Turn
from app.mbti_test.domain.models import (
    GenerateAIQuestionCommand,
    AnalyzeAnswerCommand,
    ChatMessage,
    MessageRole as ModelMessageRole,
)


HUMAN_QUESTION_COUNT = 12
TOTAL_QUESTION_COUNT = 24


class AnswerQuestionService(AnswerQuestionUseCase):
    def __init__(
        self,
        session_repository: MBTITestSessionRepositoryPort,
        human_question_provider: HumanQuestionProvider,
        ai_question_provider: AIQuestionProviderPort,
    ):
        self._session_repository = session_repository
        self._human_question_provider = human_question_provider
        self._ai_question_provider = ai_question_provider

    def execute(self, command: AnswerQuestionCommand) -> AnswerQuestionResponse:
        # 1. Find session
        session = self._session_repository.find_by_id(uuid.UUID(command.session_id))
        if not session:
            raise ValueError(f"Session not found: {command.session_id}")

        # 2. 인사 응답 처리 (greeting 후 첫 답변)
        if not session.greeting_completed:
            # 인사에 대한 응답은 저장 안 함 (무시)
            session.greeting_completed = True

            # 첫 번째 질문 반환 (index 0)
            first_question = self._human_question_provider.get_question_from_list(
                0, session.selected_human_questions
            )

            # pending_question에 저장 (다음 답변 시 Turn으로 저장됨)
            if first_question:
                session.pending_question = first_question.content

            self._session_repository.save(session)

            return AnswerQuestionResponse(
                question_number=1,  # 1번 질문
                total_questions=TOTAL_QUESTION_COUNT,
                next_question=first_question,
                is_completed=False,
            )

        # 3. 정상 답변 처리 - Turn 생성 및 저장
        current_index = session.current_question_index

        # 답변 분석: Human(0-11) vs AI(12-23)
        if current_index < HUMAN_QUESTION_COUNT:
            # Human phase: 키워드 기반 분석
            dimension = get_dimension_for_question(current_index)
            analysis = analyze_single_answer(command.answer, dimension)
            scores = analysis["scores"]
            side = analysis["side"]
            score = analysis["score"]
        else:
            # AI phase: AI 기반 분석 (맥락 포함)
            history = self._build_chat_history(session)
            analyze_command = AnalyzeAnswerCommand(
                question=session.pending_question or "",
                answer=command.answer,
                history=history,
            )
            ai_analysis = self._ai_question_provider.analyze_answer(analyze_command)
            dimension = ai_analysis.dimension
            scores = ai_analysis.scores
            side = ai_analysis.side
            score = ai_analysis.score

        # Turn 생성
        turn = Turn(
            turn_number=current_index + 1,  # 1-based
            question=session.pending_question or "",
            answer=command.answer,
            dimension=dimension,
            scores=scores,
            side=side,
            score=score,
        )
        session.turns.append(turn)
        session.current_question_index += 1

        current_index = session.current_question_index
        analysis_result = None
        partial_analysis_result = None

        # 4. 사람 질문(12개) 완료 시 분석 실행
        if current_index == HUMAN_QUESTION_COUNT:
            answers = [t.answer for t in session.turns]
            mbti, scores, confidence = run_analysis(answers)

            analysis_result = {
                "mbti": mbti,
                "scores": scores,
                "confidence": confidence,
            }
            session.human_test_result = analysis_result

        # 5. 매 질문마다 부분 MBTI 분석
        if current_index <= HUMAN_QUESTION_COUNT:
            current_answers = [t.answer for t in session.turns]
            partial_analysis_result = calculate_partial_mbti(current_answers)
            print(f"Partial MBTI Analysis for question {current_index}: {partial_analysis_result}")

        # 6. 전체 완료 체크
        if current_index >= TOTAL_QUESTION_COUNT:
            session.status = TestStatus.COMPLETED
            session.pending_question = None
            self._session_repository.save(session)
            return AnswerQuestionResponse(
                question_number=current_index,
                total_questions=TOTAL_QUESTION_COUNT,
                next_question=None,
                is_completed=True,
                analysis_result=analysis_result,
                partial_analysis_result=partial_analysis_result,
            )

        # 7. 다음 질문 가져오기
        if current_index < HUMAN_QUESTION_COUNT:
            # Human phase (questions 0-11) - 세션에 저장된 랜덤 선택 질문 사용
            next_question = self._human_question_provider.get_question_from_list(
                current_index, session.selected_human_questions
            )
        else:
            # AI phase (questions 12-23)
            history = self._build_chat_history(session)
            ai_turn = current_index - HUMAN_QUESTION_COUNT + 1  # 1-12 for AI

            ai_command = GenerateAIQuestionCommand(
                session_id=command.session_id,
                turn=ai_turn,
                history=history,
                question_mode="normal",
            )

            ai_response = self._ai_question_provider.generate_questions(ai_command)

            if ai_response.questions:
                next_question = MBTIMessage(
                    role=MessageRole.ASSISTANT,
                    content=ai_response.questions[0].text,
                    source=MessageSource.AI,
                )
            else:
                # Fallback if AI fails
                next_question = MBTIMessage(
                    role=MessageRole.ASSISTANT,
                    content="다음 질문입니다: 당신의 성격을 한 단어로 표현한다면?",
                    source=MessageSource.AI,
                )

        # 8. pending_question에 저장 (다음 답변 시 Turn으로 저장됨)
        if next_question:
            session.pending_question = next_question.content

        self._session_repository.save(session)

        return AnswerQuestionResponse(
            question_number=current_index + 1,  # 1-based for display
            total_questions=TOTAL_QUESTION_COUNT,
            next_question=next_question,
            is_completed=False,
            analysis_result=analysis_result,
            partial_analysis_result=partial_analysis_result,
        )

    def _build_chat_history(self, session) -> List[ChatMessage]:
        """Build chat history from session for AI context"""
        history = []

        # Build from turns
        for turn in session.turns:
            history.append(ChatMessage(
                role=ModelMessageRole.ASSISTANT,
                content=turn.question,
            ))
            history.append(ChatMessage(
                role=ModelMessageRole.USER,
                content=turn.answer,
            ))

        return history