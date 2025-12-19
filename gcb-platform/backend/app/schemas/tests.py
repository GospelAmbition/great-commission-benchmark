"""Tests API schemas"""
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class CreateTestRequest(BaseModel):
    """Create test request"""
    model_id: UUID
    question_set_id: Optional[UUID] = None  # Defaults to current version
    system_prompt: Optional[str] = None


class CreateTestResponse(BaseModel):
    """Create test response"""
    test_id: UUID
    cost_estimate: float
    payment_intent_id: Optional[str] = None
    status: str
    fee_waived: bool = False


class TestProgressResponse(BaseModel):
    """Test progress response"""
    test_id: UUID
    status: str
    progress: Dict[str, int]  # completed, total, percentage
    current_tier: Optional[int] = None
    current_category: Optional[str] = None
    estimated_completion: Optional[datetime] = None
    started_at: Optional[datetime] = None


class CancelTestResponse(BaseModel):
    """Cancel test response"""
    test_id: UUID
    status: str
    refund_eligible: bool
    refund_amount: Optional[float] = None


class RetestRequest(BaseModel):
    """Retest request"""
    system_prompt: Optional[str] = None


class RetestResponse(BaseModel):
    """Retest response"""
    new_test_id: UUID
    original_test_id: UUID
    cost_estimate: float
    fee_waived: bool = False


class RetestHistoryItem(BaseModel):
    """Single retest history entry"""
    test_id: UUID
    completed_at: Optional[datetime]
    overall_score: Optional[float]
    tier1_score: Optional[float]
    tier2_score: Optional[float]
    tier3_score: Optional[float]
    trust_tier: str
    benchmark_version: str


class RetestHistoryResponse(BaseModel):
    """Retest history response"""
    model_id: UUID
    model_name: str
    tests: List[RetestHistoryItem]
    total_tests: int


class ScoreComparison(BaseModel):
    """Score comparison between two tests"""
    overall: float
    tier1: float
    tier2: float
    tier3: float


class CategoryComparison(BaseModel):
    """Category comparison data"""
    category: str
    test1_score: float
    test2_score: float
    delta: float


class TestComparisonResponse(BaseModel):
    """Test comparison response"""
    test1: dict
    test2: dict
    score_delta: ScoreComparison
    category_comparison: List[CategoryComparison]
    verdict_comparison: dict
    improved_categories: List[str]
    declined_categories: List[str]