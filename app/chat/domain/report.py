from datetime import datetime
from enum import Enum


class ReportReason(str, Enum):
    """신고 사유"""
    ABUSE = "ABUSE"           # 욕설/폭언
    HARASSMENT = "HARASSMENT"  # 성희롱
    SPAM = "SPAM"             # 스팸
    OTHER = "OTHER"           # 기타


class Report:
    """신고 도메인 엔티티"""

    def __init__(
        self,
        id: str,
        reporter_id: str,
        reported_user_id: str,
        room_id: str,
        message_id: str,
        reasons: list[ReportReason],
        created_at: datetime | None = None,
    ):
        self._validate(id, reporter_id, reported_user_id, room_id, message_id, reasons)
        self.id = id
        self.reporter_id = reporter_id
        self.reported_user_id = reported_user_id
        self.room_id = room_id
        self.message_id = message_id
        self.reasons = reasons
        self.created_at = created_at or datetime.now()

    def _validate(
        self,
        id: str,
        reporter_id: str,
        reported_user_id: str,
        room_id: str,
        message_id: str,
        reasons: list[ReportReason]
    ) -> None:
        """Report 값의 유효성을 검증한다"""
        if not id:
            raise ValueError("Report id는 비어있을 수 없습니다")
        if not reporter_id:
            raise ValueError("Reporter id는 비어있을 수 없습니다")
        if not reported_user_id:
            raise ValueError("Reported user id는 비어있을 수 없습니다")
        if not room_id:
            raise ValueError("Room id는 비어있을 수 없습니다")
        if not message_id:
            raise ValueError("Message id는 비어있을 수 없습니다")
        if not reasons or len(reasons) == 0:
            raise ValueError("최소 하나의 신고 사유를 선택해야 합니다")
        if reporter_id == reported_user_id:
            raise ValueError("자기 자신을 신고할 수 없습니다")
