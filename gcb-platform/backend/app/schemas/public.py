"""Public API schemas"""
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.schemas.common import PaginationResponse


class ModelSummary(BaseModel):
    """Model summary for leaderboard"""
    id: UUID
    name: str
    provider: str
    model_id: str


class TestRunSummary(BaseModel):
    """Test run summary"""
    id: UUID
    trust_tier: str
    completed_at: Optional[datetime]
    question_set_version: str


class Scores(BaseModel):
    """Score breakdown"""
    overall: float
    tier1: float
    tier2: float
    tier3: float


class CategoryScores(BaseModel):
    """Category score breakdown"""
    pass  # Dynamic dict in response


class VerdictDistribution(BaseModel):
    """Verdict distribution"""
    ACCEPTED: int = 0
    COMPROMISED: int = 0
    REFUSED: int = 0
    ERROR: int = 0


class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    model: ModelSummary
    test_run: TestRunSummary
    scores: Scores
    category_scores: Dict[str, float]
    verdict_distribution: VerdictDistribution
    total_questions: int
    metadata: Dict[str, str]


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    semantic_version: str
    marketing_version: str
    filters: Dict[str, Optional[str]]
    total_models: int
    entries: List[LeaderboardEntry]
    pagination: PaginationResponse


class ModelListItem(BaseModel):
    """Model list item"""
    id: UUID
    name: str
    provider: str
    model_id: str
    description: Optional[str] = None
    latest_score: Optional[float] = None
    test_count: int = 0
    first_tested: Optional[datetime] = None
    last_tested: Optional[datetime] = None


class ModelsListResponse(BaseModel):
    """Models list response"""
    models: List[ModelListItem]
    pagination: PaginationResponse


class ModelDetailResponse(BaseModel):
    """Model detail response"""
    model: dict
    best_result: dict
    test_history: List[dict]
    category_breakdown: Dict[str, dict]
    leaderboard_rank: Optional[int] = None
    total_models_tested: int


class VersionInfo(BaseModel):
    """Version information"""
    semantic_version: str
    marketing_version: str
    status: str
    release_date: Optional[str] = None
    question_count: int
    tier_distribution: Dict[str, int]
    scoring_weights: Dict[str, float]
    models_tested: int = 0
    changelog_url: Optional[str] = None


class VersionsResponse(BaseModel):
    """Versions response"""
    versions: List[VersionInfo]
    current_version: str


class StatsResponse(BaseModel):
    """Platform statistics"""
    total_models_tested: int
    total_test_runs: int
    current_benchmark_version: str
    top_score: float
    average_score: float
    providers_represented: int
    last_updated: datetime


class ComparisonResponse(BaseModel):
    """Model comparison response"""
    semantic_version: str
    marketing_version: str
    models: List[dict]
    comparison: dict