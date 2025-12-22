"""Sponsorship API schemas"""
from typing import Optional, List, Literal
from pydantic import BaseModel, validator
from datetime import datetime
from uuid import UUID


class CreateSponsorshipRequest(BaseModel):
    """Create sponsorship or model request"""
    request_type: Literal["sponsorship", "request"]
    openrouter_model_id: Optional[str] = None  # Required for sponsorship
    custom_model_name: Optional[str] = None    # Required for request (unlisted model)
    message: Optional[str] = None              # Required for request, optional for sponsorship
    
    @validator('openrouter_model_id', always=True)
    def validate_openrouter_model_id(cls, v, values):
        if values.get('request_type') == 'sponsorship' and not v:
            raise ValueError('openrouter_model_id is required for sponsorship requests')
        return v
    
    @validator('custom_model_name', always=True)
    def validate_custom_model_name(cls, v, values):
        if values.get('request_type') == 'request' and not v:
            raise ValueError('custom_model_name is required for model requests')
        return v
    
    @validator('message', always=True)
    def validate_message(cls, v, values):
        if values.get('request_type') == 'request' and not v:
            raise ValueError('message is required for model requests')
        return v


class CreateSponsorshipResponse(BaseModel):
    """Response after creating a sponsorship"""
    id: UUID
    request_type: str
    model_name: str  # Either openrouter_model_id or custom_model_name
    status: str
    payment_required: bool
    payment_intent_id: Optional[str] = None
    client_secret: Optional[str] = None  # Stripe client secret for payment
    message: str


class SponsorshipItem(BaseModel):
    """Sponsorship list item"""
    id: UUID
    request_type: str
    model_name: str
    status: str
    payment_status: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class SponsorshipListResponse(BaseModel):
    """User's sponsorship list response"""
    items: List[SponsorshipItem]
    total: int


class SponsorshipQueueItem(BaseModel):
    """Sponsorship queue item for moderators"""
    id: UUID
    request_type: str
    model_name: str
    user_name: str
    user_email: str
    message: Optional[str] = None
    status: str
    payment_status: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SponsorshipQueueResponse(BaseModel):
    """Moderator sponsorship queue response"""
    items: List[SponsorshipQueueItem]
    total: int


class SponsorshipDetailResponse(BaseModel):
    """Detailed sponsorship information for moderator review"""
    id: UUID
    request_type: str
    openrouter_model_id: Optional[str] = None
    custom_model_name: Optional[str] = None
    model_name: str
    user_id: UUID
    user_name: str
    user_email: str
    message: Optional[str] = None
    status: str
    payment_id: Optional[str] = None
    payment_status: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class ReviewSponsorshipRequest(BaseModel):
    """Review sponsorship request"""
    action: Literal["approve", "reject"]
    notes: Optional[str] = None


class ReviewSponsorshipResponse(BaseModel):
    """Review sponsorship response"""
    id: UUID
    status: str
    message: str
