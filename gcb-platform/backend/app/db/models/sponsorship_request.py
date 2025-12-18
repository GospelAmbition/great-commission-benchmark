"""SponsorshipRequest model"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class SponsorshipRequest(Base):
    """SponsorshipRequest model"""
    __tablename__ = "sponsorship_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)
    justification = Column(Text, nullable=False)
    context = Column(Text)
    status = Column(String(50), default="pending")  # 'pending', 'approved', 'funded', 'completed', 'rejected'
    funded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    funded_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], backref="sponsorship_requests")
    model = relationship("Model", backref="sponsorship_requests")
    funder = relationship("User", foreign_keys=[funded_by])
