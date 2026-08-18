"""Public API endpoints"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Query, Depends, HTTPException, Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from uuid import UUID
import logging

from app.core.auth import get_db, get_db_sync
from app.core.db_errors import raise_if_db_unavailable
from app.core.cache import cache, make_cache_key, CACHE_TTL, CACHE_STALE_TTL
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.result import Result
from app.db.models.question import Question
from app.db.models.blog_post import BlogPost, blog_post_models
from app.services.leaderboard_queries import get_latest_completed_test_runs
from app.services.model_snapshots import get_model_snapshot
from app.services.openrouter import OpenRouterClient
from app.services.payment import PaymentService
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
    ComparisonResponse,
    StripePublishableKeyResponse
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
    
    Always uses the most recent test for primary scores. AI models change
    frequently, so the most recent test reflects the current state of the
    model's compliance. Test history is preserved for trend analysis.
    """
    # Get most recent completed test with pre-computed scores (exclude null)
    best_test = db.query(TestRun).options(
        joinedload(TestRun.question_set)
    ).filter(
        TestRun.model_id == model.id,
        TestRun.status == "completed",
        TestRun.overall_score.isnot(None),
        or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
    ).order_by(TestRun.completed_at.desc()).first()
    
    best_result = None
    if best_test:
        best_result = {
            "test_run_id": str(best_test.id),
            "scores": {
                "overall": float(best_test.overall_score),
                "tier1": float(best_test.tier1_score or 0),
                "tier2": float(best_test.tier2_score or 0),
                "tier3": float(best_test.tier3_score or 0),
                "category_scores": best_test.category_scores or {},
                "verdict_distribution": best_test.verdict_distribution or {
                    "ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "ERROR": 0
                },
                "total_questions": best_test.total_questions or 0,
            },
            "trust_tier": best_test.trust_tier,
            "completed_at": best_test.completed_at.isoformat() if best_test.completed_at else None,
            "benchmark_version": best_test.question_set.semantic_version
        }
    
    # Get test history (last 10 completed tests with scores)
    test_history = []
    tests = db.query(TestRun).options(
        joinedload(TestRun.question_set)
    ).filter(
        TestRun.model_id == model.id,
        TestRun.status == "completed",
        TestRun.overall_score.isnot(None),
        or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
    ).order_by(TestRun.completed_at.desc()).limit(10).all()
    
    for test in tests:
        test_history.append({
            "test_run_id": str(test.id),
            "overall_score": float(test.overall_score),
            "tier1_score": float(test.tier1_score or 0),
            "tier2_score": float(test.tier2_score or 0),
            "tier3_score": float(test.tier3_score or 0),
            "benchmark_version": test.question_set.semantic_version,
            "completed_at": test.completed_at.isoformat() if test.completed_at else None,
            "trust_tier": test.trust_tier
        })
    
    # Category breakdown from stored category_scores (total/passed for schema; score is the stored value)
    category_breakdown = {}
    category_scores = best_test.category_scores or {} if best_test else {}
    
    if best_test and best_test.category_scores:
        for cat, score in best_test.category_scores.items():
            category_breakdown[cat] = {
                "total": 100,
                "passed": int(round(score)) if score is not None else 0,
                "score": float(score) if score is not None else 0.0,
            }
    
    return {
        "best_test": best_test,
        "best_result": best_result,
        "test_history": test_history,
        "category_breakdown": category_breakdown,
        "category_scores": category_scores,
        "test_count": len(test_history)
    }


def _get_related_articles(db: Session, model: Model, limit: int = 5) -> list:
    """Get published blog posts linked to a specific model."""
    posts = (
        db.query(BlogPost)
        .join(blog_post_models, blog_post_models.c.post_id == BlogPost.id)
        .filter(
            blog_post_models.c.model_id == model.id,
            BlogPost.status == "published",
        )
        .order_by(BlogPost.published_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "excerpt": p.excerpt,
            "featured_image_url": p.featured_image_url,
            "published_at": p.published_at.isoformat() if p.published_at else None,
        }
        for p in posts
    ]


