from datetime import datetime


class ChatMessage:
    """채팅 메시지 도메인 엔티티"""

    def __init__(
        self,
        id: str,
        room_id: str,
        sender_id: str,
        content: str,
        created_at: datetime | None = None,
    ):
        self._validate(id, room_id, sender_id, content)
        self.id = id
        self.room_id = room_id
        self.sender_id = sender_id
        self.content = content
        self.created_at = created_at or datetime.now()

    def _validate(self, id: str, room_id: str, sender_id: str, content: str) -> None:
        """ChatMessage 값의 유효성을 검증한다"""
        if not id:
            raise ValueError("ChatMessage id는 비어있을 수 없습니다")
        if not room_id:
            raise ValueError("ChatMessage room_id는 비어있을 수 없습니다")
        if not sender_id:
            raise ValueError("ChatMessage sender_id는 비어있을 수 없습니다")
        if not content or not content.strip():
            raise ValueError("ChatMessage content는 비어있을 수 없습니다")