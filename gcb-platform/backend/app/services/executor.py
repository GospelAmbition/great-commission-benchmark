"""Benchmark execution service"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.db.models.question import Question
from app.db.models.question_set import QuestionSet
from app.services.openrouter import OpenRouterClient
from app.services.judge import JudgeService, JudgeResult
from app.services.scoring import ScoringService


class BenchmarkExecutor:
    """Service for executing benchmark tests"""
    
    # Configuration
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5
    
    def __init__(self, db: Session, openrouter_client: OpenRouterClient):
        self.db = db
        self.openrouter = openrouter_client
        self.judge = JudgeService(openrouter_client)
    
    async def execute(self, test_run_id: str) -> TestRun:
        """
        Execute a benchmark test run
        
        Args:
            test_run_id: Test run UUID
        
        Returns:
            Completed TestRun object
        """
        test_run = self.db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not test_run:
            raise ValueError(f"Test run {test_run_id} not found")
        
        # Update status to running
        test_run.status = "running"
        test_run.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Get questions for the question set
            questions = self.db.query(Question).filter(
                Question.question_set_id == test_run.question_set_id
            ).order_by(Question.tier, Question.category).all()
            
            # Get model info
            model = test_run.model
            model_id = model.model_id
            
            # Track failed questions for retry summary
            failed_questions = []
            
            # Execute each question
            for idx, question in enumerate(questions):
                # Check if already completed (resume from checkpoint)
                existing_result = self.db.query(Result).filter(
                    Result.test_run_id == test_run_id,
                    Result.question_id == question.id
                ).first()
                
                if existing_result:
                    continue  # Skip already completed questions
                
                # Execute question with retry logic
                success = await self._execute_question_with_retry(
                    test_run, question, model_id
                )
                
                if not success:
                    failed_questions.append(question.id)
                
                # Update checkpoint
                test_run.checkpoint_question_index = idx + 1
                self.db.commit()
            
            # Calculate scores
            scores = ScoringService.calculate_scores(self.db, test_run_id)
            
            # Run validation and check if flagging needed
            validation_result = await self._run_validation(test_run_id, scores)
            
            # Update test run with completion
            test_run.status = "completed"
            test_run.completed_at = datetime.utcnow()
            test_run.validation_metrics = {
                **scores,
                "validation": validation_result,
                "failed_questions": [str(q) for q in failed_questions]
            }
            
            # Check if should be flagged for review
            if validation_result.get("needs_review", False):
                test_run.trust_tier = "pending_review"
                test_run.admin_notes = validation_result.get("review_reason", "Flagged by automated validation")
            
            self.db.commit()
            
            return test_run
            
        except Exception as e:
            test_run.status = "failed"
            test_run.last_error = str(e)
            test_run.retry_count = (test_run.retry_count or 0) + 1
            self.db.commit()
            raise
    
    async def _execute_question_with_retry(
        self,
        test_run: TestRun,
        question: Question,
        model_id: str
    ) -> bool:
        """
        Execute a question with automatic retry on failure.
        
        Args:
            test_run: TestRun object
            question: Question object
            model_id: Model identifier
        
        Returns:
            True if successful, False if all retries failed
        """
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                await self._execute_question(test_run, question, model_id)
                return True
            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    # Wait before retry with exponential backoff
                    delay = self.RETRY_DELAY_SECONDS * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        # All retries failed - save error result
        error_result = Result(
            test_run_id=test_run.id,
            question_id=question.id,
            response=f"ERROR: {str(last_error)}",
            verdict="ERROR",
            reasoning=f"Failed after {self.MAX_RETRIES} attempts: {str(last_error)}",
            tokens_used=0
        )
        self.db.add(error_result)
        self.db.commit()
        
        return False
    
    async def _execute_question(
        self,
        test_run: TestRun,
        question: Question,
        model_id: str
    ):
        """
        Execute a single question
        
        Args:
            test_run: TestRun object
            question: Question object
            model_id: Model identifier
        """
        # Prepare messages
        messages = [
            {
                "role": "user",
                "content": question.content
            }
        ]
        
        # Get system prompt if provided (stored in validation_metrics for now)
        system_prompt = None
        if test_run.validation_metrics and isinstance(test_run.validation_metrics, dict):
            system_prompt = test_run.validation_metrics.get("system_prompt")
        
        # Call OpenRouter
        response = await self.openrouter.complete(
            model=model_id,
            messages=messages,
            system_prompt=system_prompt
        )
        
        # Evaluate response using LLM-as-Judge
        judge_result = await self.judge.evaluate(
            question=question.content,
            response=response["text"],
            tier=question.tier,
            category=question.category
        )
        
        # Normalize verdict for consistent scoring
        normalized_verdict = self.judge.normalize_verdict(judge_result.verdict, question.tier)
        
        # Build reasoning with full context
        reasoning = judge_result.reasoning
        if judge_result.refusal_type:
            reasoning = f"[{judge_result.refusal_type}] {reasoning}"
        if judge_result.confidence != "HIGH":
            reasoning = f"[Confidence: {judge_result.confidence}] {reasoning}"
        
        # Save result
        result = Result(
            test_run_id=test_run.id,
            question_id=question.id,
            response=response["text"],
            verdict=normalized_verdict,
            reasoning=reasoning,
            tokens_used=response.get("usage", {}).get("total_tokens", 0)
        )
        self.db.add(result)
        self.db.commit()
    
    async def _run_validation(self, test_run_id: str, scores: Dict) -> Dict:
        """
        Run validation checks on completed test.
        
        Checks:
        - Score anomalies (too high/low might indicate issues)
        - High ERROR rate
        - Inconsistent verdicts across similar questions
        
        Args:
            test_run_id: Test run UUID
            scores: Calculated scores dict
        
        Returns:
            Validation result dict with needs_review flag and reasons
        """
        validation = {
            "needs_review": False,
            "review_reason": None,
            "checks": {}
        }
        
        # Get results for this test run
        results = self.db.query(Result).filter(Result.test_run_id == test_run_id).all()
        total = len(results)
        
        if total == 0:
            validation["needs_review"] = True
            validation["review_reason"] = "No results recorded"
            return validation
        
        # Check 1: Error rate
        error_count = sum(1 for r in results if r.verdict == "ERROR")
        error_rate = error_count / total
        validation["checks"]["error_rate"] = {
            "value": round(error_rate * 100, 2),
            "threshold": 10,
            "passed": error_rate < 0.10
        }
        
        if error_rate >= 0.10:
            validation["needs_review"] = True
            validation["review_reason"] = f"High error rate: {error_rate*100:.1f}%"
        
        # Check 2: Score anomalies
        overall_score = scores.get("overall", 0)
        validation["checks"]["score_anomaly"] = {
            "value": overall_score,
            "passed": True
        }
        
        # Perfect scores are suspicious
        if overall_score >= 99:
            validation["needs_review"] = True
            validation["review_reason"] = f"Unusually high score: {overall_score}%"
            validation["checks"]["score_anomaly"]["passed"] = False
        
        # Very low scores might indicate model issues
        if overall_score <= 5 and error_rate < 0.10:
            validation["needs_review"] = True  
            validation["review_reason"] = f"Unusually low score: {overall_score}%"
            validation["checks"]["score_anomaly"]["passed"] = False
        
        # Check 3: Verdict distribution
        verdict_dist = scores.get("verdict_distribution", {})
        total_verdicts = sum(verdict_dist.values())
        
        if total_verdicts > 0:
            # Check for highly skewed distribution
            accepted_rate = verdict_dist.get("ACCEPTED", 0) / total_verdicts
            refused_rate = verdict_dist.get("REFUSED", 0) / total_verdicts
            
            validation["checks"]["verdict_distribution"] = {
                "accepted_rate": round(accepted_rate * 100, 2),
                "refused_rate": round(refused_rate * 100, 2),
                "passed": True
            }
            
            # 100% acceptance or 100% refusal is suspicious for a full test
            if total_verdicts > 50 and (accepted_rate >= 0.99 or refused_rate >= 0.99):
                validation["needs_review"] = True
                validation["review_reason"] = "Extremely skewed verdict distribution"
                validation["checks"]["verdict_distribution"]["passed"] = False
        
        # Check 4: Tier consistency
        tier_scores = {
            "tier1": scores.get("tier1", 0),
            "tier2": scores.get("tier2", 0),
            "tier3": scores.get("tier3", 0)
        }
        
        # Large discrepancies between tiers might warrant review
        if tier_scores["tier1"] > 0 and tier_scores["tier2"] > 0:
            tier_diff = abs(tier_scores["tier1"] - tier_scores["tier2"])
            validation["checks"]["tier_consistency"] = {
                "tier1": tier_scores["tier1"],
                "tier2": tier_scores["tier2"],
                "tier3": tier_scores["tier3"],
                "max_diff": round(tier_diff, 2),
                "passed": tier_diff < 50
            }
            
            if tier_diff >= 50:
                if not validation["needs_review"]:
                    validation["needs_review"] = True
                    validation["review_reason"] = f"Large tier score discrepancy: {tier_diff:.1f} points"
        
        return validation
    
    async def resume(self, test_run_id: str) -> TestRun:
        """
        Resume a paused or failed test run from checkpoint.
        
        Args:
            test_run_id: Test run UUID
        
        Returns:
            Completed TestRun object
        """
        test_run = self.db.query(TestRun).filter(TestRun.id == test_run_id).first()
        if not test_run:
            raise ValueError(f"Test run {test_run_id} not found")
        
        if test_run.status == "completed":
            raise ValueError("Test run is already completed")
        
        if test_run.status == "cancelled":
            raise ValueError("Test run was cancelled")
        
        # Reset status and continue execution
        test_run.status = "running"
        test_run.last_error = None
        self.db.commit()
        
        return await self.execute(test_run_id)
