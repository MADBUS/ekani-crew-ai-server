from datetime import datetime

from app.chat.application.port.chat_room_repository_port import ChatRoomRepositoryPort
from app.chat.domain.chat_room import ChatRoom


class CreateChatRoomUseCase:
    """채팅방 생성 유스케이스"""

    def __init__(self, repository: ChatRoomRepositoryPort):
        self._repository = repository

    def execute(
        self,
        room_id: str,
        user1_id: str,
        user2_id: str,
        timestamp: datetime
    ) -> str:
        """match 도메인에서 전달한 데이터로 채팅방을 생성하고 room_id를 반환한다"""
        # 두 사용자 간에 이미 채팅방이 있는지 확인 (중복 생성 방지)
        existing_room_by_users = self._repository.find_by_users(user1_id, user2_id)
        if existing_room_by_users is not None:
            # 이미 존재하는 채팅방이 있으면 기존 room_id 반환
            return existing_room_by_users.id

        # room_id로 이미 존재하는 채팅방인지 확인
        existing_room_by_id = self._repository.find_by_id(room_id)
        if existing_room_by_id is not None:
            raise ValueError("이미 존재하는 채팅방입니다")

        # 새로운 채팅방 생성
        room = ChatRoom(
            id=room_id,
            user1_id=user1_id,
            user2_id=user2_id,
            created_at=timestamp
        )

        # 저장
        self._repository.save(room)

        return room_id