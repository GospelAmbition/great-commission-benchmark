"""SponsorshipRequest model"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class SponsorshipRequest(Base):
    """SponsorshipRequest model for model test sponsorships and requests"""
    __tablename__ = "sponsorship_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Model identification - either use model_id (DB reference) or openrouter_model_id/custom_model_name
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=True)  # Optional DB model reference
    openrouter_model_id = Column(String(255), nullable=True)  # e.g., "anthropic/claude-3.5-sonnet"
    custom_model_name = Column(String(255), nullable=True)  # For unlisted model requests
    
    # Request type and content
    request_type = Column(String(50), default="sponsorship")  # "sponsorship" ($20) or "request" (free)
    message = Column(Text, nullable=True)  # User's message/justification
    justification = Column(Text, nullable=True)  # Legacy field, kept for backward compatibility
    context = Column(Text)
    
    # Status tracking
    status = Column(String(50), default="pending")  # 'pending_payment', 'pending', 'approved', 'rejected', 'completed'
    
    # Payment tracking (for sponsorships)
    payment_id = Column(String(255), nullable=True)  # Stripe PaymentIntent ID
    payment_status = Column(String(50), nullable=True)  # 'pending', 'succeeded', 'failed'
    
    # Moderation
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Legacy funding fields
    funded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    funded_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="sponsorship_requests")
    model = relationship("Model", backref="sponsorship_requests")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    funder = relationship("User", foreign_keys=[funded_by])
