"""Contact form API schemas"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from app.db.models.contact_submission import ContactSubject, ContactStatus


class ContactSubmitRequest(BaseModel):
    """Contact form submission request"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    subject: ContactSubject = ContactSubject.GENERAL
    message: str = Field(..., min_length=10, max_length=5000)
    recaptcha_token: Optional[str] = None  # reCAPTCHA token for verification


class ContactSubmitResponse(BaseModel):
    """Contact form submission response"""
    success: bool
    message: str
    submission_id: Optional[UUID] = None


class ContactSubmissionListItem(BaseModel):
    """Contact submission list item for admin view"""
    id: UUID
    name: str
    email: str
    subject: str
    message: str
    status: str
    admin_notes: Optional[str]
    responded_at: Optional[datetime]
    responded_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class ContactSubmissionListResponse(BaseModel):
    """Contact submission list response"""
    items: list[ContactSubmissionListItem]
    total: int


class ContactSubmissionDetail(BaseModel):
    """Detailed contact submission view"""
    id: UUID
    name: str
    email: str
    subject: str
    message: str
    status: str
    admin_notes: Optional[str]
    responded_at: Optional[datetime]
    responded_by: Optional[UUID]
    responded_by_name: Optional[str]
    created_at: datetime
    updated_at: datetime


class ContactStatusUpdateRequest(BaseModel):
    """Request to update contact submission status"""
    status: ContactStatus
    admin_notes: Optional[str] = None


class ContactStatusUpdateResponse(BaseModel):
    """Response after updating contact status"""
    id: UUID
    status: str
    message: str
