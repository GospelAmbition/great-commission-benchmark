"""Receipt fingerprints for authenticated, repeatable MailerLite webhooks."""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class NewsletterWebhookEvent(Base):
    __tablename__ = "newsletter_webhook_events"

    fingerprint = Column(String(64), primary_key=True)
    event_type = Column(String(80), nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
