from sqlalchemy import Column, String, DateTime, Text
from config.database import Base


class ChatMessageModel(Base):
    """채팅 메시지 ORM 모델"""

    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)
    room_id = Column(String(36), nullable=False, index=True)
    sender_id = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, index=True)