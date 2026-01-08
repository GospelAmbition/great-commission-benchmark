"""Scoring service for calculating benchmark scores"""
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.models.result import Result
from app.db.models.question import Question
from app.core.benchmark_config import (
    TIER1_WEIGHT,
    TIER2_WEIGHT,
    TIER3_WEIGHT,
    VERDICT_POINTS,
    LEGACY_VERDICT_MAPPING,
)


class ScoringService:
    """Service for calculating benchmark scores"""
    
    # Import from shared config
    TIER1_WEIGHT = TIER1_WEIGHT
    TIER2_WEIGHT = TIER2_WEIGHT
    TIER3_WEIGHT = TIER3_WEIGHT
    VERDICT_POINTS = VERDICT_POINTS
    
    @classmethod
    def calculate_tier_score(cls, results: List[Result], tier: int) -> float:
        """
        Calculate score for a specific tier
        
        Args:
            results: List of Result objects
            tier: Tier number (1, 2, or 3)
        
        Returns:
            Score as percentage (0-100)
        """
        tier_results = [r for r in results if r.question.tier == tier]
        
        if not tier_results:
            return 0.0
        
        total_points = 0.0
        for result in tier_results:
            points = cls.VERDICT_POINTS.get(result.verdict, 0.0)
            total_points += points
        
        max_points = len(tier_results)
        if max_points == 0:
            return 0.0
        
        return (total_points / max_points) * 100
    
    @classmethod
    def calculate_category_score(cls, results: List[Result], category: str) -> float:
        """
        Calculate score for a specific category
        
        Args:
            results: List of Result objects
            category: Category identifier (e.g., "3.1")
        
        Returns:
            Score as percentage (0-100)
        """
        category_results = [r for r in results if r.question.category == category]
        
        if not category_results:
            return 0.0
        
        total_points = 0.0
        for result in category_results:
            points = cls.VERDICT_POINTS.get(result.verdict, 0.0)
            total_points += points
        
        max_points = len(category_results)
        if max_points == 0:
            return 0.0
        
        return (total_points / max_points) * 100
    
    @classmethod
    def calculate_overall_score(cls, tier1_score: float, tier2_score: float, tier3_score: float) -> float:
        """
        Calculate weighted overall score
        
        Args:
            tier1_score: Tier 1 score (0-100)
            tier2_score: Tier 2 score (0-100)
            tier3_score: Tier 3 score (0-100)
        
        Returns:
            Weighted overall score (0-100)
        """
        return (
            (tier1_score * cls.TIER1_WEIGHT) +
            (tier2_score * cls.TIER2_WEIGHT) +
            (tier3_score * cls.TIER3_WEIGHT)
        )
    
    @classmethod
    def calculate_scores(cls, db: Session, test_run_id: str) -> Dict:
        """
        Calculate all scores for a test run
        
        Args:
            db: Database session
            test_run_id: Test run UUID
        
        Returns:
            Dictionary with all scores
        """
        from app.db.models.test_run import TestRun
        
        test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not test_run:
            raise ValueError(f"Test run {test_run_id} not found")
        
        # Get all results for this test run
        results = db.query(Result).filter(Result.test_run_id == test_run_id).all()
        
        # Calculate tier scores
        tier1_score = cls.calculate_tier_score(results, 1)
        tier2_score = cls.calculate_tier_score(results, 2)
        tier3_score = cls.calculate_tier_score(results, 3)
        
        # Calculate overall score
        overall_score = cls.calculate_overall_score(tier1_score, tier2_score, tier3_score)
        
        # Calculate category scores
        categories = set(r.question.category for r in results)
        category_scores = {}
        for category in categories:
            category_scores[category] = cls.calculate_category_score(results, category)
        
        # Calculate verdict distribution (unified verdicts only)
        # Map legacy verdicts to unified verdicts for distribution
        verdict_dist = {"ACCEPTED": 0, "COMPROMISED": 0, "REFUSED": 0, "ERROR": 0}
        for r in results:
            verdict = r.verdict
            # Map legacy verdicts to unified verdicts using shared config
            if verdict in LEGACY_VERDICT_MAPPING:
                verdict = LEGACY_VERDICT_MAPPING[verdict]
            if verdict in verdict_dist:
                verdict_dist[verdict] += 1
        
        return {
            "overall": round(overall_score, 2),
            "tier1": round(tier1_score, 2),
            "tier2": round(tier2_score, 2),
            "tier3": round(tier3_score, 2),
            "category_scores": category_scores,
            "verdict_distribution": verdict_dist,
            "total_questions": len(results)
        }