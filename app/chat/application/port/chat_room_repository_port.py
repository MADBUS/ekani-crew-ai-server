from abc import ABC, abstractmethod

from app.chat.domain.chat_room import ChatRoom


class ChatRoomRepositoryPort(ABC):
    """채팅방 저장소 포트 인터페이스"""

    @abstractmethod
    def save(self, room: ChatRoom) -> None:
        """채팅방을 저장한다"""
        pass

    @abstractmethod
    def find_by_id(self, room_id: str) -> ChatRoom | None:
        """id로 채팅방을 조회한다"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[ChatRoom]:
        """user_id로 해당 사용자가 참여한 채팅방 목록을 조회한다"""
        pass

    @abstractmethod
    def find_by_users(self, user1_id: str, user2_id: str) -> ChatRoom | None:
        """두 사용자 간의 채팅방을 조회한다 (순서 무관)"""
        pass