"""ActionLog model for audit trail of key system actions"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class ActionLog(Base):
    """Audit log for key administrative and registration actions."""

    __tablename__ = "action_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(80), nullable=False, index=True)
    actor_type = Column(String(20), nullable=False)  # user, api_key, anonymous, system
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    actor_api_key_id = Column(UUID(as_uuid=True), ForeignKey("user_api_keys.id"), nullable=True, index=True)
    entity_type = Column(String(80), nullable=True, index=True)
    entity_id = Column(String(255), nullable=True)
    extra_data = Column(JSONB, nullable=True)  # Action-specific details (avoids SQLAlchemy reserved 'metadata')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    actor_user = relationship("User", backref="action_logs")
    actor_api_key = relationship("UserAPIKey", backref="action_logs")
