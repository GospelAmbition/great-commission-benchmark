"""Runner API endpoints (for CLI)"""
import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, Tuple, Dict, List

from app.core.auth import get_db, has_permission
from app.db.models.user import User
from app.db.models.user_api_key import UserAPIKey
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.model import Model
from app.db.models.test_run import TestRun
from app.core.rate_limit import RateLimitDependency
from app.api.v1.endpoints.api_keys import validate_api_key

logger = logging.getLogger(__name__)

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


@router.get("/user-info")
async def get_user_info(
    request: Request,
    db: Session = Depends(get_db),
    auth: Tuple[UserAPIKey, User] = Depends(require_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get user information for the authenticated API key.
    
    Returns the user's role and permission flags for controlling
    access to sensitive data like question content in the results viewer.
    
    Roles with elevated access:
    - admin: Full access to all features
    - benchmark_developer: Access to benchmark development features including question content
    - moderator: Access to moderation features
    - user: Standard user access
    """
    api_key_record, user = auth
    
    # Determine permission flags based on permissions (admin cascades)
    from app.core.auth import has_permission
    
    is_admin = has_permission(user, "can_admin")
    is_benchmark_developer = has_permission(user, "can_edit_benchmark")
    is_moderator = has_permission(user, "can_moderate")
    
    return {
        "role": user.role,
        "is_admin": is_admin,
        "is_benchmark_developer": is_benchmark_developer,
        "is_moderator": is_moderator,
        "email": user.email,
        "name": user.name,
        "permissions": {
            "can_view_benchmark": has_permission(user, "can_view_benchmark"),
            "can_edit_benchmark": has_permission(user, "can_edit_benchmark"),
            "can_moderate": has_permission(user, "can_moderate"),
            "can_manage_blog": has_permission(user, "can_manage_blog"),
            "can_admin": has_permission(user, "can_admin")
        }
    }


@router.get("/models")
async def get_runner_models(
    request: Request,
    db: Session = Depends(get_db),
    auth: Tuple[UserAPIKey, User] = Depends(require_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get all published models for bulk testing.
    
    Returns active models with their model_id strings (OpenRouter-style identifiers).
    Restricted to admin or benchmark editor users for use by the bulk tester.
    """
    api_key_record, user = auth
    
    # Permission gate: require admin or benchmark editor
    if not has_permission(user, "can_admin") and not has_permission(user, "can_edit_benchmark"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Requires admin or benchmark editor access."
        )
    
    models = db.query(Model).filter(
        Model.is_active == True
    ).order_by(Model.name).all()
    
    # Get the current active question set for version context
    active_qs = db.query(QuestionSet).filter(
        QuestionSet.status == "active"
    ).first()
    current_version = active_qs.semantic_version if active_qs else None
    
    model_items = []
    for model in models:
        # Check if this model has already been tested on the current version
        latest_test = None
        if active_qs:
            latest_test = db.query(TestRun).filter(
                TestRun.model_id == model.id,
                TestRun.question_set_id == active_qs.id,
                TestRun.status == "completed"
            ).order_by(TestRun.completed_at.desc()).first()
        
        model_items.append({
            "id": str(model.id),
            "model_id": model.model_id,
            "name": model.name,
            "provider": model.provider,
            "last_tested_version": current_version if latest_test else None,
            "last_tested_at": latest_test.completed_at.isoformat() if latest_test and latest_test.completed_at else None,
        })
    
    return {
        "models": model_items,
        "total": len(model_items),
        "current_version": current_version,
    }


@router.post("/bulk-submit")
async def bulk_submit(
    request: Request,
    db: Session = Depends(get_db),
    auth: Tuple[UserAPIKey, User] = Depends(require_api_key),
):
    """Submit benchmark results directly, bypassing moderation.
    
    This endpoint is restricted to admin users and is designed for the
    bulk benchmark tester to auto-publish results after testing all models.
    
    Creates TestRun + Result records directly (no CommunitySubmission,
    no payment, no moderation queue). Results get trust_tier="automated".
    """
    api_key_record, user = auth
    
    # Permission gate: require admin only
    if not has_permission(user, "can_admin"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Requires admin access for bulk submission."
        )
    
    # Parse request body
    body = await request.json()
    export_data = body.get("export_data")
    
    if not export_data:
        raise HTTPException(
            status_code=400,
            detail="Missing required field: export_data"
        )
    
    # Validate export schema (reuse from submissions endpoint)
    from app.api.v1.endpoints.submissions import validate_export_schema
    
    validation_errors = validate_export_schema(export_data)
    if validation_errors:
        return {
            "status": "rejected",
            "validation_errors": validation_errors,
            "message": "Export validation failed"
        }
    
    # Extract model and version information
    test_run_data = export_data.get("test_run", {})
    model_id_str = test_run_data.get("model", "Unknown")
    model_name = model_id_str  # Use model_id as display name
    version = test_run_data.get("benchmark_version", "1.0")
    
    # Use SubmissionProcessorService to create TestRun + Results
    from app.services.submission_processor import SubmissionProcessorService
    
    processor = SubmissionProcessorService(db)
    
    try:
        # Get or create the Model record
        model = processor.get_or_create_model(model_id_str, model_name)
        
        # Get the QuestionSet
        question_set = processor.get_question_set(version)
        if not question_set:
            return {
                "status": "error",
                "message": f"No question set found for version {version}"
            }
        
        # Get or create methodology version
        methodology_version = processor.get_or_create_methodology_version(question_set)
        
        # Parse completion time
        completed_at = datetime.utcnow()
        if test_run_data.get("completed_at"):
            try:
                completed_at = datetime.fromisoformat(
                    test_run_data["completed_at"].replace("Z", "+00:00")
                )
            except Exception:
                pass
        
        # Create the TestRun directly (bypassing CommunitySubmission)
        test_run = TestRun(
            user_id=user.id,
            model_id=model.id,
            question_set_id=question_set.id,
            methodology_version_id=methodology_version.id,
            status="completed",
            trust_tier="automated",  # Distinguishes bulk tester runs
            completed_at=completed_at,
            started_at=completed_at,
        )
        db.add(test_run)
        db.flush()
        
        # Build lookup for question matching
        tier_cat_lookup = processor.build_tier_category_lookup(question_set.id)
        
        # Create Result records
        from app.db.models.result import Result
        
        responses = export_data.get("responses", [])
        results_created = 0
        used_question_ids: set = set()
        
        for response_data in responses:
            question = processor.find_question(
                response_data,
                question_set.id,
                tier_cat_lookup,
                used_question_ids
            )
            
            if not question:
                continue
            
            used_question_ids.add(question.id)
            
            result = Result(
                test_run_id=test_run.id,
                question_id=question.id,
                response=response_data.get("response", ""),
                verdict=response_data.get("verdict", "UNKNOWN"),
                reasoning=response_data.get("judge_reasoning", ""),
                thought_process=response_data.get("thought_process"),
            )
            db.add(result)
            results_created += 1
        
        db.commit()
        
        # Extract scores
        summary = export_data.get("summary", {})
        
        logger.info(
            f"Bulk submit: model={model_id_str}, version={version}, "
            f"results={results_created}, score={summary.get('score', 0)}, "
            f"user={user.email}"
        )
        
        return {
            "status": "published",
            "test_run_id": str(test_run.id),
            "model_id": model_id_str,
            "results_created": results_created,
            "score": summary.get("score", 0),
            "message": f"Results published directly for {model_id_str} ({results_created} results)"
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Bulk submit failed for {model_id_str}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process submission: {str(e)}"
        )