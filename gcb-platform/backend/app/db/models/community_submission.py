"""CommunitySubmission model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class CommunitySubmission(Base):
    """CommunitySubmission model"""
    __tablename__ = "community_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    model_name = Column(String(255), nullable=False)
    model_url = Column(String(500))
    organization = Column(String(255))
    cli_version = Column(String(50), nullable=False)
    question_set_version = Column(String(10), nullable=False)
    results_package = Column(JSONB, nullable=False)
    overall_score = Column(Integer)
    tier1_score = Column(Integer)
    tier2_score = Column(Integer)
    tier3_score = Column(Integer)
    status = Column(String(50), default="pending", index=True)  # 'pending', 'reviewing', 'approved', 'rejected'
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewer_notes = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))

    user = relationship("User", foreign_keys=[user_id], backref="community_submissions")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
