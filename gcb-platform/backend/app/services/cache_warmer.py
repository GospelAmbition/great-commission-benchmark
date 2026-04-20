"""
Cache warming service for pre-populating and maintaining cache freshness.

This service ensures that users never experience cold cache loads by:
1. Pre-warming the cache on application startup
2. Running a background task that refreshes cache entries before they expire
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, or_

from app.core.cache import cache, make_cache_key, CACHE_TTL, CACHE_STALE_TTL
from app.core.auth import get_db_sync
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.schemas.public import (
    LeaderboardResponse,
    LeaderboardEntry,
    ModelSummary,
    TestRunSummary,
    Scores,
    VerdictDistribution,
)

logger = logging.getLogger(__name__)

# Background task reference
_background_task: Optional[asyncio.Task] = None

# How often to check for stale cache entries (in seconds)
REFRESH_CHECK_INTERVAL = 300  # 5 minutes


async def warm_leaderboard_cache(db: Session) -> None:
    """
    Pre-populate the leaderboard cache with the default query parameters.
    This is the most common query that users will make.
    """
    logger.info("Warming leaderboard cache...")
    
    try:
        # Default parameters that match the frontend's initial load
        default_params = {
            "version": "current",
            "category": None,
            "tier": None,
            "provider": None,
            "trust_tier": None,
            "limit": 50,
            "offset": 0,
            "sort": "score",
            "order": "desc"
        }
        
        # Generate the leaderboard data
        result = await _generate_leaderboard_data(db, **default_params)
        
        # Store in cache with long stale TTL
        cache_key = make_cache_key("leaderboard", default_params)
        await cache.set(
            cache_key, 
            result, 
            ttl_seconds=CACHE_TTL["leaderboard"],
            stale_ttl_seconds=CACHE_STALE_TTL["leaderboard"]
        )
        
        logger.info(f"Leaderboard cache warmed successfully with {len(result.entries)} entries")
        
    except Exception as e:
        # Log connection errors at info level, other errors at error level
        if "connection" in str(e).lower() or "refused" in str(e).lower():
            logger.info(f"Leaderboard cache warming skipped - database not available")
        else:
            logger.error(f"Failed to warm leaderboard cache: {e}", exc_info=True)


async def warm_category_rankings_cache(db: Session) -> None:
    """Pre-populate the category rankings cache."""
    logger.info("Warming category rankings cache...")
    
    try:
        result = await _generate_category_rankings_data(db, limit_per_category=5)
        
        cache_key = make_cache_key("category_rankings", {"limit": 5})
        await cache.set(
            cache_key,
            result,
            ttl_seconds=CACHE_TTL["category_rankings"],
            stale_ttl_seconds=CACHE_STALE_TTL["category_rankings"]
        )
        
        logger.info(f"Category rankings cache warmed with {len(result.get('categories', {}))} categories")
        
    except Exception as e:
        # Log connection errors at info level, other errors at error level
        if "connection" in str(e).lower() or "refused" in str(e).lower():
            logger.info(f"Category rankings cache warming skipped - database not available")
        else:
            logger.error(f"Failed to warm category rankings cache: {e}", exc_info=True)


async def warm_filter_options_cache(db: Session) -> None:
    """Pre-populate the filter options cache."""
    logger.info("Warming filter options cache...")
    
    try:
        from sqlalchemy import or_
        
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
        
        # Get distinct versions from publicly visible question sets
        versions = db.query(QuestionSet.semantic_version).filter(
            or_(
                QuestionSet.status == "active",
                (QuestionSet.status == "archived") & (QuestionSet.is_publicly_visible == True)
            )
        ).distinct().all()
        versions = sorted([v[0] for v in versions if v[0]], reverse=True)
        
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
        
        cache_key = make_cache_key("filter_options")
        await cache.set(cache_key, result, 300)  # 5 minute TTL
        
        logger.info("Filter options cache warmed successfully")
        
    except Exception as e:
        # Log connection errors at info level, other errors at error level
        if "connection" in str(e).lower() or "refused" in str(e).lower():
            logger.info(f"Filter options cache warming skipped - database not available")
        else:
            logger.error(f"Failed to warm filter options cache: {e}", exc_info=True)


async def _generate_leaderboard_data(
    db: Session,
    version: str = "current",
    category: Optional[str] = None,
    tier: Optional[int] = None,
    provider: Optional[str] = None,
    trust_tier: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "score",
    order: str = "desc"
) -> LeaderboardResponse:
    """Generate leaderboard data using stored scores (no recalculation)."""
    
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
    
    # Build query for completed test runs with pre-computed scores
    # Exclude bogus 0-question runs (e.g. failed/deleted tests that left a 0% record)
    query = db.query(TestRun).options(
        joinedload(TestRun.model),
        joinedload(TestRun.question_set)
    ).join(Model, TestRun.model_id == Model.id).filter(
        TestRun.status == "completed",
        TestRun.question_set_id == question_set.id,
        TestRun.overall_score.isnot(None),
        or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
        Model.is_active == True
    )
    
    if provider:
        query = query.filter(Model.provider == provider)
    if trust_tier:
        query = query.filter(TestRun.trust_tier == trust_tier)
    
    # Get test runs ordered by completed_at desc
    test_runs = query.order_by(TestRun.completed_at.desc()).all()
    
    # Deduplicate: keep only the most recent test per model
    seen_models = set()
    unique_test_runs = []
    for test_run in test_runs:
        if test_run.model_id not in seen_models:
            seen_models.add(test_run.model_id)
            unique_test_runs.append(test_run)
    
    # Precompute tier categories for tier filter (if needed)
    tier_categories = set()
    if tier:
        tier_cats = db.query(Question.category).filter(
            Question.question_set_id == question_set.id,
            Question.tier == tier
        ).distinct().all()
        tier_categories = {c[0] for c in tier_cats if c[0]}
    
    # Build entries from stored scores only
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
    paginated_entries = entries[offset:offset+limit]
    
    # Update ranks after sorting and pagination
    for idx, entry in enumerate(paginated_entries):
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
        total_models=total_models,
        entries=paginated_entries,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": total_models,
            "has_more": (offset + limit) < total_models
        }
    )


async def _generate_category_rankings_data(db: Session, limit_per_category: int = 5) -> dict:
    """Generate category rankings data using stored scores (no recalculation)."""
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
    
    # Get all completed test runs with pre-computed scores for this question set
    # Exclude bogus 0-question runs (e.g. failed/deleted tests)
    test_runs = db.query(TestRun).options(
        joinedload(TestRun.model),
        joinedload(TestRun.question_set)
    ).join(Model, TestRun.model_id == Model.id).filter(
        TestRun.status == "completed",
        TestRun.question_set_id == question_set.id,
        TestRun.overall_score.isnot(None),
        or_(TestRun.total_questions.is_(None), TestRun.total_questions > 0),
        Model.is_active == True
    ).order_by(TestRun.completed_at.desc()).all()
    
    # Deduplicate: keep only the most recent test per model
    seen_models = set()
    unique_test_runs = []
    for test_run in test_runs:
        if test_run.model_id not in seen_models:
            seen_models.add(test_run.model_id)
            unique_test_runs.append(test_run)
    
    total_models_count = len(unique_test_runs)
    
    # Build scores from stored data only
    test_run_scores = {}
    for test_run in unique_test_runs:
        cat_scores = test_run.category_scores or {}
        test_run_scores[test_run.id] = {
            "test_run": test_run,
            "scores": {"category_scores": cat_scores}
        }
    
    # Build category rankings from most recent test per model
    categories_data = {}
    for category_code in category_codes:
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
    
    return {
        "categories": categories_data,
        "total_models": total_models_count,
        "benchmark_version": question_set.semantic_version
    }


async def warm_all_caches() -> None:
    """Warm all critical caches on startup."""
    logger.info("Starting cache warming...")
    start_time = datetime.utcnow()
    
    # Get a database session
    db = None
    try:
        db = get_db_sync()
        # Test database connection first
        db.execute(text("SELECT 1"))
        db.commit()
    except Exception as e:
        # Database not available - log at info level instead of error
        logger.info(f"Database not available for cache warming: {e}")
        if db:
            db.close()
        return
    
    try:
        # Warm caches in order of importance
        await warm_filter_options_cache(db)
        await warm_leaderboard_cache(db)
        await warm_category_rankings_cache(db)
        
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Cache warming completed in {elapsed:.2f} seconds")
        
    except Exception as e:
        # Log connection errors at info level, other errors at error level
        if "connection" in str(e).lower() or "refused" in str(e).lower():
            logger.info(f"Cache warming skipped - database connection issue: {e}")
        else:
            logger.error(f"Cache warming failed: {e}", exc_info=True)
    finally:
        if db:
            db.close()


async def _background_refresh_loop() -> None:
    """Background task that periodically refreshes the cache before it expires."""
    logger.info("Starting background cache refresh loop")
    
    while True:
        try:
            await asyncio.sleep(REFRESH_CHECK_INTERVAL)
            
            # Refresh all caches proactively
            logger.info("Running proactive cache refresh...")
            await warm_all_caches()
            
        except asyncio.CancelledError:
            logger.info("Background cache refresh loop cancelled")
            break
        except Exception as e:
            logger.error(f"Error in background cache refresh: {e}", exc_info=True)
            # Continue running despite errors
            await asyncio.sleep(60)  # Wait a bit before retrying


def start_background_refresh() -> None:
    """Start the background refresh task."""
    global _background_task
    if _background_task is None or _background_task.done():
        _background_task = asyncio.create_task(_background_refresh_loop())
        logger.info("Background cache refresh task started")


def stop_background_refresh() -> None:
    """Stop the background refresh task."""
    global _background_task
    if _background_task and not _background_task.done():
        _background_task.cancel()
        logger.info("Background cache refresh task stopped")
