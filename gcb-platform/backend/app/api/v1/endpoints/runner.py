"""Runner API endpoints (for CLI)"""
import os
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, Tuple

from app.core.auth import get_db
from app.db.models.user import User
from app.db.models.user_api_key import UserAPIKey
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.db.models.methodology_version import MethodologyVersion
from app.core.rate_limit import RateLimitDependency
from app.api.v1.endpoints.api_keys import validate_api_key

router = APIRouter()


# CLI version info - updated when new builds are published
# This can also be read from a database table or config file
CLI_VERSION_INFO = {
    "version": os.getenv("GCB_RUNNER_VERSION", "0.1.0"),
    "minimum_version": "0.1.0",
    "release_notes": "Initial release",
    "downloads": {
        "macos-arm64": {
            "filename": "gcb-runner-macos-arm64",
            "sha256": os.getenv("GCB_RUNNER_SHA256_MACOS_ARM64", ""),
        },
        "macos-x64": {
            "filename": "gcb-runner-macos-x64",
            "sha256": os.getenv("GCB_RUNNER_SHA256_MACOS_X64", ""),
        },
        "linux-x64": {
            "filename": "gcb-runner-linux-x64",
            "sha256": os.getenv("GCB_RUNNER_SHA256_LINUX_X64", ""),
        },
        "windows-x64": {
            "filename": "gcb-runner.exe",
            "sha256": os.getenv("GCB_RUNNER_SHA256_WINDOWS", ""),
        },
    }
}


class APIKeyAuth:
    """Dependency for API key authentication that returns the user"""
    
    async def __call__(
        self,
        x_api_key: Optional[str] = Header(None),
        db: Session = Depends(get_db)
    ) -> Tuple[UserAPIKey, User]:
        """Validate API key and return the key and user"""
        if not x_api_key:
            raise HTTPException(
                status_code=401,
                detail="API key required. Get one from your dashboard at https://greatcommissionbenchmark.ai/dashboard/settings"
            )
        
        api_key_record, user = validate_api_key(db, x_api_key)
        
        if not api_key_record or not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired API key"
            )
        
        return api_key_record, user


# Dependency instance
require_api_key = APIKeyAuth()

# Rate limiter for runner endpoints: 50 requests per hour
runner_rate_limit = RateLimitDependency("runner")


@router.get("/latest")
async def get_runner_latest(request: Request):
    """
    Get the latest CLI version info for auto-updates.
    
    This endpoint is public (no auth required) so the CLI can check
    for updates without requiring an API key.
    
    Returns version info, download URLs, and SHA256 hashes for verification.
    """
    # Build download URLs based on the frontend URL
    frontend_url = os.getenv("FRONTEND_URL", "https://greatcommissionbenchmark.ai")
    base_download_url = f"{frontend_url}/downloads"
    
    downloads = {}
    for platform, info in CLI_VERSION_INFO["downloads"].items():
        if info.get("sha256"):  # Only include platforms with hashes set
            downloads[platform] = {
                "url": f"{base_download_url}/{info['filename']}",
                "filename": info["filename"],
                "sha256": info["sha256"],
            }
    
    return {
        "version": CLI_VERSION_INFO["version"],
        "minimum_version": CLI_VERSION_INFO["minimum_version"],
        "release_notes": CLI_VERSION_INFO["release_notes"],
        "downloads": downloads,
    }


@router.get("/versions")
async def get_runner_versions(
    request: Request,
    include_drafts: bool = Query(False, description="Include draft/locked versions for testing"),
    db: Session = Depends(get_db),
    auth: Tuple[UserAPIKey, User] = Depends(require_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get available benchmark versions for CLI
    
    By default, only returns published versions (active/archived).
    Pass include_drafts=true to also include draft and locked versions for testing.
    """
    # auth contains (api_key_record, user) - available for logging/tracking
    # Build status filter - always include published versions
    statuses = ["active", "archived"]
    if include_drafts:
        statuses.extend(["draft", "locked"])
    
    question_sets = db.query(QuestionSet).filter(
        QuestionSet.status.in_(statuses)
    ).order_by(QuestionSet.created_at.desc()).all()
    
    versions = []
    for qs in question_sets:
        question_count = db.query(Question).filter(Question.question_set_id == qs.id).count()
        
        # Map status for display: active -> current, keep others as-is
        display_status = "current" if qs.status == "active" else qs.status
        
        versions.append({
            "semantic_version": qs.semantic_version,
            "marketing_version": qs.marketing_version,
            "status": display_status,
            "question_count": question_count,
            "release_date": qs.created_at.isoformat() if qs.created_at else None,
            "is_draft": qs.status in ["draft", "locked"]
        })
    
    return {
        "versions": versions,
        "current_version": next((v["semantic_version"] for v in versions if v["status"] == "current"), None)
    }


@router.get("/questions")
async def get_runner_questions(
    request: Request,
    version: Optional[str] = None,
    db: Session = Depends(get_db),
    auth: Tuple[UserAPIKey, User] = Depends(require_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get full question set for CLI"""
    # auth contains (api_key_record, user) - available for logging/tracking
    # Get question set
    if version:
        question_set = db.query(QuestionSet).filter(QuestionSet.semantic_version == version).first()
    else:
        question_set = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Get questions
    questions = db.query(Question).filter(
        Question.question_set_id == question_set.id
    ).order_by(Question.tier, Question.category).all()
    
    # Get methodology version
    methodology_version = db.query(MethodologyVersion).filter(
        MethodologyVersion.question_set_id == question_set.id
    ).order_by(MethodologyVersion.active_from.desc()).first()
    
    # Build response
    questions_data = []
    for q in questions:
        questions_data.append({
            "id": str(q.id),
            "content": q.content,
            "category": q.category,
            "tier": q.tier,
            "subcategory": q.subcategory
        })
    
    return {
        "version": question_set.semantic_version,
        "marketing_version": question_set.marketing_version,
        "questions": questions_data,
        "scoring_config": methodology_version.scoring_config if methodology_version else {
            "tier1_weight": 0.70,
            "tier2_weight": 0.20,
            "tier3_weight": 0.10
        },
        "is_draft": question_set.status in ["draft", "locked"]
    }


@router.get("/judge-prompts")
async def get_judge_prompts(
    request: Request,
    version: Optional[str] = None,
    db: Session = Depends(get_db),
    auth: Tuple[UserAPIKey, User] = Depends(require_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get judge prompts for each tier.
    
    Prompts are served from code (single source of truth) rather than database.
    This ensures consistency between server-side judging and CLI judging.
    """
    # Import prompts from the judge service (single source of truth)
    from app.services.judge import TIER1_JUDGE_PROMPT, TIER2_JUDGE_PROMPT, TIER3_JUDGE_PROMPT
    
    # Get question set for version info
    if version:
        question_set = db.query(QuestionSet).filter(QuestionSet.semantic_version == version).first()
    else:
        question_set = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Serve prompts from code (single source of truth)
    # These are the same prompts used for server-side judging
    return {
        "version": question_set.semantic_version,
        "prompts": {
            "tier1_task": TIER1_JUDGE_PROMPT,
            "tier2_doctrine": TIER2_JUDGE_PROMPT,
            "tier3_worldview": TIER3_JUDGE_PROMPT
        }
    }