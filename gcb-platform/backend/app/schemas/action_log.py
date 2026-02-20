"""Action log API schemas"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ActionLogActor(BaseModel):
    """Actor (user) who performed the action"""

    id: UUID
    name: Optional[str]
    email: str


class ActionLogListItem(BaseModel):
    """Action log entry for admin list"""

    id: UUID
    action: str
    actor_type: str
    actor_user: Optional[ActionLogActor]
    actor_api_key_id: Optional[UUID]
    entity_type: Optional[str]
    entity_id: Optional[str]
    metadata: Optional[dict[str, Any]] = None  # From extra_data column, exposed as metadata in API
    created_at: datetime


class ActionLogListResponse(BaseModel):
    """Paginated action log list response"""

    items: list[ActionLogListItem]
    total: int
