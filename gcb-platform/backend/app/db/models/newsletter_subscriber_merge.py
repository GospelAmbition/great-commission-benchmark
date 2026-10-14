"""Original records retained when legacy case variants are consolidated."""
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base


class NewsletterSubscriberMerge(Base):
    __tablename__ = "newsletter_subscriber_merges"
    original_id = Column(UUID(as_uuid=True), primary_key=True)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("newsletter_subscribers.id"), nullable=False, index=True)
    original_record = Column(JSONB, nullable=False)
    merged_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
