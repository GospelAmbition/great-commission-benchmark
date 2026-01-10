"""User API schemas"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.schemas.common import PaginationResponse, GCBBaseModel


class UserProfile(GCBBaseModel):
    """User profile"""
    id: UUID
    auth0_id: str
    email: str
    name: Optional[str] = None
    role: str
    organization: Optional[str] = None
    tester_agreement_accepted: bool = False
    created_at: datetime
    # Permissions
    can_view_benchmark: bool = False
    can_edit_benchmark: bool = False
    can_moderate: bool = False
    can_manage_blog: bool = False
    can_admin: bool = False


class UserStats(GCBBaseModel):
    """User statistics"""
    total_tests: int = 0
    completed_tests: int = 0
    pending_tests: int = 0
    running_tests: int = 0
    total_submissions: int = 0
    approved_submissions: int = 0
    total_contribution: float = 0.0


class UserProfileResponse(GCBBaseModel):
    """User profile response"""
    user: UserProfile
    stats: UserStats


class UpdateProfileRequest(GCBBaseModel):
    """Update profile request"""
    name: Optional[str] = None
    organization: Optional[str] = None


class TestModelInfo(GCBBaseModel):
    """Model info in test list item"""
    id: str
    name: str
    provider: str
    model_id: Optional[str] = None


class TestScores(GCBBaseModel):
    """Scores in test list item"""
    overall: float
    tier1: float
    tier2: float
    tier3: float


class TestProgress(GCBBaseModel):
    """Progress info in test list item"""
    completed: int
    total: int
    percentage: int


class TestListItem(GCBBaseModel):
    """Test list item"""
    id: UUID
    model: TestModelInfo
    status: str
    payment_status: str
    scores: Optional[TestScores] = None
    progress: TestProgress
    benchmark_version: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    trust_tier: Optional[str] = None
    leaderboard_rank: Optional[int] = None


class UserTestsResponse(GCBBaseModel):
    """User tests response"""
    tests: List[TestListItem]
    pagination: PaginationResponse


class SubmissionListItem(GCBBaseModel):
    """Submission list item"""
    id: UUID
    model_name: str
    model_provider: str
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class UserSubmissionsResponse(GCBBaseModel):
    """User submissions response"""
    submissions: List[SubmissionListItem]
    pagination: PaginationResponse


class ActivityItem(GCBBaseModel):
    """Activity feed item"""
    type: str
    timestamp: datetime
    title: str
    description: str
    link: Optional[str] = None


class UserActivityResponse(GCBBaseModel):
    """User activity response"""
    activities: List[ActivityItem]


class NotificationPreferences(GCBBaseModel):
    """Notification preferences"""
    test_completed: bool = True
    test_failed: bool = True
    submission_approved: bool = True
    submission_rejected: bool = True
    payment_confirmation: bool = True
    newsletter: bool = False


class NotificationPreferencesResponse(GCBBaseModel):
    """Notification preferences response"""
    preferences: NotificationPreferences
