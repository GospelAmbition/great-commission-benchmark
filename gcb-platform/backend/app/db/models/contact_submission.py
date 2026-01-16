"""ContactSubmission model"""
from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class ContactStatus(str, enum.Enum):
    """Contact submission status types"""
    NEW = "new"
    READ = "read"
    RESPONDED = "responded"


class ContactSubject(str, enum.Enum):
    """Contact form subject categories"""
    GENERAL = "general"
    TECHNICAL = "technical"
    PARTNERSHIP = "partnership"
    MEDIA = "media"
    FEEDBACK = "feedback"
    OTHER = "other"


class ContactSubmission(Base):
    """ContactSubmission model for storing contact form submissions"""
    __tablename__ = "contact_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    subject = Column(SQLEnum(ContactSubject), nullable=False, default=ContactSubject.GENERAL)
    message = Column(Text, nullable=False)
    status = Column(SQLEnum(ContactStatus), default=ContactStatus.NEW, nullable=False)
    admin_notes = Column(Text, nullable=True)  # Notes from admin handling the submission
    responded_at = Column(DateTime(timezone=True), nullable=True)
    responded_by = Column(UUID(as_uuid=True), nullable=True)  # Admin who responded
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
