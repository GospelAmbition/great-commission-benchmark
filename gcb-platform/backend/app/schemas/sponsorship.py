"""Sponsorship API schemas"""
from typing import Optional, List, Literal, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, validator
from datetime import datetime
from uuid import UUID

from app.schemas.common import GCBBaseModel


class CostBreakdown(BaseModel):
    """Cost breakdown for sponsorship pricing"""
    input_tokens: int
    estimated_output_tokens: int
    input_cost: float  # In USD
    output_cost: float  # In USD
    base_fee: float  # In USD
    total: float  # In USD
    prompt_cost_per_token: float
    completion_cost_per_token: float
    question_count: int
    version: str


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


class CreateSponsorshipResponse(GCBBaseModel):
    """Response after creating a sponsorship"""
    id: UUID
    request_type: str
    model_name: str  # Either openrouter_model_id or custom_model_name
    status: str
    payment_required: bool
    payment_intent_id: Optional[str] = None
    client_secret: Optional[str] = None  # Stripe client secret for payment
    message: str
    cost_breakdown: Optional[CostBreakdown] = None  # Cost breakdown for sponsorships


class SponsorshipItem(GCBBaseModel):
    """Sponsorship list item"""
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    
    id: UUID
    request_type: str
    model_name: str
    status: str
    payment_status: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class SponsorshipListResponse(BaseModel):
    """User's sponsorship list response"""
    items: List[SponsorshipItem]
    total: int


class SponsorshipQueueItem(GCBBaseModel):
    """Sponsorship queue item for moderators"""
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    
    id: UUID
    request_type: str
    model_name: str
    user_name: str
    user_email: str
    message: Optional[str] = None
    status: str
    payment_status: Optional[str] = None
    created_at: datetime
    assigned_moderator_id: Optional[UUID] = None
    assigned_moderator_name: Optional[str] = None
    assigned_at: Optional[datetime] = None


class SponsorshipQueueResponse(BaseModel):
    """Moderator sponsorship queue response"""
    items: List[SponsorshipQueueItem]
    total: int


class SponsorshipDetailResponse(GCBBaseModel):
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
    assigned_moderator_id: Optional[UUID] = None
    assigned_moderator_name: Optional[str] = None
    assigned_at: Optional[datetime] = None


class ReviewSponsorshipRequest(BaseModel):
    """Review sponsorship request"""
    action: Literal["approve", "reject"]
    notes: Optional[str] = None


class ReviewSponsorshipResponse(BaseModel):
    """Review sponsorship response"""
    id: UUID
    status: str
    message: str


class AssignModeratorRequest(BaseModel):
    """Request to assign a moderator to a sponsorship"""
    moderator_id: UUID


class AssignModeratorResponse(BaseModel):
    """Response after assigning moderator"""
    id: UUID
    assigned_moderator_id: UUID
    assigned_moderator_name: str
    assigned_at: datetime
    message: str


class AdminSponsorshipItem(GCBBaseModel):
    """Sponsorship item for admin view"""
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    
    id: UUID
    request_type: str
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
    assigned_moderator_id: Optional[UUID] = None
    assigned_moderator_name: Optional[str] = None
    assigned_at: Optional[datetime] = None


class AdminSponsorshipListResponse(BaseModel):
    """Admin sponsorship list response"""
    items: List[AdminSponsorshipItem]
    total: int


class ModeratorListItem(BaseModel):
    """Moderator list item for dropdown"""
    id: UUID
    name: Optional[str]
    email: str


class ModeratorListResponse(BaseModel):
    """List of available moderators"""
    moderators: List[ModeratorListItem]
