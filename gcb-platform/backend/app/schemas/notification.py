"""Notification settings API schemas"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from app.db.models.notification_setting import NotificationType


class NotificationSettingItem(BaseModel):
    """Single notification setting item"""
    id: UUID
    notification_type: str
    recipient_email: Optional[str]
    is_enabled: bool
    description: Optional[str]
    updated_at: datetime
    updated_by_id: Optional[UUID]
    updated_by_name: Optional[str]


class NotificationSettingsListResponse(BaseModel):
    """List of all notification settings"""
    settings: list[NotificationSettingItem]


class NotificationSettingUpdateRequest(BaseModel):
    """Request to update a notification setting"""
    recipient_email: Optional[EmailStr] = None
    is_enabled: Optional[bool] = None


class NotificationSettingUpdateResponse(BaseModel):
    """Response after updating a notification setting"""
    id: UUID
    notification_type: str
    recipient_email: Optional[str]
    is_enabled: bool
    message: str
