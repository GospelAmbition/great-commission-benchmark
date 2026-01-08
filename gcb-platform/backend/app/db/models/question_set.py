"""QuestionSet model"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class QuestionSet(Base):
    """QuestionSet model
    
    Status values: 'draft', 'active', 'archived'
    
    is_publicly_visible controls whether archived versions appear in the public API.
    Active versions are always publicly visible regardless of this flag.
    """
    __tablename__ = "question_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semantic_version = Column(String(10), nullable=False)  # '1.0', '1.1', '1.2', '2.0', etc.
    marketing_version = Column(String(20), nullable=False)  # 'Version 1', 'Version 2', etc.
    status = Column(String(20), nullable=False)  # 'draft', 'active', 'archived'
    is_publicly_visible = Column(Boolean, nullable=False, default=False)  # Controls public visibility for archived versions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    locked_at = Column(DateTime(timezone=True))
    archived_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    target_question_count = Column(Integer, nullable=True)  # Optional target for version (e.g., 200 or 300)
