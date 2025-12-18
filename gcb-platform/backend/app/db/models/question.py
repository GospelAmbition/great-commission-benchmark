"""Question model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Question(Base):
    """Question model"""
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_set_id = Column(UUID(as_uuid=True), ForeignKey("question_sets.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)  # Use case category (3.1-3.7)
    tier = Column(Integer, nullable=False, index=True)  # 1=Task, 2=Doctrinal, 3=Worldview
    subcategory = Column(String(100))
    expected_verdict = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question_set = relationship("QuestionSet", backref="questions")
