"""Stripe configuration model for storing encrypted Stripe API credentials"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class StripeConfig(Base):
    """
    Stores Stripe API configuration with encrypted sensitive fields.
    
    Allows admins to update Stripe credentials via the admin panel,
    enabling seamless steward transitions without requiring deployment changes.
    
    Security:
    - secret_key and webhook_secret are encrypted using Fernet (AES-128)
    - Encryption key is derived from NEXTAUTH_SECRET
    - Only one active config should exist at a time
    """
    __tablename__ = "stripe_config"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Encrypted fields (using Fernet encryption)
    secret_key_encrypted = Column(Text, nullable=False)  # sk_test_xxx or sk_live_xxx
    webhook_secret_encrypted = Column(Text, nullable=True)  # whsec_xxx
    
    # Public key (safe to store unencrypted)
    publishable_key = Column(String(255), nullable=False)  # pk_test_xxx or pk_live_xxx
    
    # Configuration metadata
    is_active = Column(Boolean, default=True, nullable=False)
    is_live_mode = Column(Boolean, default=False, nullable=False)  # Determined from key prefix
    
    # Descriptive name for the config (e.g., "Production - Ministry Name")
    name = Column(String(255), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationship to user who last updated
    updated_by = relationship("User", foreign_keys=[updated_by_id])
