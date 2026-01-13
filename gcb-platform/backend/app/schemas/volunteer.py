"""Volunteer API schemas"""
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from app.db.models.volunteer_application import VolunteerRole


class VolunteerApplicationRequest(BaseModel):
    """Volunteer application request"""
    email: EmailStr
    name: str
    role: VolunteerRole
    background: Optional[str] = None
    motivation: Optional[str] = None


class VolunteerApplicationResponse(BaseModel):
    """Volunteer application response"""
    success: bool
    message: str
    application_id: Optional[UUID] = None


class VolunteerApplicationListItem(BaseModel):
    """Volunteer application list item"""
    id: UUID
    user_id: Optional[UUID]
    email: str
    name: str
    role: str
    background: Optional[str]
    motivation: Optional[str]
    status: str
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class VolunteerApplicationListResponse(BaseModel):
    """Volunteer application list response"""
    applications: list[VolunteerApplicationListItem]
    total: int
