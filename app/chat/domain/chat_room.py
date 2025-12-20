from datetime import datetime


class ChatRoom:
    """채팅방 도메인 엔티티"""

    def __init__(
        self,
        id: str,
        user1_id: str,
        user2_id: str,
        created_at: datetime | None = None,
    ):
        self._validate(id, user1_id, user2_id)
        self.id = id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.created_at = created_at or datetime.now()

    def _validate(self, id: str, user1_id: str, user2_id: str) -> None:
        """ChatRoom 값의 유효성을 검증한다"""
        if not id:
            raise ValueError("ChatRoom id는 비어있을 수 없습니다")
        if not user1_id:
            raise ValueError("ChatRoom user1_id는 비어있을 수 없습니다")
        if not user2_id:
            raise ValueError("ChatRoom user2_id는 비어있을 수 없습니다")