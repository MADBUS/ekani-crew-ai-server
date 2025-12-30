from datetime import datetime


class ChatRoom:
    """채팅방 도메인 엔티티"""

    def __init__(
        self,
        id: str,
        user1_id: str,
        user2_id: str,
        created_at: datetime | None = None,
        user1_last_read_at: datetime | None = None,
        user2_last_read_at: datetime | None = None,
    ):
        self._validate(id, user1_id, user2_id)
        self.id = id
        self.user1_id = user1_id
        self.user2_id = user2_id
        self.created_at = created_at or datetime.now()
        self.user1_last_read_at = user1_last_read_at
        self.user2_last_read_at = user2_last_read_at

    def _validate(self, id: str, user1_id: str, user2_id: str) -> None:
        """ChatRoom 값의 유효성을 검증한다"""
        if not id:
            raise ValueError("ChatRoom id는 비어있을 수 없습니다")
        if not user1_id:
            raise ValueError("ChatRoom user1_id는 비어있을 수 없습니다")
        if not user2_id:
            raise ValueError("ChatRoom user2_id는 비어있을 수 없습니다")

    def mark_read_by_user(self, user_id: str, read_at: datetime | None = None) -> None:
        """특정 사용자가 채팅방을 읽음 처리한다"""
        if user_id == self.user1_id:
            self.user1_last_read_at = read_at or datetime.now()
        elif user_id == self.user2_id:
            self.user2_last_read_at = read_at or datetime.now()
        else:
            raise ValueError(f"User {user_id} is not a participant of this chat room")

    def get_last_read_at(self, user_id: str) -> datetime | None:
        """특정 사용자의 마지막 읽은 시간을 반환한다"""
        if user_id == self.user1_id:
            return self.user1_last_read_at
        elif user_id == self.user2_id:
            return self.user2_last_read_at
        else:
            raise ValueError(f"User {user_id} is not a participant of this chat room")