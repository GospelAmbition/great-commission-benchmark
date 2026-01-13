"""VolunteerApplication model"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.db.base import Base


class VolunteerRole(str, enum.Enum):
    """Volunteer role types"""
    MODERATOR = "moderator"
    ADVISOR = "advisor"


class VolunteerApplication(Base):
    """VolunteerApplication model"""
    __tablename__ = "volunteer_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # Nullable for anonymous applications
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(VolunteerRole), nullable=False)
    background = Column(Text, nullable=True)  # Background, expertise, experience
    motivation = Column(Text, nullable=True)  # Why they want to volunteer
    status = Column(String(50), default="pending", nullable=False)  # pending, approved, rejected
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)  # Admin who reviewed
    notes = Column(Text, nullable=True)  # Admin notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
