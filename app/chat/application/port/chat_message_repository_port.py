from abc import ABC, abstractmethod

from app.chat.domain.chat_message import ChatMessage


class ChatMessageRepositoryPort(ABC):
    """채팅 메시지 저장소 포트 인터페이스"""

    @abstractmethod
    def save(self, message: ChatMessage) -> None:
        """메시지를 저장한다"""
        pass

    @abstractmethod
    def find_by_id(self, message_id: str) -> ChatMessage | None:
        """id로 메시지를 조회한다"""
        pass

    @abstractmethod
    def find_by_room_id(self, room_id: str) -> list[ChatMessage]:
        """room_id로 해당 채팅방의 메시지 목록을 시간순으로 조회한다"""
        pass