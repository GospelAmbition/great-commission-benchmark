"""Public API schemas"""
from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from app.schemas.common import PaginationResponse, GCBBaseModel


class ModelSummary(GCBBaseModel):
    """Model summary for leaderboard"""
    id: UUID
    name: str
    provider: str
    model_id: str
    description: Optional[str] = None  # Short catalog description (e.g. from OpenRouter)


class TestRunSummary(GCBBaseModel):
    """Test run summary"""
    id: UUID
    trust_tier: Optional[str] = None
    completed_at: Optional[datetime] = None
    question_set_version: str


class Scores(GCBBaseModel):
    """Score breakdown"""
    overall: float
    tier1: float
    tier2: float
    tier3: float


class VerdictDistribution(GCBBaseModel):
    """Verdict distribution"""
    ACCEPTED: int = 0
    COMPROMISED: int = 0
    REFUSED: int = 0
    ERROR: int = 0


class ScoreRange(GCBBaseModel):
    """Score range for aggregated results"""
    min_score: Optional[float] = None
    max_score: Optional[float] = None


class LeaderboardEntry(GCBBaseModel):
    """Leaderboard entry"""
    rank: int
    model: ModelSummary
    test_run: TestRunSummary
    scores: Scores
    category_scores: Dict[str, float]
    verdict_distribution: VerdictDistribution
    total_questions: int
    metadata: Dict[str, str]
    # Legacy fields (retained for API compatibility, always 1/None with most-recent-test scoring)
    test_count: int = 1  # Always 1 — leaderboard shows most recent test only
    score_range: Optional[ScoreRange] = None  # Not used — no longer averaging across tests


class LeaderboardResponse(GCBBaseModel):
    """Leaderboard response"""
    semantic_version: str
    marketing_version: str
    filters: Dict[str, Optional[str]]
    total_models: int
    entries: List[LeaderboardEntry]
    pagination: PaginationResponse


class ModelListItem(GCBBaseModel):
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


class ModelsListResponse(GCBBaseModel):
    """Models list response"""
    models: List[ModelListItem]
    pagination: PaginationResponse


class ModelInfo(GCBBaseModel):
    """Model info in detail response"""
    id: str
    name: str
    provider: str
    model_id: str


class TestResultInfo(GCBBaseModel):
    """Best test result info"""
    test_run_id: str
    scores: Scores
    trust_tier: Optional[str] = None
    completed_at: Optional[str] = None
    benchmark_version: str


class TestHistoryItem(GCBBaseModel):
    """Test history item"""
    test_run_id: str
    overall_score: float
    benchmark_version: str
    completed_at: Optional[str] = None
    trust_tier: Optional[str] = None


class CategoryBreakdown(GCBBaseModel):
    """Category breakdown stats"""
    total: int
    passed: int
    score: float = 0.0


class ModelDetailResponse(GCBBaseModel):
    """Model detail response"""
    model: ModelInfo
    best_result: Optional[TestResultInfo] = None
    test_history: List[TestHistoryItem]
    category_breakdown: Dict[str, CategoryBreakdown]
    leaderboard_rank: Optional[int] = None
    total_models_tested: int


class VersionInfo(GCBBaseModel):
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


class VersionsResponse(GCBBaseModel):
    """Versions response"""
    versions: List[VersionInfo]
    current_version: str


class StatsResponse(GCBBaseModel):
    """Platform statistics"""
    total_models_tested: int
    total_test_runs: int
    current_benchmark_version: str
    top_score: float
    average_score: float
    providers_represented: int
    last_updated: datetime


class ComparisonModelInfo(GCBBaseModel):
    """Model info for comparison"""
    id: str
    name: str
    provider: str


class ComparisonModelData(GCBBaseModel):
    """Model data for comparison response"""
    model: ComparisonModelInfo
    test_run_id: str
    scores: Scores
    verdict_distribution: Dict[str, int]


class ScoreDelta(GCBBaseModel):
    """Score delta for comparison"""
    overall: float
    tier1: float
    tier2: float
    tier3: float


class ComparisonData(GCBBaseModel):
    """Comparison data"""
    score_delta: Optional[ScoreDelta] = None


class ComparisonResponse(GCBBaseModel):
    """Model comparison response"""
    semantic_version: str
    marketing_version: str
    models: List[ComparisonModelData]
    comparison: ComparisonData


class StripePublishableKeyResponse(GCBBaseModel):
    """Stripe publishable key response"""
    publishable_key: Optional[str] = None
    is_configured: bool
