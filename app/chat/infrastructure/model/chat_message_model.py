from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class ChatMessageModel(Base):
    """채팅 메시지 ORM 모델"""

    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)
    room_id = Column(String(36), ForeignKey("chat_rooms.id"), nullable=False, index=True)
    sender_id = Column(String(255), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, index=True)

    # Relationships
    room = relationship("ChatRoomModel", back_populates="messages")
    sender = relationship("UserModel", foreign_keys=[sender_id])