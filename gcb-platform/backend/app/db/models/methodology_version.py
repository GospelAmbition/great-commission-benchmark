"""MethodologyVersion model"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class MethodologyVersion(Base):
    """MethodologyVersion model
    
    Note: judge_prompt is deprecated and no longer used. Judge prompts are now
    served from code via app/services/judge.py (single source of truth).
    The column is kept nullable for backward compatibility with existing records.
    """
    __tablename__ = "methodology_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_set_id = Column(UUID(as_uuid=True), ForeignKey("question_sets.id", ondelete="CASCADE"), nullable=False)
    judge_prompt = Column(Text, nullable=True)  # Deprecated: prompts now served from code
    scoring_config = Column(JSONB, nullable=False)
    active_from = Column(DateTime(timezone=True), nullable=False)
    active_until = Column(DateTime(timezone=True))
    changelog = Column(Text)

    question_set = relationship("QuestionSet", backref="methodology_versions")
