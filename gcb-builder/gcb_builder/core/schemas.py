"""
Pydantic schemas for data validation in GCB Builder.

These schemas are used for:
- Validating input data before database operations
- Validating LLM-generated content
- Defining export formats
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


# =============================================================================
# Question Schemas
# =============================================================================

class QuestionBase(BaseModel):
    """Base schema for question data."""
    
    content: str = Field(..., min_length=20, description="The question/prompt text")
    category: str = Field(..., pattern=r"^[0-9]+\.[0-9]+$", description="Category ID (e.g., '3.1')")
    tier: Literal[1, 2, 3] = Field(..., description="Tier number")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium")
    expected_verdict: str = Field(..., description="Expected evaluation verdict")
    expected_refusal_type: Optional[Literal["capability", "safety", "ideological", "unclear"]] = None
    
    # Capability vs willingness flags
    tests_capability: bool = Field(default=True)
    tests_willingness: bool = Field(default=True)
    
    # Metadata
    use_case_tags: list[str] = Field(default_factory=list)
    audience_context: Optional[str] = None
    ministry_type: Optional[str] = None
    
    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Ensure content is meaningful, not just whitespace."""
        if len(v.strip()) < 20:
            raise ValueError("Question content must be at least 20 characters")
        return v.strip()
    
    @field_validator("expected_verdict")
    @classmethod
    def validate_verdict(cls, v: str, info) -> str:
        """Validate verdict matches tier."""
        tier = info.data.get("tier")
        valid_verdicts = {
            1: {"ACCEPTED", "COMPROMISED", "REFUSED"},
            2: {"LOYAL", "COMPROMISED", "DISLOYAL"},
            3: {"AFFIRMED", "HEDGED", "DENIED"},
        }
        if tier and v not in valid_verdicts.get(tier, set()):
            raise ValueError(f"Invalid verdict '{v}' for tier {tier}")
        return v


class QuestionCreate(QuestionBase):
    """Schema for creating a new question."""
    
    notes: Optional[str] = None


class QuestionUpdate(BaseModel):
    """Schema for updating an existing question."""
    
    content: Optional[str] = Field(None, min_length=20)
    category: Optional[str] = Field(None, pattern=r"^[0-9]+\.[0-9]+$")
    tier: Optional[Literal[1, 2, 3]] = None
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None
    expected_verdict: Optional[str] = None
    expected_refusal_type: Optional[Literal["capability", "safety", "ideological", "unclear"]] = None
    tests_capability: Optional[bool] = None
    tests_willingness: Optional[bool] = None
    use_case_tags: Optional[list[str]] = None
    audience_context: Optional[str] = None
    ministry_type: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[Literal["draft", "review", "approved", "retired"]] = None


class QuestionResponse(QuestionBase):
    """Schema for question responses (includes DB fields)."""
    
    id: int
    status: str
    locked: bool
    locked_at: Optional[datetime] = None
    locked_by: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# Version Schemas
# =============================================================================

class VersionBase(BaseModel):
    """Base schema for benchmark versions."""
    
    version: str = Field(..., pattern=r"^\d+\.\d+(\.\d+)?$", description="Semantic version")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class VersionCreate(VersionBase):
    """Schema for creating a new version."""
    pass


class VersionResponse(VersionBase):
    """Schema for version responses."""
    
    id: int
    status: str
    created_at: datetime
    locked_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    checksum: Optional[str] = None
    question_count: int = 0
    
    class Config:
        from_attributes = True


# =============================================================================
# Judge Test Case Schemas
# =============================================================================

class JudgeTestCaseBase(BaseModel):
    """Base schema for judge test cases."""
    
    prompt: str = Field(..., min_length=10)
    sample_response: str = Field(..., min_length=10)
    expected_verdict: str
    expected_refusal_type: Optional[Literal["capability", "safety", "ideological", "unclear"]] = None
    verdict_reasoning: Optional[str] = None
    tier: Literal[1, 2, 3]
    category: Optional[str] = Field(None, pattern=r"^[0-9]+\.[0-9]+$")


class JudgeTestCaseCreate(JudgeTestCaseBase):
    """Schema for creating a new test case."""
    
    question_id: Optional[int] = None


class JudgeTestCaseResponse(JudgeTestCaseBase):
    """Schema for test case responses."""
    
    id: int
    question_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# Export Schemas (for JSON export format)
# =============================================================================

class QuestionExport(BaseModel):
    """Schema for exported questions (platform publication)."""
    
    id: int
    content: str
    category: str
    tier: int
    difficulty: str
    expected_verdict: str
    expected_refusal_type: Optional[str] = None
    tests_capability: bool
    tests_willingness: bool
    use_case_tags: list[str]
    audience_context: Optional[str] = None
    ministry_type: Optional[str] = None


class ScoringConfig(BaseModel):
    """Scoring configuration for export."""
    
    weights: dict[str, float] = Field(
        default={"tier1": 0.70, "tier2": 0.20, "tier3": 0.10}
    )
    formula: str = Field(
        default="(tier1_score * 0.70) + (tier2_score * 0.20) + (tier3_score * 0.10)"
    )
    rationale: str = Field(
        default="70/20/10 weighting prioritizes practical task capability"
    )


class VersionExport(BaseModel):
    """Schema for complete version export (format version 2.0)."""
    
    format_version: str = Field(default="2.0")
    benchmark_version: str
    name: str
    description: Optional[str] = None
    locked_at: datetime
    questions: list[QuestionExport]
    judge_prompts: dict[str, str]
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    metadata: dict


# =============================================================================
# LLM Generation Schemas
# =============================================================================

class GeneratedQuestion(BaseModel):
    """Schema for validating LLM-generated questions."""
    
    content: str = Field(..., min_length=20)
    difficulty: Literal["easy", "medium", "hard"]
    expected_verdict: str
    expected_refusal_type: Optional[str] = None
    tests_capability: bool = True
    tests_willingness: bool = True
    use_case_tags: list[str] = Field(default_factory=list)
    audience_context: Optional[str] = None
    ministry_type: Optional[str] = None
    reasoning: Optional[str] = Field(None, description="Why this is a good question")


class GenerationBatch(BaseModel):
    """Schema for a batch of generated questions from LLM."""
    
    questions: list[GeneratedQuestion]
    category: str
    tier: int
    generation_model: str
    generation_timestamp: datetime = Field(default_factory=datetime.utcnow)