def _get_provider_articles(db: Session, provider: str, limit: int = 5) -> list:
    """Get published blog posts linked to any model from a given provider."""
    posts = (
        db.query(BlogPost)
        .join(blog_post_models, blog_post_models.c.post_id == BlogPost.id)
        .join(Model, blog_post_models.c.model_id == Model.id)
        .filter(
            Model.provider == provider,
            BlogPost.status == "published",
        )
        .distinct()
        .order_by(BlogPost.published_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "slug": p.slug,
            "excerpt": p.excerpt,
            "featured_image_url": p.featured_image_url,
            "published_at": p.published_at.isoformat() if p.published_at else None,
        }
        for p in posts
    ]


@router.get("/filter-options")
async def get_filter_options(
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Get available filter options for the leaderboard.
    Returns distinct providers and categories from models that have completed test runs.
    """
    # Check cache first
    cache_key = make_cache_key("filter_options")
    cached_result = await cache.get(cache_key)
    if cached_result:
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    response.headers["X-Cache"] = "MISS"
    
    # Get distinct providers from models that have completed test runs
    providers = db.query(Model.provider).join(
        TestRun, TestRun.model_id == Model.id
    ).filter(
        TestRun.status == "completed",
        Model.is_active == True
    ).distinct().all()
    providers = sorted([p[0] for p in providers if p[0]])
    
    # Get distinct categories from questions in the active question set
    active_qs = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    categories = []
    if active_qs:
        cat_results = db.query(Question.category).filter(
            Question.question_set_id == active_qs.id
        ).distinct().all()
        categories = sorted([c[0] for c in cat_results if c[0]])
    
    # Get distinct trust tiers from completed test runs
    trust_tiers = db.query(TestRun.trust_tier).filter(
        TestRun.status == "completed",
        TestRun.trust_tier.isnot(None)
    ).distinct().all()
    trust_tiers = sorted([t[0] for t in trust_tiers if t[0]])
    
    # Get distinct versions from publicly visible question sets (active or archived with is_publicly_visible=True)
    versions = db.query(QuestionSet.semantic_version).filter(
        or_(
            QuestionSet.status == "active",
            (QuestionSet.status == "archived") & (QuestionSet.is_publicly_visible == True)
        )
    ).distinct().all()
    versions = sorted([v[0] for v in versions if v[0]], reverse=True)  # Most recent first
    
    result = {
        "providers": providers,
        "categories": categories,
        "trust_tiers": trust_tiers,
        "tiers": [
            {"value": "tier1", "label": "Tier 1 (Task)"},
            {"value": "tier2", "label": "Tier 2 (Doctrine)"},
            {"value": "tier3", "label": "Tier 3 (Worldview)"}
        ],
        "versions": versions
    }
    
    # Cache for 5 minutes
    await cache.set(cache_key, result, 300)
    
    return result


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    response: Response,
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
    """Get public leaderboard with stale-while-revalidate caching.
    
    Displays the most recent test score for each model, reflecting the current
    state of the model's compliance. AI models change frequently, so the most
    recent test is the most relevant indicator.
    
    Returns cached data immediately (even if stale) while refreshing in background.
    This ensures users never wait for cold cache loads.
    """
    # Check cache with stale-while-revalidate support
    cache_params = {
        "version": version, "category": category, "tier": tier,
        "provider": provider, "trust_tier": trust_tier,
        "limit": limit, "offset": offset, "sort": sort, "order": order
    }
    cache_key = make_cache_key("leaderboard", cache_params)
    
    # Get cached value with stale status
    cached_result, is_fresh, should_refresh = await cache.get_with_stale(cache_key)
    
    if cached_result is not None:
        # Return cached data immediately
        if is_fresh:
            response.headers["X-Cache"] = "HIT"
        else:
            response.headers["X-Cache"] = "STALE"
            # Trigger background refresh if data is stale
            if should_refresh:
                import asyncio
                asyncio.create_task(_refresh_leaderboard_cache(cache_key, cache_params))
        return cached_result
    
    response.headers["X-Cache"] = "MISS"
    
    try:
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
        
        # Query most recent completed test run per model
        entries = []
        unique_test_runs = get_latest_completed_test_runs(
            db,
            question_set_id=question_set.id,
            provider=provider,
            trust_tier=trust_tier,
        )
        
        # Precompute tier categories for tier filter (if needed)
        tier_categories = set()
        if tier:
            tier_cats = db.query(Question.category).filter(
                Question.question_set_id == question_set.id,
                Question.tier == tier
            ).distinct().all()
            tier_categories = {c[0] for c in tier_cats if c[0]}
        
        # Build entries from stored scores only (no recalculation)
        for test_run in unique_test_runs:
            cat_scores = test_run.category_scores or {}
            
            # Filter by category/tier if specified
            if category and category not in cat_scores:
                continue
            if tier and not (tier_categories & set(cat_scores.keys())):
                continue
            
            scores_data = {
                "overall": float(test_run.overall_score),
                "tier1": float(test_run.tier1_score or 0),
                "tier2": float(test_run.tier2_score or 0),
                "tier3": float(test_run.tier3_score or 0),
                "category_scores": cat_scores,
                "verdict_distribution": test_run.verdict_distribution or {
                    "ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "ERROR": 0
                },
                "total_questions": test_run.total_questions or 0,
            }
            
            entry = LeaderboardEntry(
                rank=0,
                model=ModelSummary(
                    id=test_run.model.id,
                    name=test_run.model.name,
                    provider=test_run.model.provider,
                    model_id=test_run.model.model_id,
                    description=test_run.model.description,
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
                },
                test_count=1,
                score_range=None
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
        
        # Store total before pagination
        total_models = len(entries)
        
        # Apply pagination after sorting
        if limit is None:
            pagination_limit = total_models
            paginated_entries = entries
            effective_offset = 0
        else:
            pagination_limit = limit
            paginated_entries = entries[offset:offset + limit]
            effective_offset = offset
        
        # Update ranks after sorting and pagination
        for idx, entry in enumerate(paginated_entries):
            entry.rank = effective_offset + idx + 1
        
        result = LeaderboardResponse(
            semantic_version=question_set.semantic_version,
            marketing_version=question_set.marketing_version,
            filters={
                "category": category,
                "tier": str(tier) if tier else None,
                "provider": provider,
                "trust_tier": trust_tier
            },
            total_models=total_models,
            entries=paginated_entries,
            pagination={
                "limit": pagination_limit,
                "offset": effective_offset,
                "total": total_models,
                "has_more": False if limit is None else (offset + limit) < total_models
            }
        )
        
        # Cache with stale-while-revalidate TTLs
        await cache.set(
            cache_key, 
            result, 
            ttl_seconds=CACHE_TTL["leaderboard"],
            stale_ttl_seconds=CACHE_STALE_TTL["leaderboard"]
        )
        
        return result
    except Exception as exc:
        raise_if_db_unavailable(exc)


async def _refresh_leaderboard_cache(cache_key: str, params: dict):
    """Background task to refresh a stale leaderboard cache entry.
    
    This is called when a user hits a stale cache entry.
    The user gets immediate response with stale data while this refreshes.
    """
    db = None
    try:
        logger.info(f"Background refresh started for cache key: {cache_key}")
        await cache.mark_refreshing(cache_key)
        
        db = get_db_sync()
        from app.services.cache_warmer import _generate_leaderboard_data
        
        result = await _generate_leaderboard_data(
            db,
            version=params.get("version", "current"),
            category=params.get("category"),
            tier=params.get("tier"),
            provider=params.get("provider"),
            trust_tier=params.get("trust_tier"),
            limit=params.get("limit", 50),
            offset=params.get("offset", 0),
            sort=params.get("sort", "score"),
            order=params.get("order", "desc")
        )
        
        await cache.set(
            cache_key,
            result,
            ttl_seconds=CACHE_TTL["leaderboard"],
            stale_ttl_seconds=CACHE_STALE_TTL["leaderboard"]
        )
        
        logger.info(f"Background refresh completed for cache key: {cache_key}")
    except Exception as e:
        logger.error(f"Background refresh failed for {cache_key}: {e}")
    finally:
        if db is not None:
            db.close()
        await cache.unmark_refreshing(cache_key)


@router.get("/models", response_model=ModelsListResponse)
async def list_models(
    provider: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all tested models. Excludes models with no valid completed test (e.g. failed/deleted)."""
    cache_key = make_cache_key("models_list", {
        "provider": provider,
        "search": search,
        "limit": limit,
        "offset": offset,
    })
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached

    # Only models that have at least one valid completed test run
    has_valid_test = db.query(TestRun.model_id).filter(
        TestRun.status == "completed",
        TestRun.overall_score.isnot(None),
        or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
    ).distinct().subquery()
    query = db.query(Model).filter(
        Model.is_active == True,
        Model.id.in_(db.query(has_valid_test.c.model_id))
    )
    if provider:
        query = query.filter(Model.provider == provider)
    if search:
        query = query.filter(Model.name.ilike(f"%{search}%"))
    models = query.order_by(Model.created_at.desc()).offset(offset).limit(limit).all()
    
    # Build response with stats
    model_items = []
    for model in models:
        # Get latest valid test run with pre-computed scores
        latest_test = db.query(TestRun).filter(
            TestRun.model_id == model.id,
            TestRun.status == "completed",
            TestRun.overall_score.isnot(None),
            or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
        ).order_by(TestRun.completed_at.desc()).first()
        
        # Get test count
        test_count = db.query(TestRun).filter(TestRun.model_id == model.id).count()
        
        # Get first and last tested dates
        first_test = db.query(TestRun).filter(TestRun.model_id == model.id).order_by(TestRun.created_at.asc()).first()
        last_test = latest_test
        
        latest_score = float(latest_test.overall_score) if latest_test and latest_test.overall_score is not None else None
        
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
    
    result = ModelsListResponse(
        models=model_items,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (offset + limit) < total
        }
    )
    await cache.set(
        cache_key,
        result,
        ttl_seconds=CACHE_TTL["models_list"],
        stale_ttl_seconds=CACHE_TTL["models_list"],
    )
    return result


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
            "description": model.get("description"),  # Model description from OpenRouter
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
    """Get detailed model information by model_id string. Returns 404 if model has no valid completed test."""
    model = db.query(Model).filter(Model.model_id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Use shared helper to get model detail data
    data = await get_model_snapshot(db, model)
    if not data["best_result"]:
        raise HTTPException(status_code=404, detail="Model has no valid benchmark results")
    best_result = data["best_result"]
    test_history = data["test_history"]
    category_scores = data["category_scores"]
    test_count = data.get("test_count", len(test_history))
    
    # Always use the most recent test for primary scores
    overall_score = best_result["scores"]["overall"] if best_result else None
    tier1_score = best_result["scores"]["tier1"] if best_result else None
    tier2_score = best_result["scores"]["tier2"] if best_result else None
    tier3_score = best_result["scores"]["tier3"] if best_result else None
    
    verdict_distribution = (
        best_result["scores"].get("verdict_distribution") if best_result else None
    ) or {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "ERROR": 0}

    return {
        "id": str(model.id),
        "model_id": model.model_id,
        "model_name": model.name,
        "name": model.name,
        "provider": model.provider,
        "description": model.description,
        "overall_score": overall_score,
        "score": overall_score,
        "tier1_score": tier1_score,
        "tier2_score": tier2_score,
        "tier3_score": tier3_score,
        "verdict_distribution": verdict_distribution,
        "total_questions": (
            best_result["scores"].get("total_questions") if best_result else None
        ) or 0,
        "trust_tier": best_result["trust_tier"] if best_result else None,
        "test_count": test_count,
        "category_scores": category_scores,
        "version_history": [
            {
                "version": t["benchmark_version"],
                "score": t["overall_score"],
                "date": t["completed_at"]
            }
            for t in test_history
        ],
        "test_history": test_history,
        "related_articles": _get_related_articles(db, model),
    }


@router.get("/models/{model_id}")
async def get_model_detail(
    model_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed model information by UUID. Returns 404 if model has no valid completed test."""
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Use shared helper to get model detail data
    data = await get_model_snapshot(db, model)
    if not data["best_result"]:
        raise HTTPException(status_code=404, detail="Model has no valid benchmark results")
    
    # Calculate leaderboard rank (simplified)
    leaderboard_rank = None
    total_models_tested = db.query(Model).filter(Model.is_active == True).count()
    
    return {
        "model": {
            "id": str(model.id),
            "name": model.name,
            "provider": model.provider,
            "model_id": model.model_id,
            "description": model.description
        },
        "best_result": data["best_result"],
        "test_history": data["test_history"],
        "category_breakdown": data["category_breakdown"],
        "leaderboard_rank": leaderboard_rank,
        "total_models_tested": total_models_tested,
        "related_articles": _get_related_articles(db, model),
    }


@router.get("/providers/{provider}/articles")
async def get_provider_articles(
    provider: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get published blog posts linked to models from a given provider."""
    return {"articles": _get_provider_articles(db, provider, limit)}


@router.get("/versions", response_model=VersionsResponse)
async def list_versions(response: Response, db: Session = Depends(get_db)):
    """List all published benchmark versions (excludes drafts and hidden archived versions)"""
    # Check cache first
    cache_key = make_cache_key("versions")
    cached_result = await cache.get(cache_key)
    if cached_result:
        response.headers["X-Cache"] = "HIT"
        return cached_result
    
    response.headers["X-Cache"] = "MISS"
    
    # Only return publicly visible versions:
    # - Active versions (always visible)
    # - Archived versions with is_publicly_visible=True
    question_sets = db.query(QuestionSet).filter(
        or_(
            QuestionSet.status == "active",
            and_(
                QuestionSet.status == "archived",
                QuestionSet.is_publicly_visible == True
            )
        )
    ).order_by(QuestionSet.created_at.desc()).all()
    
    # Defensive check: explicitly filter out any archived versions that are not publicly visible
    # This ensures hidden archived versions are never returned, even if the query somehow includes them
    question_sets = [
        qs for qs in question_sets
        if qs.status == "active" or (qs.status == "archived" and qs.is_publicly_visible is True)
    ]
    
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
    
    try:
        # Get current version
        current_qs = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
        current_version = current_qs.semantic_version if current_qs else "1.0"
        
        # Count models tested - only models with completed test runs (with scores) for current benchmark
        if current_qs:
            total_models_tested = db.query(Model).join(TestRun).filter(
                Model.is_active == True,
                TestRun.question_set_id == current_qs.id,
                TestRun.status == "completed",
                TestRun.overall_score.isnot(None),
            ).distinct().count()
        else:
            total_models_tested = 0
        
        # Count test runs - only for current benchmark (with scores)
        if current_qs:
            total_test_runs = db.query(TestRun).filter(
                TestRun.question_set_id == current_qs.id,
                TestRun.status == "completed",
                TestRun.overall_score.isnot(None),
            ).count()
        else:
            total_test_runs = 0
        
        # Top and average scores from stored values only
        if current_qs:
            top_score_result = db.query(func.max(TestRun.overall_score)).filter(
                TestRun.question_set_id == current_qs.id,
                TestRun.status == "completed",
                TestRun.overall_score.isnot(None),
            ).scalar()
            avg_score_result = db.query(func.avg(TestRun.overall_score)).filter(
                TestRun.question_set_id == current_qs.id,
                TestRun.status == "completed",
                TestRun.overall_score.isnot(None),
            ).scalar()
            top_score = float(top_score_result) if top_score_result is not None else 0.0
            average_score = float(avg_score_result) if avg_score_result is not None else 0.0
        else:
            top_score = 0.0
            average_score = 0.0
        
        # Count providers - only providers with models tested (with scores) in current benchmark
        if current_qs:
            providers_represented = db.query(Model.provider).join(TestRun).filter(
                TestRun.question_set_id == current_qs.id,
                TestRun.status == "completed",
                TestRun.overall_score.isnot(None),
            ).distinct().count()
        else:
            providers_represented = 0
        
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
    except Exception as exc:
        raise_if_db_unavailable(exc)


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

    cache_key = make_cache_key("model_comparison", {
        "models": [str(model_id) for model_id in models],
        "version": version,
        "category": category,
    })
    cached = await cache.get(cache_key)
    if cached is not None:
        return cached
    
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
        if not model or not model.is_active:
            continue
        
        # Get latest test run for this model and version with pre-computed scores
        test_run = db.query(TestRun).options(
            joinedload(TestRun.model),
            joinedload(TestRun.question_set)
        ).filter(
            TestRun.model_id == model_id,
            TestRun.question_set_id == question_set.id,
            TestRun.status == "completed",
            TestRun.overall_score.isnot(None),
            or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
        ).order_by(TestRun.completed_at.desc()).first()
        
        if not test_run:
            continue
        
        scores = {
            "overall": float(test_run.overall_score),
            "tier1": float(test_run.tier1_score or 0),
            "tier2": float(test_run.tier2_score or 0),
            "tier3": float(test_run.tier3_score or 0),
            "category_scores": test_run.category_scores or {},
            "verdict_distribution": test_run.verdict_distribution or {
                "ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "ERROR": 0
            },
        }
        
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
    
    await cache.set(
        cache_key,
        comparison_data,
        ttl_seconds=CACHE_TTL["model_comparison"],
        stale_ttl_seconds=CACHE_STALE_TTL["model_comparison"],
    )
    return comparison_data


@router.get("/leaderboard-page")
async def get_leaderboard_page(
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Combined endpoint that returns both the default leaderboard and filter options
    in a single request. Used by the frontend to load the leaderboard page with
    one round-trip instead of two.

    Returns the complete current leaderboard sorted by score, plus filter options.
    Filter options are returned in the same response so the page can render
    immediately and filter locally without additional leaderboard requests.
    """
    import asyncio

    # Build default leaderboard cache key (matches the frontend default params)
    default_leaderboard_params = {
        "version": "current",
        "category": None,
        "tier": None,
        "provider": None,
        "trust_tier": None,
        "limit": None,
        "offset": 0,
        "sort": "score",
        "order": "desc",
    }
    lb_cache_key = make_cache_key("leaderboard", default_leaderboard_params)
    fo_cache_key = make_cache_key("filter_options")

    # Fetch both from cache concurrently
    lb_cached, lb_fresh, lb_should_refresh = await cache.get_with_stale(lb_cache_key)
    fo_cached = await cache.get(fo_cache_key)

    # Trigger background leaderboard refresh if stale
    if lb_cached is not None and not lb_fresh and lb_should_refresh:
        asyncio.create_task(_refresh_leaderboard_cache(lb_cache_key, default_leaderboard_params))

    # If both are cached, return immediately
    if lb_cached is not None and fo_cached is not None:
        response.headers["X-Cache"] = "HIT" if lb_fresh else "STALE"
        return {"leaderboard": lb_cached, "filter_options": fo_cached}

    try:
        # If leaderboard is missing from cache, compute it (cold start)
        if lb_cached is None:
            response.headers["X-Cache"] = "MISS"
            from app.services.cache_warmer import _generate_leaderboard_data
            lb_cached = await _generate_leaderboard_data(db, **default_leaderboard_params)
            await cache.set(
                lb_cache_key,
                lb_cached,
                ttl_seconds=CACHE_TTL["leaderboard"],
                stale_ttl_seconds=CACHE_STALE_TTL["leaderboard"],
            )

        # If filter options are missing from cache, compute them
        if fo_cached is None:
            providers = db.query(Model.provider).join(
                TestRun, TestRun.model_id == Model.id
            ).filter(
                TestRun.status == "completed",
                Model.is_active == True,
            ).distinct().all()
            providers = sorted([p[0] for p in providers if p[0]])

            active_qs = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
            categories = []
            if active_qs:
                cat_results = db.query(Question.category).filter(
                    Question.question_set_id == active_qs.id
                ).distinct().all()
                categories = sorted([c[0] for c in cat_results if c[0]])

            trust_tiers = db.query(TestRun.trust_tier).filter(
                TestRun.status == "completed",
                TestRun.trust_tier.isnot(None),
            ).distinct().all()
            trust_tiers = sorted([t[0] for t in trust_tiers if t[0]])

            versions = db.query(QuestionSet.semantic_version).filter(
                or_(
                    QuestionSet.status == "active",
                    (QuestionSet.status == "archived") & (QuestionSet.is_publicly_visible == True),
                )
            ).distinct().all()
            versions = sorted([v[0] for v in versions if v[0]], reverse=True)

            fo_cached = {
                "providers": providers,
                "categories": categories,
                "trust_tiers": trust_tiers,
                "tiers": [
                    {"value": "tier1", "label": "Tier 1 (Task)"},
                    {"value": "tier2", "label": "Tier 2 (Doctrine)"},
                    {"value": "tier3", "label": "Tier 3 (Worldview)"},
                ],
                "versions": versions,
            }
            await cache.set(fo_cache_key, fo_cached, 300)

        return {"leaderboard": lb_cached, "filter_options": fo_cached}
    except Exception as exc:
        raise_if_db_unavailable(exc)


@router.get("/category-rankings")
async def get_category_rankings(
    response: Response,
    limit_per_category: int = Query(5, ge=1, le=10, description="Number of top models per category"),
    db: Session = Depends(get_db)
):
    """
    Get top models for all categories in a single request.
    
    This endpoint is optimized for the Category Rankings page, returning
    all 19 categories with their top models in one call instead of 19
    parallel requests.
    
    Uses stale-while-revalidate caching for instant responses.
    
    Returns:
        Dict with categories grouped by tier, each containing top models
        with their scores for that specific category.
    """
    # Check cache with stale-while-revalidate support
    cache_key = make_cache_key("category_rankings", {"limit": limit_per_category})
    cached_result, is_fresh, should_refresh = await cache.get_with_stale(cache_key)
    
    if cached_result is not None:
        if is_fresh:
            response.headers["X-Cache"] = "HIT"
        else:
            response.headers["X-Cache"] = "STALE"
            if should_refresh:
                import asyncio
                asyncio.create_task(_refresh_category_rankings_cache(cache_key, limit_per_category))
        return cached_result
    
    response.headers["X-Cache"] = "MISS"
    
    try:
        # Get active question set
        question_set = db.query(QuestionSet).filter(
            QuestionSet.status == "active"
        ).order_by(QuestionSet.created_at.desc()).first()
        
        if not question_set:
            return {"categories": {}, "total_models": 0}
        
        # Get all distinct categories from the question set
        categories = db.query(Question.category).filter(
            Question.question_set_id == question_set.id
        ).distinct().all()
        category_codes = sorted([c[0] for c in categories if c[0]])
        
        unique_test_runs = get_latest_completed_test_runs(
            db,
            question_set_id=question_set.id,
        )
        
        # Build scores from stored data only
        test_run_scores = {}
        for test_run in unique_test_runs:
            cat_scores = test_run.category_scores or {}
            test_run_scores[test_run.id] = {
                "test_run": test_run,
                "scores": {
                    "category_scores": cat_scores,
                }
            }
        
        # Build category rankings
        categories_data = {}
        for category_code in category_codes:
            # Get top models for this category based on category score
            category_models = []
            for test_run_id, data in test_run_scores.items():
                test_run = data["test_run"]
                scores = data["scores"]
                category_score = scores.get("category_scores", {}).get(category_code)
                
                if category_score is not None:
                    category_models.append({
                        "model_id": test_run.model.model_id,
                        "model_name": test_run.model.name,
                        "provider": test_run.model.provider,
                        "score": round(category_score, 2)
                    })
            
            # Sort by category score descending and take top N
            category_models.sort(key=lambda x: x["score"], reverse=True)
            top_models = category_models[:limit_per_category]
            
            categories_data[category_code] = {
                "models": top_models,
                "total_models": len(category_models)
            }
        
        result = {
            "categories": categories_data,
            "total_models": len(unique_test_runs),
            "benchmark_version": question_set.semantic_version
        }
        
        # Cache with stale-while-revalidate TTLs
        await cache.set(
            cache_key, 
            result, 
            ttl_seconds=CACHE_TTL["category_rankings"],
            stale_ttl_seconds=CACHE_STALE_TTL["category_rankings"]
        )
        
        return result
    except Exception as exc:
        raise_if_db_unavailable(exc)


async def _refresh_category_rankings_cache(cache_key: str, limit_per_category: int):
    """Background task to refresh a stale category rankings cache entry."""
    db = None
    try:
        logger.info(f"Background refresh started for cache key: {cache_key}")
        await cache.mark_refreshing(cache_key)
        
        db = get_db_sync()
        from app.services.cache_warmer import _generate_category_rankings_data
        
        result = await _generate_category_rankings_data(db, limit_per_category)
        
        await cache.set(
            cache_key,
            result,
            ttl_seconds=CACHE_TTL["category_rankings"],
            stale_ttl_seconds=CACHE_STALE_TTL["category_rankings"]
        )
        
        logger.info(f"Background refresh completed for cache key: {cache_key}")
    except Exception as e:
        logger.error(f"Background refresh failed for {cache_key}: {e}")
    finally:
        if db is not None:
            db.close()
        await cache.unmark_refreshing(cache_key)


@router.get("/stripe/publishable-key", response_model=StripePublishableKeyResponse)
async def get_stripe_publishable_key(
    db: Session = Depends(get_db)
):
    """
    Get the Stripe publishable key for frontend use.
    This endpoint is public and safe to expose the publishable key.
    """
    keys = PaymentService.get_stripe_keys(db)
    publishable_key = keys.get("publishable_key")
    
    return StripePublishableKeyResponse(
        publishable_key=publishable_key,
        is_configured=bool(publishable_key)
    )
