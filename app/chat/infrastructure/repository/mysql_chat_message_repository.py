from sqlalchemy.orm import Session

from app.chat.application.port.chat_message_repository_port import ChatMessageRepositoryPort
from app.chat.domain.chat_message import ChatMessage
from app.chat.infrastructure.model.chat_message_model import ChatMessageModel


class MySQLChatMessageRepository(ChatMessageRepositoryPort):
    """MySQL 기반 채팅 메시지 저장소"""

    def __init__(self, db_session: Session):
        self._db = db_session

    def save(self, message: ChatMessage) -> None:
        """메시지를 저장한다"""
        message_model = ChatMessageModel(
            id=message.id,
            room_id=message.room_id,
            sender_id=message.sender_id,
            content=message.content,
            created_at=message.created_at,
        )
        self._db.add(message_model)
        self._db.commit()

    def find_by_id(self, message_id: str) -> ChatMessage | None:
        """id로 메시지를 조회한다"""
        message_model = self._db.query(ChatMessageModel).filter(
            ChatMessageModel.id == message_id
        ).first()

        if message_model is None:
            return None

        return ChatMessage(
            id=message_model.id,
            room_id=message_model.room_id,
            sender_id=message_model.sender_id,
            content=message_model.content,
            created_at=message_model.created_at,
        )

    def find_by_room_id(self, room_id: str) -> list[ChatMessage]:
        """room_id로 해당 채팅방의 메시지 목록을 시간순으로 조회한다"""
        message_models = self._db.query(ChatMessageModel).filter(
            ChatMessageModel.room_id == room_id
        ).order_by(ChatMessageModel.created_at).all()

        return [
            ChatMessage(
                id=model.id,
                room_id=model.room_id,
                sender_id=model.sender_id,
                content=model.content,
                created_at=model.created_at,
            )
            for model in message_models
        ]