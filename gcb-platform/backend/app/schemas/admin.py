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
    can_view_benchmark: bool = False
    can_edit_benchmark: bool = False
    can_moderate: bool = False
    can_manage_blog: bool = False
    can_admin: bool = False


class UserListResponse(BaseModel):
    """User list response"""
    users: List[UserListItem]
    total: int


class UpdateUserRoleRequest(BaseModel):
    """Update user role request"""
    role: str  # 'user', 'moderator', 'blog_manager', 'benchmark_viewer', 'benchmark_administrator', 'admin'


class UpdateUserRoleResponse(BaseModel):
    """Update user role response"""
    user_id: UUID
    role: str
    message: str


class UpdateUserPermissionsRequest(BaseModel):
    """Update user permissions request"""
    can_view_benchmark: Optional[bool] = None
    can_edit_benchmark: Optional[bool] = None
    can_moderate: Optional[bool] = None
    can_manage_blog: Optional[bool] = None
    can_admin: Optional[bool] = None


class UserPermissionsResponse(BaseModel):
    """User permissions response"""
    user_id: UUID
    can_view_benchmark: bool
    can_edit_benchmark: bool
    can_moderate: bool
    can_manage_blog: bool
    can_admin: bool
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
    metadata: Optional[Dict] = None  # Only 'difficulty' should be stored here
    expected_verdict: Optional[str] = None
    is_locked: Optional[bool] = False
    notes: Optional[str] = None


class QuestionUpdateRequest(BaseModel):
    """Question update request"""
    tier: Optional[int] = None
    category: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict] = None  # Only 'difficulty' should be stored here
    expected_verdict: Optional[str] = None
    is_locked: Optional[bool] = None
    notes: Optional[str] = None


class QuestionResponse(BaseModel):
    """Question response"""
    id: UUID
    question_set_id: UUID
    tier: int
    category: str
    content: str
    metadata: Optional[Dict] = None  # Only 'difficulty' should be stored here
    expected_verdict: Optional[str] = None
    is_locked: bool
    notes: Optional[str] = None


class QuestionSetCreateRequest(BaseModel):
    """Question set create request"""
    semantic_version: str = "1.0"
    marketing_version: str = "Version 1"
    notes: Optional[str] = None
    target_question_count: Optional[int] = None  # Optional target (e.g., 200 or 300)


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
    target_is_auto: bool  # True if target was auto-calculated from actual count
    tier_stats: Dict[int, TierStats]
    difficulty_stats: DifficultyStats
    category_difficulty_matrix: Dict[str, CategoryDifficultyBreakdown]  # category -> difficulty breakdown


class QuestionSetCopyRequest(BaseModel):
    """Question set copy request"""
    new_semantic_version: str
    new_marketing_version: str
    notes: Optional[str] = None


class QuestionSetUpdateTargetRequest(BaseModel):
    """Request to update question set target"""
    target_question_count: Optional[int] = None  # Set to None to use auto-calculation


class QuestionSetUpdateTargetResponse(BaseModel):
    """Response after updating question set target"""
    question_set_id: UUID
    target_question_count: Optional[int]
    message: str
