"""Result model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Result(Base):
    """Result model"""
    __tablename__ = "results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_run_id = Column(UUID(as_uuid=True), ForeignKey("test_runs.id"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    response = Column(Text, nullable=False)
    verdict = Column(String(50), nullable=False, index=True)  # 'ACCEPTED', 'COMPROMISED', 'REFUSED', etc.
    reasoning = Column(Text)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_run = relationship("TestRun", backref="results")
    question = relationship("Question", backref="results")
