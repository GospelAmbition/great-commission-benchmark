"""Newsletter campaign send audit model."""
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class NewsletterCampaignSend(Base):
    """Stores newsletter send attempts for duplicate-send protection and audits."""

    __tablename__ = "newsletter_campaign_sends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    audience = Column(String(20), nullable=False, index=True)  # test | production
    campaign_type = Column(String(20), nullable=False, default="newsletter", index=True)  # newsletter | highlight
    campaign_id = Column(String(255), nullable=True)
    recipient_count = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="sent", index=True)
    provider = Column(String(50), nullable=False, default="mailerlite")
    sent_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    post = relationship("BlogPost", backref="newsletter_campaign_sends")
    sent_by_user = relationship("User", backref="newsletter_campaign_sends")
