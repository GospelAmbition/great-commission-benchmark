"""Public API endpoints"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Query, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from uuid import UUID
import logging

from app.core.auth import get_db
from app.core.cache import cache, make_cache_key, CACHE_TTL
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.result import Result
from app.db.models.question import Question
from app.services.scoring import ScoringService
from app.services.openrouter import OpenRouterClient
from app.schemas.public import (
    LeaderboardResponse,
    LeaderboardEntry,
    ModelSummary,
    TestRunSummary,
    Scores,
    VerdictDistribution,
    ModelsListResponse,
    ModelListItem,
    VersionsResponse,
    VersionInfo,
    StatsResponse,
    ComparisonResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Helper Functions
# =============================================================================

def _get_model_detail_data(db: Session, model: Model) -> dict:
    """
    Shared helper to get model detail data including scores, test history,
    and category breakdown. Used by both UUID and model_id lookup endpoints.
    """
    # Get best (most recent completed) test result
    best_test = db.query(TestRun).filter(
        TestRun.model_id == model.id,
        TestRun.status == "completed"
    ).order_by(TestRun.completed_at.desc()).first()
    
    best_result = None
    if best_test:
        scores = ScoringService.calculate_scores(db, str(best_test.id))
        best_result = {
            "test_run_id": str(best_test.id),
            "scores": scores,
            "trust_tier": best_test.trust_tier,
            "completed_at": best_test.completed_at.isoformat() if best_test.completed_at else None,
            "benchmark_version": best_test.question_set.semantic_version
        }
    
    # Get test history (last 10 completed tests)
    test_history = []
    tests = db.query(TestRun).filter(
        TestRun.model_id == model.id,
        TestRun.status == "completed"
    ).order_by(TestRun.completed_at.desc()).limit(10).all()
    
    for test in tests:
        scores = ScoringService.calculate_scores(db, str(test.id))
        test_history.append({
            "test_run_id": str(test.id),
            "overall_score": scores["overall"],
            "benchmark_version": test.question_set.semantic_version,
            "completed_at": test.completed_at.isoformat() if test.completed_at else None,
            "trust_tier": test.trust_tier
        })
    
    # Calculate category breakdown from best test
    category_breakdown = {}
    category_scores = {}
    pass_verdicts = {"ACCEPTED"}
    
    if best_test:
        results = db.query(Result).filter(Result.test_run_id == best_test.id).all()
        for result in results:
            cat = result.question.category
            if cat not in category_breakdown:
                category_breakdown[cat] = {"total": 0, "passed": 0}
            category_breakdown[cat]["total"] += 1
            if result.verdict in pass_verdicts:
                category_breakdown[cat]["passed"] += 1
        
        # Calculate percentage scores per category
        for cat, data in category_breakdown.items():
            category_scores[cat] = round((data["passed"] / data["total"]) * 100, 1) if data["total"] > 0 else 0
            # Also add detailed score using ScoringService
            cat_results = [r for r in results if r.question.category == cat]
            category_breakdown[cat]["score"] = ScoringService.calculate_category_score(cat_results, cat)
    
    return {
        "best_test": best_test,
        "best_result": best_result,
        "test_history": test_history,
        "category_breakdown": category_breakdown,
        "category_scores": category_scores
    }


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    version: str = Query("current", description="Semantic version or 'current'"),
    category: Optional[str] = Query(None),
    tier: Optional[int] = Query(None),
    provider: Optional[str] = Query(None),
    trust_tier: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("score", regex="^(score|date|tier1|tier2|tier3)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """Get public leaderboard"""
    # Get question set version
    if version == "current":
        question_set = db.query(QuestionSet).filter(
            QuestionSet.status == "active"
        ).order_by(QuestionSet.created_at.desc()).first()
    else:
        question_set = db.query(QuestionSet).filter(
            QuestionSet.semantic_version == version
        ).first()
    
    # Return empty leaderboard if no question set exists
    if not question_set:
        return LeaderboardResponse(
            semantic_version="1.0.0",
            marketing_version="1.0",
            filters={
                "category": category,
                "tier": str(tier) if tier else None,
                "provider": provider,
                "trust_tier": trust_tier
            },
            total_models=0,
            entries=[],
            pagination={
                "limit": limit,
                "offset": offset,
                "total": 0,
                "has_more": False
            }
        )
    
    # Build query for completed test runs
    query = db.query(TestRun).filter(
        TestRun.status == "completed",
        TestRun.question_set_id == question_set.id
    )
    
    # Apply filters
    if provider:
        query = query.join(Model).filter(Model.provider == provider)
    
    if trust_tier:
        query = query.filter(TestRun.trust_tier == trust_tier)
    
    # Get test runs (ordered by completed_at desc so most recent is first)
    test_runs = query.order_by(TestRun.completed_at.desc()).all()
    
    # Deduplicate: keep only the most recent test per model
    seen_models = set()
    unique_test_runs = []
    for test_run in test_runs:
        if test_run.model_id not in seen_models:
            seen_models.add(test_run.model_id)
            unique_test_runs.append(test_run)
    test_runs = unique_test_runs
    
    # Calculate scores and build entries
    entries = []
    for idx, test_run in enumerate(test_runs[offset:offset+limit]):
        # Calculate scores
        scores_data = ScoringService.calculate_scores(db, str(test_run.id))
        
        # Filter by category/tier if specified
        if category or tier:
            results = db.query(Result).filter(Result.test_run_id == test_run.id).all()
            if category:
                results = [r for r in results if r.question.category == category]
            if tier:
                results = [r for r in results if r.question.tier == tier]
            
            if not results:
                continue  # Skip if no matching results
        
        # Build entry
        entry = LeaderboardEntry(
            rank=offset + idx + 1,
            model=ModelSummary(
                id=test_run.model.id,
                name=test_run.model.name,
                provider=test_run.model.provider,
                model_id=test_run.model.model_id
            ),
            test_run=TestRunSummary(
                id=test_run.id,
                trust_tier=test_run.trust_tier,
                completed_at=test_run.completed_at,
                question_set_version=question_set.semantic_version
            ),
            scores=Scores(
                overall=scores_data["overall"],
                tier1=scores_data["tier1"],
                tier2=scores_data["tier2"],
                tier3=scores_data["tier3"]
            ),
            category_scores=scores_data["category_scores"],
            verdict_distribution=VerdictDistribution(**scores_data["verdict_distribution"]),
            total_questions=scores_data["total_questions"],
            metadata={
                "submission_date": test_run.completed_at.isoformat() if test_run.completed_at else "",
                "methodology_version": question_set.semantic_version
            }
        )
        entries.append(entry)
    
    # Sort entries
    reverse_order = (order == "desc")
    if sort == "score":
        entries.sort(key=lambda e: e.scores.overall, reverse=reverse_order)
    elif sort == "date":
        entries.sort(key=lambda e: e.test_run.completed_at or datetime.min, reverse=reverse_order)
    elif sort == "tier1":
        entries.sort(key=lambda e: e.scores.tier1, reverse=reverse_order)
    elif sort == "tier2":
        entries.sort(key=lambda e: e.scores.tier2, reverse=reverse_order)
    elif sort == "tier3":
        entries.sort(key=lambda e: e.scores.tier3, reverse=reverse_order)
    
    # Update ranks after sorting
    for idx, entry in enumerate(entries):
        entry.rank = offset + idx + 1
    
    return LeaderboardResponse(
        semantic_version=question_set.semantic_version,
        marketing_version=question_set.marketing_version,
        filters={
            "category": category,
            "tier": str(tier) if tier else None,
            "provider": provider,
            "trust_tier": trust_tier
        },
        total_models=len(test_runs),
        entries=entries,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": len(test_runs),
            "has_more": (offset + limit) < len(test_runs)
        }
    )


@router.get("/models", response_model=ModelsListResponse)
async def list_models(
    provider: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all tested models"""
    query = db.query(Model).filter(Model.is_active == True)
    
    if provider:
        query = query.filter(Model.provider == provider)
    
    if search:
        query = query.filter(Model.name.ilike(f"%{search}%"))
    
    models = query.order_by(Model.created_at.desc()).offset(offset).limit(limit).all()
    
    # Build response with stats
    model_items = []
    for model in models:
        # Get latest test run
        latest_test = db.query(TestRun).filter(
            TestRun.model_id == model.id,
            TestRun.status == "completed"
        ).order_by(TestRun.completed_at.desc()).first()
        
        # Get test count
        test_count = db.query(TestRun).filter(TestRun.model_id == model.id).count()
        
        # Get first and last tested dates
        first_test = db.query(TestRun).filter(TestRun.model_id == model.id).order_by(TestRun.created_at.asc()).first()
        last_test = latest_test
        
        latest_score = None
        if latest_test:
            scores = ScoringService.calculate_scores(db, str(latest_test.id))
            latest_score = scores["overall"]
        
        model_items.append(ModelListItem(
            id=model.id,
            name=model.name,
            provider=model.provider,
            model_id=model.model_id,
            latest_score=latest_score,
            test_count=test_count,
            first_tested=first_test.created_at if first_test else None,
            last_tested=last_test.completed_at if last_test else None
        ))
    
    total = query.count()
    
    return ModelsListResponse(
        models=model_items,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (offset + limit) < total
        }
    )


