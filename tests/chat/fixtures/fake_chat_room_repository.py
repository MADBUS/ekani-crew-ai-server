from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.chat.domain.chat_room import ChatRoom


class FakeChatRoomRepository(ChatRoomRepositoryPort):
    """테스트용 Fake ChatRoom 저장소"""

    def __init__(self):
        self._rooms: dict[str, ChatRoom] = {}

    def save(self, room: ChatRoom) -> None:
        self._rooms[room.id] = room

    def find_by_id(self, room_id: str) -> ChatRoom | None:
        return self._rooms.get(room_id)

    def find_by_user_id(self, user_id: str) -> list[ChatRoom]:
        return [
            room for room in self._rooms.values()
            if room.user1_id == user_id or room.user2_id == user_id
        ]

    def find_by_users(self, user1_id: str, user2_id: str) -> ChatRoom | None:
        """두 사용자 간의 채팅방을 조회한다 (순서 무관)"""
        for room in self._rooms.values():
            if (room.user1_id == user1_id and room.user2_id == user2_id) or \
               (room.user1_id == user2_id and room.user2_id == user1_id):
                return room
        return None