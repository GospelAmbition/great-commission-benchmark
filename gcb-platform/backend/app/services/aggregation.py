"""Aggregation service for calculating and updating model version statistics.

This service is responsible for maintaining the pre-computed aggregate statistics
in the model_version_stats table, which powers the leaderboard with averaged
scores across multiple test submissions.
"""
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime
import logging
from decimal import Decimal
import asyncio

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.model_version_stats import ModelVersionStats
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.services.scoring import ScoringService

logger = logging.getLogger(__name__)


async def invalidate_model_stats_cache(model_id: Optional[UUID] = None, question_set_id: Optional[UUID] = None):
    """
    Invalidate caches affected by a model's stats update.
    
    When stats are updated, we need to invalidate:
    - Leaderboard cache (shows averaged scores)
    - Category rankings cache (shows category scores)
    - Model detail caches (shows individual model data)
    
    For simplicity, we clear all caches since the leaderboard/category caches
    are keyed by various filter combinations. A more sophisticated approach
    would selectively invalidate only affected keys.
    
    Args:
        model_id: Optional model UUID to invalidate specific model caches
        question_set_id: Optional question set UUID to scope invalidation
    """
    from app.core.cache import cache
    
    # For now, clear all caches since leaderboard keys include many filter combinations
    # A future optimization could track and invalidate only specific cache keys
    await cache.clear()
    logger.info(f"Cache invalidated for model={model_id}, question_set={question_set_id}")


