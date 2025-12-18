"""Runner API endpoints (for CLI)"""
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.auth import get_db
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.db.models.methodology_version import MethodologyVersion
from app.core.rate_limit import RateLimitDependency

router = APIRouter()


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Verify API key for runner endpoints"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Basic validation - must be at least 32 characters
    if len(x_api_key) < 32:
        raise HTTPException(status_code=401, detail="Invalid API key format")
    
    # TODO: Validate against database for production
    # For now, accept any key that meets format requirements
    return x_api_key


# Rate limiter for runner endpoints: 50 requests per hour
runner_rate_limit = RateLimitDependency("runner")


@router.get("/versions")
async def get_runner_versions(
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get available benchmark versions for CLI"""
    question_sets = db.query(QuestionSet).filter(
        QuestionSet.status.in_(["active", "archived"])
    ).order_by(QuestionSet.created_at.desc()).all()
    
    versions = []
    for qs in question_sets:
        question_count = db.query(Question).filter(Question.question_set_id == qs.id).count()
        
        versions.append({
            "semantic_version": qs.semantic_version,
            "marketing_version": qs.marketing_version,
            "status": "current" if qs.status == "active" else qs.status,
            "question_count": question_count,
            "release_date": qs.created_at.isoformat() if qs.created_at else None
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
    api_key: str = Depends(verify_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get full question set for CLI"""
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
        }
    }


@router.get("/judge-prompts")
async def get_judge_prompts(
    request: Request,
    version: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
    _rate_limit: bool = Depends(runner_rate_limit)
):
    """Get judge prompts for each tier"""
    # Get question set
    if version:
        question_set = db.query(QuestionSet).filter(QuestionSet.semantic_version == version).first()
    else:
        question_set = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Get methodology version
    methodology_version = db.query(MethodologyVersion).filter(
        MethodologyVersion.question_set_id == question_set.id
    ).order_by(MethodologyVersion.active_from.desc()).first()
    
    if not methodology_version:
        raise HTTPException(status_code=404, detail="Methodology version not found")
    
    # TODO: Split judge prompt by tier (currently stored as single prompt)
    # For now, return the single prompt for all tiers
    return {
        "version": question_set.semantic_version,
        "prompts": {
            "tier1": methodology_version.judge_prompt,  # TODO: Split by tier
            "tier2": methodology_version.judge_prompt,
            "tier3": methodology_version.judge_prompt
        }
    }