from sqlalchemy import Column, String, DateTime
from config.database import Base


class ChatRoomModel(Base):
    """채팅방 ORM 모델"""

    __tablename__ = "chat_rooms"

    id = Column(String(36), primary_key=True)
    user1_id = Column(String(255), nullable=False, index=True)
    user2_id = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)