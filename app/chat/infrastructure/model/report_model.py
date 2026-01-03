from sqlalchemy import Column, String, DateTime, Text
from config.database import Base


class ReportModel(Base):
    """신고 ORM 모델"""

    __tablename__ = "reports"

    id = Column(String(36), primary_key=True)
    reporter_id = Column(String(255), nullable=False, index=True)
    reported_user_id = Column(String(255), nullable=False, index=True)
    room_id = Column(String(36), nullable=False, index=True)
    message_id = Column(String(36), nullable=False, index=True)
    reasons = Column(Text, nullable=False)  # JSON array로 저장
    created_at = Column(DateTime, nullable=False)
