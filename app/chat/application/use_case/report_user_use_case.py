import uuid
from datetime import datetime

from app.chat.application.port.report_repository_port import ReportRepositoryPort
from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.domain.report import Report, ReportReason


class ReportUserUseCase:
    """사용자 신고 유스케이스"""

    def __init__(
        self,
        report_repository: ReportRepositoryPort,
        chat_room_repository: ChatRoomRepositoryPort,
        chat_message_repository: ChatMessageRepositoryPort
    ):
        self._report_repository = report_repository
        self._chat_room_repository = chat_room_repository
        self._chat_message_repository = chat_message_repository

    def execute(
        self,
        reporter_id: str,
        message_id: str,
        reasons: list[ReportReason]
    ) -> str:
        """메시지를 신고하고 report_id를 반환한다"""
        # 1. 메시지 조회
        message = self._chat_message_repository.find_by_id(message_id)
        if message is None:
            raise ValueError("메시지를 찾을 수 없습니다")

        # 2. 채팅방 조회
        room = self._chat_room_repository.find_by_id(message.room_id)
        if room is None:
            raise ValueError("채팅방을 찾을 수 없습니다")

        # 3. 신고자가 채팅방 참여자인지 확인
        if reporter_id != room.user1_id and reporter_id != room.user2_id:
            raise ValueError("채팅방 참여자만 신고할 수 있습니다")

        # 4. 피신고자 확인 (메시지 발신자)
        reported_user_id = message.sender_id

        # 5. 자기 메시지 신고 방지 (도메인에서도 검증하지만 명확성을 위해 여기서도 체크)
        if reporter_id == reported_user_id:
            raise ValueError("자기 자신을 신고할 수 없습니다")

        # 6. 중복 신고 체크
        existing_report = self._report_repository.find_by_message_and_reporter(message_id, reporter_id)
        if existing_report is not None:
            raise ValueError("이미 신고한 메시지입니다")

        # 7. 신고 생성
        report = Report(
            id=str(uuid.uuid4()),
            reporter_id=reporter_id,
            reported_user_id=reported_user_id,
            room_id=room.id,
            message_id=message_id,
            reasons=reasons,
            created_at=datetime.now()
        )

        # 8. 저장
        self._report_repository.save(report)

        return report.id
