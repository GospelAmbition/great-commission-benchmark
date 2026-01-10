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
    role = Column(String(50), default="user")  # 'user', 'moderator', 'benchmark_developer', 'admin'
    # Permission flags (replaces hierarchical role system)
    can_view_benchmark = Column(Boolean, default=False, nullable=False)  # Read-only benchmark dashboard access
    can_edit_benchmark = Column(Boolean, default=False, nullable=False)  # Edit benchmark questions/versions
    can_moderate = Column(Boolean, default=False, nullable=False)  # Access moderation dashboard
    can_manage_blog = Column(Boolean, default=False, nullable=False)  # Access blog management dashboard
    can_admin = Column(Boolean, default=False, nullable=False)  # Administrator (cascades to all permissions)
    credentials = Column(Text)  # For moderators: background, expertise
    tester_agreement_accepted = Column(Boolean, default=False, nullable=False)
    tester_agreement_accepted_at = Column(DateTime(timezone=True), nullable=True)
    fee_waived = Column(Boolean, default=False, nullable=False)  # CLI submission fee waiver
    fee_waived_at = Column(DateTime(timezone=True), nullable=True)
    fee_waived_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    fee_waived_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
