"""NewsletterSubscriber model"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class NewsletterSubscriber(Base):
    """NewsletterSubscriber model"""
    __tablename__ = "newsletter_subscribers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    source = Column(String(120), nullable=False, default="website", server_default="website")
    consent_note = Column(String(1000), nullable=True)
    imported_at = Column(DateTime(timezone=True), nullable=True)
    import_batch_id = Column(UUID(as_uuid=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    mailerlite_subscriber_id = Column(String(255), nullable=True)
    sync_status = Column(String(20), nullable=False, default="pending", server_default="pending", index=True)
    sync_revision = Column(Integer, nullable=False, default=1, server_default="1")
    sync_attempts = Column(Integer, nullable=False, default=0, server_default="0")
    sync_error = Column(String(255), nullable=True)
    sync_next_attempt_at = Column(DateTime(timezone=True), nullable=True)
    sync_lease_id = Column(UUID(as_uuid=True), nullable=True)
    sync_lease_until = Column(DateTime(timezone=True), nullable=True)
    mailerlite_synced_at = Column(DateTime(timezone=True), nullable=True)
    mailerlite_status = Column(String(30), nullable=True)
    mailerlite_group_id = Column(String(255), nullable=True)
    mailerlite_event_at = Column(DateTime(timezone=True), nullable=True)
    resubscribe_nonce = Column(UUID(as_uuid=True), nullable=True)
    resubscribe_requested_at = Column(DateTime(timezone=True), nullable=True)
    resubscribe_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    resubscribe_pending = Column(Boolean, nullable=False, default=False, server_default="false")
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    unsubscribed_at = Column(DateTime(timezone=True))

    __table_args__ = (Index("uq_newsletter_subscribers_canonical_email", func.lower(func.trim(email)), unique=True),)
