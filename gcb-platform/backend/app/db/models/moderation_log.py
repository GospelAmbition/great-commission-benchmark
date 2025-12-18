"""ModerationLog model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class ModerationLog(Base):
    """ModerationLog model"""
    __tablename__ = "moderation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_run_id = Column(UUID(as_uuid=True), ForeignKey("test_runs.id"), nullable=False, index=True)
    moderator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)  # 'verified', 'concerns', 'escalated'
    sample_size = Column(Integer)
    agreements = Column(Integer)
    disagreements = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_run = relationship("TestRun", backref="moderation_logs")
    moderator = relationship("User", backref="moderation_logs")
