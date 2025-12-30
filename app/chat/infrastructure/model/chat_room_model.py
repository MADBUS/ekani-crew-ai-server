from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config.database import Base


class ChatRoomModel(Base):
    """채팅방 ORM 모델"""

    __tablename__ = "chat_rooms"

    id = Column(String(36), primary_key=True)
    user1_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    user2_id = Column(String(255), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    user1_last_read_at = Column(DateTime, nullable=True)
    user2_last_read_at = Column(DateTime, nullable=True)

    # Relationships
    user1 = relationship("UserModel", foreign_keys=[user1_id])
    user2 = relationship("UserModel", foreign_keys=[user2_id])
    messages = relationship("ChatMessageModel", back_populates="room", cascade="all, delete-orphan")