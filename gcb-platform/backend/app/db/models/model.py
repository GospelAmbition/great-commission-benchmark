"""Model (LLM) model"""
from sqlalchemy import Column, String, Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base import Base


class Model(Base):
    """Model (LLM) model"""
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(String(255), unique=True, nullable=False, index=True)  # OpenRouter model ID
    name = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    estimated_cost_per_test = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
