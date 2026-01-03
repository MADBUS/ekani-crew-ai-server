from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort


class LeaveChatRoomUseCase:
    """채팅방 나가기 유스케이스"""

    def __init__(self, repository: ChatRoomRepositoryPort):
        self._repository = repository

    def execute(self, room_id: str, user_id: str) -> None:
        """사용자가 채팅방을 나간다"""
        # 채팅방 조회
        room = self._repository.find_by_id(room_id)
        if room is None:
            raise ValueError("채팅방을 찾을 수 없습니다")

        # 채팅방 나가기
        room.leave_room(user_id)

        # 저장
        self._repository.save(room)
