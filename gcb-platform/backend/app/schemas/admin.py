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


class QuestionResponse(BaseModel):
    """Question response"""
    id: UUID
    question_set_id: UUID
    tier: int
    category: str
    content: str
    metadata: Optional[Dict] = None
    is_locked: bool


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
