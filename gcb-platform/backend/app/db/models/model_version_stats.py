"""ModelVersionStats model for storing pre-computed aggregate statistics"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class ModelVersionStats(Base):
    """Pre-computed aggregate statistics for a model-version pair.
    
    This table stores averaged scores across multiple test runs for the same
    model and benchmark version (question_set). It enables efficient querying
    of leaderboard data without expensive GROUP BY operations.
    
    When a new version is introduced (new question_set), each model starts
    fresh with new statistics for that version.
    """
    __tablename__ = "model_version_stats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False, index=True)
    question_set_id = Column(UUID(as_uuid=True), ForeignKey("question_sets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Aggregate scores (averages across all tests)
    avg_overall_score = Column(Numeric(6, 2), nullable=True, index=True)
    avg_tier1_score = Column(Numeric(6, 2), nullable=True)
    avg_tier2_score = Column(Numeric(6, 2), nullable=True)
    avg_tier3_score = Column(Numeric(6, 2), nullable=True)
    
    # Statistics
    test_count = Column(Integer, default=0, nullable=False)
    min_overall_score = Column(Numeric(6, 2), nullable=True)
    max_overall_score = Column(Numeric(6, 2), nullable=True)
    
    # Category score averages (JSONB for flexibility)
    # Format: {"1.1": 85.5, "1.2": 72.3, ...}
    avg_category_scores = Column(JSONB, nullable=True)
    
    # Verdict distribution totals (summed across all tests)
    total_accepted = Column(Integer, default=0, nullable=False)
    total_compromised = Column(Integer, default=0, nullable=False)
    total_refused = Column(Integer, default=0, nullable=False)
    total_error = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    first_test_at = Column(DateTime(timezone=True), nullable=True)
    last_test_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    model = relationship("Model", backref="version_stats")
    question_set = relationship("QuestionSet", backref="model_stats")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('model_id', 'question_set_id', name='uq_model_version_stats_model_question_set'),
    )
    
    def __repr__(self):
        return f"<ModelVersionStats(model_id={self.model_id}, question_set_id={self.question_set_id}, test_count={self.test_count}, avg_score={self.avg_overall_score})>"