@router.get("/available-models")
async def list_available_models(
    response: Response,
    search: Optional[str] = Query(None, description="Search filter for model name or ID"),
    limit: int = Query(100, ge=1, le=500),
):
    """
    List available models from OpenRouter API.
    This returns all models that can be tested, not just ones already in our database.
    """
    # Check cache first
    cache_key = make_cache_key("openrouter_models")
    cached_result = await cache.get(cache_key)
    
    if cached_result and not search:
        response.headers["X-Cache"] = "HIT"
        models_data = cached_result
    else:
        response.headers["X-Cache"] = "MISS"
        openrouter = OpenRouterClient()
        try:
            models_data = await openrouter.list_models()
        except Exception as e:
            logger.error(f"Failed to fetch models from OpenRouter: {e}")
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch models from OpenRouter. Please try again later."
            )
        finally:
            await openrouter.close()
        
        # Cache the raw models data for 5 minutes
        if not search:
            await cache.set(cache_key, models_data, 300)
    
    # Filter and transform the models
    items = []
    for model in models_data:
        model_id = model.get("id", "")
        model_name = model.get("name", model_id)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            if search_lower not in model_id.lower() and search_lower not in model_name.lower():
                continue
        
        # Extract provider from model ID (e.g., "anthropic/claude-3" -> "anthropic")
        provider = model_id.split("/")[0] if "/" in model_id else "unknown"
        
        # Get pricing info
        pricing = model.get("pricing", {})
        prompt_cost = float(pricing.get("prompt", 0)) if pricing.get("prompt") else 0
        completion_cost = float(pricing.get("completion", 0)) if pricing.get("completion") else 0
        
        items.append({
            "id": model_id,
            "model_id": model_id,
            "name": model_name,
            "provider": provider,
            "context_length": model.get("context_length", 0),
            "pricing": {
                "prompt": prompt_cost,
                "completion": completion_cost
            },
            # Estimate cost per test based on average token usage
            # Rough estimate: ~50k input tokens, ~20k output tokens per full test
            "estimated_cost_per_test": round((prompt_cost * 50000 + completion_cost * 20000) / 1000000, 2)
        })
    
    # Sort by name
    items.sort(key=lambda x: x["name"])
    
    # Apply limit
    items = items[:limit]
    
    return {
        "items": items,
        "total": len(items)
    }


