"""User API schemas"""
from typing import Optional, List, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

from app.schemas.common import PaginationResponse


class UserProfile(BaseModel):
    """User profile"""
    id: UUID
    auth0_id: str
    email: str
    name: Optional[str] = None
    role: str
    organization: Optional[str] = None
    created_at: datetime


class UserStats(BaseModel):
    """User statistics"""
    total_tests: int = 0
    completed_tests: int = 0
    pending_tests: int = 0
    running_tests: int = 0
    total_submissions: int = 0
    approved_submissions: int = 0
    total_contribution: float = 0.0


class UserProfileResponse(BaseModel):
    """User profile response"""
    user: UserProfile
    stats: UserStats


class UpdateProfileRequest(BaseModel):
    """Update profile request"""
    name: Optional[str] = None
    organization: Optional[str] = None


class TestListItem(BaseModel):
    """Test list item"""
    id: UUID
    model: dict
    status: str
    payment_status: str
    scores: Optional[dict] = None
    progress: dict
    benchmark_version: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    trust_tier: str
    leaderboard_rank: Optional[int] = None


class UserTestsResponse(BaseModel):
    """User tests response"""
    tests: List[TestListItem]
    pagination: PaginationResponse


class SubmissionListItem(BaseModel):
    """Submission list item"""
    id: UUID
    model_name: str
    model_provider: str
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class UserSubmissionsResponse(BaseModel):
    """User submissions response"""
    submissions: List[SubmissionListItem]
    pagination: PaginationResponse


class ActivityItem(BaseModel):
    """Activity feed item"""
    type: str
    timestamp: datetime
    title: str
    description: str
    link: Optional[str] = None


class UserActivityResponse(BaseModel):
    """User activity response"""
    activities: List[ActivityItem]


class NotificationPreferences(BaseModel):
    """Notification preferences"""
    test_completed: bool = True
    test_failed: bool = True
    submission_approved: bool = True
    submission_rejected: bool = True
    payment_confirmation: bool = True
    newsletter: bool = False


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response"""
    preferences: NotificationPreferences