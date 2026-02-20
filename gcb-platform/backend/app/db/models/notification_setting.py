"""NotificationSetting model"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class NotificationType(str, enum.Enum):
    """Types of notifications that can be configured"""
    SPONSORSHIP = "sponsorship"  # New sponsorship/model requests
    VOLUNTEER = "volunteer"      # New volunteer applications
    CONTACT = "contact"          # New contact form submissions
    MODERATION = "moderation"    # Community submissions needing moderator review


class NotificationSetting(Base):
    """NotificationSetting model for configuring notification recipients"""
    __tablename__ = "notification_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_type = Column(
        SQLEnum(NotificationType, values_callable=lambda x: [e.value for e in x]),
        unique=True, nullable=False
    )
    recipient_email = Column(String(255), nullable=True)  # Email address to send notifications to
    is_enabled = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)  # Description of what this notification is for
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationship to User who last updated
    updated_by = relationship("User", foreign_keys=[updated_by_id])