@router.get("/models/by-id")
async def get_model_by_model_id(
    model_id: str = Query(..., description="Model identifier string (e.g., 'qwen/qwen3-coder-30b')"),
    db: Session = Depends(get_db)
):
    """Get detailed model information by model_id string"""
    model = db.query(Model).filter(Model.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Use shared helper to get model detail data
    data = _get_model_detail_data(db, model)
    best_result = data["best_result"]
    test_history = data["test_history"]
    category_scores = data["category_scores"]
    
    return {
        "id": str(model.id),
        "model_id": model.model_id,
        "model_name": model.name,
        "name": model.name,
        "provider": model.provider,
        "overall_score": best_result["scores"]["overall"] if best_result else None,
        "score": best_result["scores"]["overall"] if best_result else None,
        "tier1_score": best_result["scores"]["tier1"] if best_result else None,
        "tier2_score": best_result["scores"]["tier2"] if best_result else None,
        "tier3_score": best_result["scores"]["tier3"] if best_result else None,
        "trust_tier": best_result["trust_tier"] if best_result else None,
        "test_count": len(test_history),
        "category_scores": category_scores,
        "version_history": [
            {
                "version": t["benchmark_version"],
                "score": t["overall_score"],
                "date": t["completed_at"]
            }
            for t in test_history
        ]
    }


@router.get("/models/{model_id}")
async def get_model_detail(
    model_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed model information by UUID"""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Use shared helper to get model detail data
    data = _get_model_detail_data(db, model)
    
    # Calculate leaderboard rank (simplified)
    leaderboard_rank = None
    total_models_tested = db.query(Model).filter(Model.is_active == True).count()
    
    return {
        "model": {
            "id": str(model.id),
            "name": model.name,
            "provider": model.provider,
            "model_id": model.model_id
        },
        "best_result": data["best_result"],
        "test_history": data["test_history"],
        "category_breakdown": data["category_breakdown"],
        "leaderboard_rank": leaderboard_rank,
        "total_models_tested": total_models_tested
    }


@router.get("/versions", response_model=VersionsResponse)
async def list_versions(response: Response, db: Session = Depends(get_db)):
    """List all published benchmark versions (excludes drafts)"""
    # Check cache first
    cache_key = make_cache_key("versions")
    cached_result = await cache.get(cache_key)
    if cached_result:
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    response.headers["X-Cache"] = "MISS"
    
    # Only return published versions (active or archived), not drafts
    question_sets = db.query(QuestionSet).filter(
        QuestionSet.status.in_(["active", "archived"])
    ).order_by(QuestionSet.created_at.desc()).all()
    
    versions = []
    current_version = None
    
    for qs in question_sets:
        # Count questions per tier
        questions = db.query(Question).filter(Question.question_set_id == qs.id).all()
        tier_dist = {
            "tier1": sum(1 for q in questions if q.tier == 1),
            "tier2": sum(1 for q in questions if q.tier == 2),
            "tier3": sum(1 for q in questions if q.tier == 3)
        }
        
        # Count models tested
        models_tested = db.query(TestRun).filter(
            TestRun.question_set_id == qs.id,
            TestRun.status == "completed"
        ).distinct(TestRun.model_id).count()
        
        version_info = VersionInfo(
            semantic_version=qs.semantic_version,
            marketing_version=qs.marketing_version,
            status="current" if qs.status == "active" else qs.status,
            release_date=qs.created_at.date().isoformat() if qs.created_at else None,
            question_count=len(questions),
            tier_distribution=tier_dist,
            scoring_weights={
                "tier1": 0.70,
                "tier2": 0.20,
                "tier3": 0.10
            },
            models_tested=models_tested
        )
        versions.append(version_info)
        
        if qs.status == "active" and not current_version:
            current_version = qs.semantic_version
    
    result = VersionsResponse(
        versions=versions,
        current_version=current_version or versions[0].semantic_version if versions else "1.0"
    )
    
    # Cache the result
    await cache.set(cache_key, result, CACHE_TTL["versions"])
    
    return result


@router.get("/stats", response_model=StatsResponse)
async def get_stats(response: Response, db: Session = Depends(get_db)):
    """Get platform statistics"""
    from datetime import datetime
    
    # Check cache first
    cache_key = make_cache_key("public_stats")
    cached_result = await cache.get(cache_key)
    if cached_result:
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    response.headers["X-Cache"] = "MISS"
    
    # Get current version
    current_qs = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    current_version = current_qs.semantic_version if current_qs else "1.0"
    
    # Count models tested
    total_models_tested = db.query(Model).filter(Model.is_active == True).count()
    
    # Count test runs
    total_test_runs = db.query(TestRun).filter(TestRun.status == "completed").count()
    
    # Calculate top and average scores
    completed_tests = db.query(TestRun).filter(TestRun.status == "completed").all()
    scores = []
    for test in completed_tests:
        try:
            test_scores = ScoringService.calculate_scores(db, str(test.id))
            scores.append(test_scores["overall"])
        except:
            pass
    
    top_score = max(scores) if scores else 0.0
    average_score = sum(scores) / len(scores) if scores else 0.0
    
    # Count providers
    providers_represented = db.query(Model.provider).distinct().count()
    
    result = StatsResponse(
        total_models_tested=total_models_tested,
        total_test_runs=total_test_runs,
        current_benchmark_version=current_version,
        top_score=round(top_score, 2),
        average_score=round(average_score, 2),
        providers_represented=providers_represented,
        last_updated=datetime.utcnow()
    )
    
    # Cache the result
    await cache.set(cache_key, result, CACHE_TTL["public_stats"])
    
    return result


@router.get("/leaderboard/compare")
async def compare_models(
    models: List[UUID] = Query(..., description="Model IDs to compare (max 5)"),
    version: str = Query("current"),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Compare multiple models"""
    if len(models) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 models can be compared")
    
    # Get version
    if version == "current":
        question_set = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    else:
        question_set = db.query(QuestionSet).filter(QuestionSet.semantic_version == version).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Version not found")
    
    comparison_data = {
        "semantic_version": question_set.semantic_version,
        "marketing_version": question_set.marketing_version,
        "models": [],
        "comparison": {}
    }
    
    model_scores = []
    for model_id in models:
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            continue
        
        # Get latest test run for this model and version
        test_run = db.query(TestRun).filter(
            TestRun.model_id == model_id,
            TestRun.question_set_id == question_set.id,
            TestRun.status == "completed"
        ).order_by(TestRun.completed_at.desc()).first()
        
        if not test_run:
            continue
        
        scores = ScoringService.calculate_scores(db, str(test_run.id))
        
        model_data = {
            "model": {
                "id": str(model.id),
                "name": model.name,
                "provider": model.provider
            },
            "test_run_id": str(test_run.id),
            "scores": scores,
            "verdict_distribution": scores["verdict_distribution"]
        }
        comparison_data["models"].append(model_data)
        model_scores.append(scores)
    
    # Calculate deltas if we have at least 2 models
    if len(model_scores) >= 2:
        base_scores = model_scores[0]
        comparison_data["comparison"] = {
            "score_delta": {
                "overall": model_scores[1]["overall"] - base_scores["overall"],
                "tier1": model_scores[1]["tier1"] - base_scores["tier1"],
                "tier2": model_scores[1]["tier2"] - base_scores["tier2"],
                "tier3": model_scores[1]["tier3"] - base_scores["tier3"]
            }
        }
    
    return comparison_data