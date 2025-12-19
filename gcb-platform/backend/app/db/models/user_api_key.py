"""User API Key model for CLI runner authentication"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class UserAPIKey(Base):
    """API Key model for authenticating CLI runner requests"""
    __tablename__ = "user_api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)  # User-friendly label (e.g., "My Laptop", "CI Server")
    key_prefix = Column(String(8), nullable=False)  # First 8 chars for identification (gcb_xxxx)
    key_hash = Column(String(255), nullable=False)  # SHA-256 hash of the full key
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration

    # Relationship
    user = relationship("User", backref="api_keys")
