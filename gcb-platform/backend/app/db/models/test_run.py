"""TestRun model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class TestRun(Base):
    """TestRun model"""
    __tablename__ = "test_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False, index=True)
    question_set_id = Column(UUID(as_uuid=True), ForeignKey("question_sets.id"), nullable=False, index=True)
    methodology_version_id = Column(UUID(as_uuid=True), ForeignKey("methodology_versions.id"), nullable=False)
    status = Column(String(50), nullable=False, index=True)  # 'pending', 'running', 'completed', etc.
    retry_count = Column(Integer, default=0)
    last_error = Column(Text)
    checkpoint_question_index = Column(Integer)
    payment_id = Column(String(255))
    payment_status = Column(String(50))
    total_cost = Column(Numeric(10, 2))
    trust_tier = Column(String(50), default="automated")  # 'automated', 'reviewed', 'validated'
    validation_metrics = Column(JSONB)
    admin_assigned_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    admin_notes = Column(Text)
    # Moderator review for automated (bulk) runs: queue vs history
    moderator_reviewed_at = Column(DateTime(timezone=True), nullable=True)
    moderator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    moderator_decision = Column(String(20), nullable=True)  # 'accepted' | 'rejected'
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    user = relationship("User", foreign_keys=[user_id], backref="test_runs")
    moderator = relationship("User", foreign_keys=[moderator_id])
    model = relationship("Model", backref="test_runs")
    question_set = relationship("QuestionSet", backref="test_runs")
    methodology_version = relationship("MethodologyVersion", backref="test_runs")
    admin_assigned = relationship("User", foreign_keys=[admin_assigned_id])