class AggregationService:
    """Service for calculating and updating aggregate model-version statistics."""
    
    @classmethod
    def recalculate_model_stats(
        cls, 
        db: Session, 
        model_id: UUID, 
        question_set_id: UUID
    ) -> Optional[ModelVersionStats]:
        """
        Recalculate aggregate stats for a model-version pair from scratch.
        
        This method fetches all completed test runs for the given model and
        question_set, calculates averages across all tests, and updates or
        creates the ModelVersionStats record.
        
        Args:
            db: Database session
            model_id: UUID of the model
            question_set_id: UUID of the question set (benchmark version)
            
        Returns:
            The updated or created ModelVersionStats record, or None if no tests exist
        """
        # Get all completed test runs for this model+version
        test_runs = db.query(TestRun).filter(
            TestRun.model_id == model_id,
            TestRun.question_set_id == question_set_id,
            TestRun.status == "completed"
        ).order_by(TestRun.completed_at.asc()).all()
        
        if not test_runs:
            # No completed tests - remove stats if they exist
            existing = db.query(ModelVersionStats).filter(
                ModelVersionStats.model_id == model_id,
                ModelVersionStats.question_set_id == question_set_id
            ).first()
            if existing:
                db.delete(existing)
                db.commit()
            return None
        
        # Calculate scores for each test run
        all_scores = []
        all_verdict_distributions = []
        all_category_scores: Dict[str, List[float]] = {}
        
        for test_run in test_runs:
            try:
                scores = ScoringService.calculate_scores(db, str(test_run.id))
                all_scores.append({
                    "overall": scores["overall"],
                    "tier1": scores["tier1"],
                    "tier2": scores["tier2"],
                    "tier3": scores["tier3"],
                    "completed_at": test_run.completed_at
                })
                all_verdict_distributions.append(scores["verdict_distribution"])
                
                # Collect category scores
                for category, score in scores.get("category_scores", {}).items():
                    if category not in all_category_scores:
                        all_category_scores[category] = []
                    all_category_scores[category].append(score)
                    
            except Exception as e:
                logger.warning(f"Failed to calculate scores for test run {test_run.id}: {e}")
                continue
        
        if not all_scores:
            return None
        
        # Calculate averages
        test_count = len(all_scores)
        avg_overall = sum(s["overall"] for s in all_scores) / test_count
        avg_tier1 = sum(s["tier1"] for s in all_scores) / test_count
        avg_tier2 = sum(s["tier2"] for s in all_scores) / test_count
        avg_tier3 = sum(s["tier3"] for s in all_scores) / test_count
        
        overall_scores = [s["overall"] for s in all_scores]
        min_overall = min(overall_scores)
        max_overall = max(overall_scores)
        
        # Calculate average category scores
        avg_category_scores = {}
        for category, scores_list in all_category_scores.items():
            if scores_list:
                avg_category_scores[category] = round(sum(scores_list) / len(scores_list), 2)
        
        # Sum verdict distributions
        total_accepted = sum(d.get("ACCEPTED", 0) for d in all_verdict_distributions)
        total_compromised = sum(d.get("COMPROMISED", 0) for d in all_verdict_distributions)
        total_refused = sum(d.get("REFUSED", 0) for d in all_verdict_distributions)
        total_error = sum(d.get("ERROR", 0) for d in all_verdict_distributions)
        
        # Get first and last test timestamps
        first_test_at = all_scores[0]["completed_at"]
        last_test_at = all_scores[-1]["completed_at"]
        
        # Update or create the stats record
        stats = db.query(ModelVersionStats).filter(
            ModelVersionStats.model_id == model_id,
            ModelVersionStats.question_set_id == question_set_id
        ).first()
        
        if not stats:
            stats = ModelVersionStats(
                model_id=model_id,
                question_set_id=question_set_id
            )
            db.add(stats)
        
        # Update all fields
        stats.avg_overall_score = Decimal(str(round(avg_overall, 2)))
        stats.avg_tier1_score = Decimal(str(round(avg_tier1, 2)))
        stats.avg_tier2_score = Decimal(str(round(avg_tier2, 2)))
        stats.avg_tier3_score = Decimal(str(round(avg_tier3, 2)))
        stats.test_count = test_count
        stats.min_overall_score = Decimal(str(round(min_overall, 2)))
        stats.max_overall_score = Decimal(str(round(max_overall, 2)))
        stats.avg_category_scores = avg_category_scores
        stats.total_accepted = total_accepted
        stats.total_compromised = total_compromised
        stats.total_refused = total_refused
        stats.total_error = total_error
        stats.first_test_at = first_test_at
        stats.last_test_at = last_test_at
        stats.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(stats)
        
        logger.info(
            f"Recalculated stats for model {model_id}, question_set {question_set_id}: "
            f"test_count={test_count}, avg_overall={avg_overall:.2f}"
        )
        
        return stats
    
    @classmethod
    def update_stats_for_test_run(cls, db: Session, test_run: TestRun, invalidate_cache: bool = True) -> Optional[ModelVersionStats]:
        """
        Update stats when a new test run completes.
        
        This is a convenience method that extracts model_id and question_set_id
        from the test run and calls recalculate_model_stats.
        
        Args:
            db: Database session
            test_run: The completed test run
            invalidate_cache: Whether to invalidate caches after update (default True)
            
        Returns:
            The updated ModelVersionStats record
        """
        if test_run.status != "completed":
            logger.warning(f"Test run {test_run.id} is not completed, skipping stats update")
            return None
            
        stats = cls.recalculate_model_stats(
            db, 
            test_run.model_id, 
            test_run.question_set_id
        )
        
        # Invalidate caches asynchronously
        if invalidate_cache and stats:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(invalidate_model_stats_cache(
                        test_run.model_id, 
                        test_run.question_set_id
                    ))
                else:
                    loop.run_until_complete(invalidate_model_stats_cache(
                        test_run.model_id, 
                        test_run.question_set_id
                    ))
            except RuntimeError:
                # No event loop, skip async cache invalidation
                logger.warning("No event loop available for cache invalidation")
        
        return stats
    
    @classmethod
    def get_or_calculate_stats(
        cls, 
        db: Session, 
        model_id: UUID, 
        question_set_id: UUID
    ) -> Optional[ModelVersionStats]:
        """
        Get existing stats or calculate them if they don't exist.
        
        Args:
            db: Database session
            model_id: UUID of the model
            question_set_id: UUID of the question set
            
        Returns:
            The ModelVersionStats record, or None if no tests exist
        """
        stats = db.query(ModelVersionStats).filter(
            ModelVersionStats.model_id == model_id,
            ModelVersionStats.question_set_id == question_set_id
        ).first()
        
        if stats:
            return stats
            
        # Calculate stats if they don't exist
        return cls.recalculate_model_stats(db, model_id, question_set_id)
    
    @classmethod
    def get_individual_test_scores(
        cls, 
        db: Session, 
        model_id: UUID, 
        question_set_id: UUID
    ) -> List[Dict]:
        """
        Get individual test scores for a model-version pair.
        
        This is useful for displaying detailed breakdowns on model detail pages.
        
        Args:
            db: Database session
            model_id: UUID of the model
            question_set_id: UUID of the question set
            
        Returns:
            List of dictionaries with individual test scores and metadata
        """
        test_runs = db.query(TestRun).filter(
            TestRun.model_id == model_id,
            TestRun.question_set_id == question_set_id,
            TestRun.status == "completed"
        ).order_by(TestRun.completed_at.desc()).all()
        
        results = []
        for test_run in test_runs:
            try:
                scores = ScoringService.calculate_scores(db, str(test_run.id))
                results.append({
                    "test_run_id": str(test_run.id),
                    "overall_score": scores["overall"],
                    "tier1_score": scores["tier1"],
                    "tier2_score": scores["tier2"],
                    "tier3_score": scores["tier3"],
                    "category_scores": scores.get("category_scores", {}),
                    "verdict_distribution": scores.get("verdict_distribution", {}),
                    "completed_at": test_run.completed_at.isoformat() if test_run.completed_at else None,
                    "trust_tier": test_run.trust_tier,
                    "user_id": str(test_run.user_id) if test_run.user_id else None
                })
            except Exception as e:
                logger.warning(f"Failed to calculate scores for test run {test_run.id}: {e}")
                continue
        
        return results
    
    @classmethod
    def backfill_all_stats(cls, db: Session) -> Tuple[int, int]:
        """
        Backfill stats for all model-version pairs that have completed tests.
        
        This is useful for initial population of the model_version_stats table.
        
        Args:
            db: Database session
            
        Returns:
            Tuple of (success_count, error_count)
        """
        # Find all unique model-version pairs with completed tests
        pairs = db.query(
            TestRun.model_id, 
            TestRun.question_set_id
        ).filter(
            TestRun.status == "completed"
        ).distinct().all()
        
        success_count = 0
        error_count = 0
        
        for model_id, question_set_id in pairs:
            try:
                cls.recalculate_model_stats(db, model_id, question_set_id)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to backfill stats for model {model_id}, qs {question_set_id}: {e}")
                error_count += 1
        
        logger.info(f"Backfill complete: {success_count} successful, {error_count} errors")
        return success_count, error_count
