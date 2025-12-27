"""Moderator API schemas"""
from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.schemas.common import GCBBaseModel


class QueueItem(GCBBaseModel):
    """Moderation queue item"""
    test_id: UUID
    model_name: str
    user_name: str
    overall_score: Optional[float]
    status: str
    trust_tier: str
    created_at: datetime
    priority: int


class QueueResponse(BaseModel):
    """Moderation queue response"""
    items: List[QueueItem]
    total: int


class VerdictReview(BaseModel):
    """Individual verdict review"""
    result_id: UUID
    verdict: str  # 'agree', 'disagree', 'unsure'
    notes: Optional[str] = None


class ReviewSubmissionRequest(BaseModel):
    """Review submission request"""
    test_id: UUID
    verdict_reviews: List[VerdictReview]
    overall_assessment: str  # 'verified', 'concerns', 'escalated'
    notes: Optional[str] = None


class ReviewSubmissionResponse(BaseModel):
    """Review submission response"""
    review_id: UUID
    test_id: UUID
    trust_tier: str
    requires_second_review: bool


class ModeratorActivityItem(GCBBaseModel):
    """Moderator activity item"""
    review_id: UUID
    test_id: Optional[UUID] = None  # None for CLI submissions
    submission_id: Optional[UUID] = None  # None for platform tests
    model_name: str
    action: str
    review_type: str  # 'platform_test' or 'cli_submission'
    duration_seconds: Optional[int]
    created_at: datetime


class ModeratorActivityResponse(BaseModel):
    """Moderator activity response"""
    items: List[ModeratorActivityItem]
    total: int


class ModeratorStatsResponse(BaseModel):
    """Moderator stats response"""
    personal: Dict
    system_wide: Dict


class CommunitySubmissionReviewRequest(BaseModel):
    """Community submission review request"""
    action: str  # 'approve' or 'reject'
    notes: Optional[str] = None


class CommunitySubmissionReviewResponse(BaseModel):
    """Community submission review response"""
    submission_id: UUID
    status: str
    message: str
