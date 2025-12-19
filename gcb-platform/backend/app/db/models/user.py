"""User model"""
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth0_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255))
    role = Column(String(50), default="user")  # 'user', 'moderator', 'admin'
    credentials = Column(Text)  # For moderators: background, expertise
    tester_agreement_accepted = Column(Boolean, default=False, nullable=False)
    tester_agreement_accepted_at = Column(DateTime(timezone=True), nullable=True)
    fee_waived = Column(Boolean, default=False, nullable=False)  # CLI submission fee waiver
    fee_waived_at = Column(DateTime(timezone=True), nullable=True)
    fee_waived_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    fee_waived_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
