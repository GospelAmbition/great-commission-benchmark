"""Admin API schemas"""
from typing import Optional, List, Dict
from pydantic import BaseModel
from uuid import UUID


class UserListItem(BaseModel):
    """User list item"""
    id: UUID
    email: str
    name: Optional[str]
    role: str
    created_at: str
    test_count: int
    fee_waived: Optional[bool] = None
    fee_waived_reason: Optional[str] = None


class UserListResponse(BaseModel):
    """User list response"""
    users: List[UserListItem]
    total: int


class UpdateUserRoleRequest(BaseModel):
    """Update user role request"""
    role: str  # 'user', 'moderator', 'admin'


class UpdateUserRoleResponse(BaseModel):
    """Update user role response"""
    user_id: UUID
    role: str
    message: str


class UpdateFeeWaiverRequest(BaseModel):
    """Update fee waiver request"""
    waived: bool
    reason: Optional[str] = None


class UpdateFeeWaiverResponse(BaseModel):
    """Update fee waiver response"""
    user_id: UUID
    fee_waived: bool
    fee_waived_reason: Optional[str] = None
    message: str


class QuestionImportRequest(BaseModel):
    """Question import request"""
    questions: List[Dict]  # Question data
    dry_run: bool = False


class QuestionImportResponse(BaseModel):
    """Question import response"""
    imported: int
    errors: List[str]
    dry_run: bool


class QuestionCreateRequest(BaseModel):
    """Question create request"""
    question_set_id: UUID
    tier: int
    category: str
    content: str
    metadata: Optional[Dict] = None


class QuestionUpdateRequest(BaseModel):
    """Question update request"""
    tier: Optional[int] = None
    category: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict] = None
    is_locked: Optional[bool] = None
    notes: Optional[str] = None


class QuestionResponse(BaseModel):
    """Question response"""
    id: UUID
    question_set_id: UUID
    tier: int
    category: str
    content: str
    metadata: Optional[Dict] = None
    is_locked: bool
    notes: Optional[str] = None


class QuestionSetCreateRequest(BaseModel):
    """Question set create request"""
    semantic_version: str = "1.0"
    marketing_version: str = "Version 1"
    notes: Optional[str] = None


class VersionCreateRequest(BaseModel):
    """Version create request"""
    semantic_version: str
    question_ids: List[UUID]
    description: Optional[str] = None


class VersionPublishRequest(BaseModel):
    """Version publish request"""
    version: str


class AdminStatsResponse(BaseModel):
    """Admin stats response"""
    users: Dict
    tests: Dict
    revenue: Dict
    moderation: Dict
    api_keys: Dict


class CategoryDifficultyBreakdown(BaseModel):
    """Difficulty breakdown for a category"""
    easy: int = 0
    medium: int = 0
    hard: int = 0


class CategoryStats(BaseModel):
    """Category statistics"""
    count: int
    target: int
    difficulty: CategoryDifficultyBreakdown = CategoryDifficultyBreakdown()


class TierStats(BaseModel):
    """Tier statistics"""
    count: int
    target: int
    categories: Dict[str, CategoryStats]


class DifficultyCount(BaseModel):
    """Difficulty count for a single difficulty level"""
    count: int
    percentage: float


class DifficultyStats(BaseModel):
    """Difficulty distribution statistics"""
    easy: DifficultyCount
    medium: DifficultyCount
    hard: DifficultyCount


class QuestionSetStatsResponse(BaseModel):
    """Question set statistics response"""
    question_set_id: UUID
    semantic_version: str
    marketing_version: str
    total_questions: int
    target_total: int
    tier_stats: Dict[int, TierStats]
    difficulty_stats: DifficultyStats
    category_difficulty_matrix: Dict[str, CategoryDifficultyBreakdown]  # category -> difficulty breakdown


class QuestionSetCopyRequest(BaseModel):
    """Question set copy request"""
    new_semantic_version: str
    new_marketing_version: str
    notes: Optional[str] = None
