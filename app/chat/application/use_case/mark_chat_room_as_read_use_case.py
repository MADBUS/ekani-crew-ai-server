from datetime import datetime

from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort


class MarkChatRoomAsReadUseCase:
    """채팅방 읽음 처리 유스케이스"""

    def __init__(self, room_repository: ChatRoomRepositoryPort):
        self._room_repository = room_repository

    def execute(self, room_id: str, user_id: str) -> None:
        """
        특정 사용자가 채팅방의 메시지를 읽음 처리한다.

        Args:
            room_id: 채팅방 ID
            user_id: 읽음 처리할 사용자 ID

        Raises:
            ValueError: 채팅방을 찾을 수 없거나 사용자가 참여자가 아닌 경우
        """
        # 채팅방 조회
        room = self._room_repository.find_by_id(room_id)
        if room is None:
            raise ValueError(f"채팅방을 찾을 수 없습니다: {room_id}")

        # 읽음 처리
        room.mark_read_by_user(user_id, datetime.now())

        # 저장
        self._room_repository.save(room)
