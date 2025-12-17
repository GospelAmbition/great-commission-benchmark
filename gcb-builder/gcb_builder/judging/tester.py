"""
Judge Testing Framework for GCB Builder.

This module provides:
- Test case management (CRUD operations)
- Accuracy measurement (target: ≥90%)
- Cohen's Kappa calculation
- Confusion matrix generation
- Per-tier and refusal type accuracy tracking
- Validation workflow for judge prompts

Reference: spec-inter-rater-reliability.md for methodology
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from gcb_builder.core.database import get_db
from gcb_builder.core.models import JudgeTestCase, JudgeTestResult


# Verdict types for each tier
TIER1_VERDICTS = ["ACCEPTED", "COMPROMISED", "REFUSED"]
TIER2_VERDICTS = ["LOYAL", "COMPROMISED", "DISLOYAL"]
TIER3_VERDICTS = ["AFFIRMED", "HEDGED", "DENIED"]
REFUSAL_TYPES = ["CAPABILITY", "SAFETY", "IDEOLOGICAL", "UNCLEAR"]


@dataclass
class Verdict:
    """Represents a judge verdict."""
    verdict: str
    refusal_type: Optional[str] = None
    reasoning: Optional[str] = None
    confidence: Optional[str] = None


@dataclass
class ValidationResult:
    """Results from validating a judge prompt."""
    total_cases: int
    correct_verdicts: int
    accuracy: float
    cohens_kappa: float
    per_tier_accuracy: dict[int, float]
    refusal_type_accuracy: Optional[float]
    confusion_matrix: dict[str, dict[str, int]]
    misclassified_cases: list[dict[str, Any]]
    passed: bool
    judge_prompt_version: Optional[str] = None
    judge_model: Optional[str] = None


class LLMBackend(Protocol):
    """Protocol for LLM backends used by the judge."""
    
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Complete a chat completion request."""
        ...


class JudgeTester:
    """
    Test case management and validation system for judge prompts.
    
    Provides functionality to:
    - Create and manage test cases
    - Run judge prompts against test cases
    - Calculate accuracy metrics
    - Generate validation reports
    """
    
    def __init__(self, backend: Optional[LLMBackend] = None):
        """
        Initialize the judge tester.
        
        Args:
            backend: Optional LLM backend for running judge evaluations.
                    If None, test cases can still be managed but not evaluated.
        """
        self.backend = backend
        self._judge_prompts_cache: dict[int, str] = {}
    
    # ============================================================================
    # Test Case Management
    # ============================================================================
    
    def create_test_case(
        self,
        prompt: str,
        sample_response: str,
        expected_verdict: str,
        tier: int,
        expected_refusal_type: Optional[str] = None,
        verdict_reasoning: Optional[str] = None,
        category: Optional[str] = None,
        question_id: Optional[int] = None,
    ) -> JudgeTestCase:
        """
        Create a new test case.
        
        Args:
            prompt: The question/prompt text
            sample_response: The response to evaluate
            expected_verdict: Expected verdict (ACCEPTED, COMPROMISED, REFUSED, etc.)
            tier: Tier number (1, 2, or 3)
            expected_refusal_type: Expected refusal type if verdict is REFUSED
            verdict_reasoning: Explanation of why this is the correct verdict
            category: Optional category ID (e.g., "3.2")
            question_id: Optional link to a Question record
            
        Returns:
            The created JudgeTestCase
        """
        if tier not in [1, 2, 3]:
            raise ValueError(f"Tier must be 1, 2, or 3, got {tier}")
        
        # Validate verdict for tier
        valid_verdicts = {
            1: TIER1_VERDICTS,
            2: TIER2_VERDICTS,
            3: TIER3_VERDICTS,
        }
        if expected_verdict not in valid_verdicts[tier]:
            raise ValueError(
                f"Invalid verdict for tier {tier}: {expected_verdict}. "
                f"Valid verdicts: {valid_verdicts[tier]}"
            )
        
        # Validate refusal type if provided
        if expected_refusal_type and expected_refusal_type not in REFUSAL_TYPES:
            raise ValueError(
                f"Invalid refusal type: {expected_refusal_type}. "
                f"Valid types: {REFUSAL_TYPES}"
            )
        
        with get_db() as db:
            test_case = JudgeTestCase(
                prompt=prompt,
                sample_response=sample_response,
                expected_verdict=expected_verdict,
                expected_refusal_type=expected_refusal_type,
                verdict_reasoning=verdict_reasoning,
                tier=tier,
                category=category,
                question_id=question_id,
            )
            db.add(test_case)
            db.commit()
            test_case_id = test_case.id
        
        # Return a fresh query - the object will be attached to a new session
        # Caller should use it within their own session context if needed
        with get_db() as db:
            result = db.get(JudgeTestCase, test_case_id)
            # Make transient so it can be used outside session
            from sqlalchemy.orm import make_transient
            make_transient(result)
            # Pre-load all scalar attributes
            _ = result.id, result.prompt, result.sample_response, result.expected_verdict
            return result
    
    def get_test_case(self, test_case_id: int) -> Optional[JudgeTestCase]:
        """Get a test case by ID."""
        with get_db() as db:
            result = db.get(JudgeTestCase, test_case_id)
            if result:
                from sqlalchemy.orm import make_transient
                make_transient(result)
                # Pre-load all scalar attributes
                _ = (
                    result.id,
                    result.prompt,
                    result.sample_response,
                    result.expected_verdict,
                    result.tier,
                )
            return result
    
    def list_test_cases(
        self,
        tier: Optional[int] = None,
        category: Optional[str] = None,
    ) -> list[JudgeTestCase]:
        """
        List test cases, optionally filtered by tier or category.
        
        Args:
            tier: Optional tier filter (1, 2, or 3)
            category: Optional category filter (e.g., "3.2")
            
        Returns:
            List of matching test cases
        """
        with get_db() as db:
            query = select(JudgeTestCase)
            
            if tier is not None:
                query = query.where(JudgeTestCase.tier == tier)
            
            if category is not None:
                query = query.where(JudgeTestCase.category == category)
            
            query = query.order_by(JudgeTestCase.tier, JudgeTestCase.category)
            results = list(db.scalars(query).all())
            # Make all results transient and pre-load attributes
            from sqlalchemy.orm import make_transient
            for result in results:
                make_transient(result)
                _ = (
                    result.id,
                    result.prompt,
                    result.tier,
                    result.expected_verdict,
                )
            return results
    
    def delete_test_case(self, test_case_id: int) -> bool:
        """
        Delete a test case.
        
        Returns:
            True if deleted, False if not found
        """
        with get_db() as db:
            test_case = db.get(JudgeTestCase, test_case_id)
            if test_case:
                db.delete(test_case)
                db.commit()
                return True
            return False
    
    # ============================================================================
    # Judge Prompt Loading
    # ============================================================================
    
    def load_judge_prompt(self, tier: int) -> str:
        """
        Load a judge prompt from the judge_prompts directory.
        
        Args:
            tier: Tier number (1, 2, or 3)
            
        Returns:
            The judge prompt template text
        """
        if tier in self._judge_prompts_cache:
            return self._judge_prompts_cache[tier]
        
        # Determine prompt file name
        prompt_files = {
            1: "tier1_task.md",
            2: "tier2_doctrine.md",
            3: "tier3_worldview.md",
        }
        
        prompt_file = prompt_files.get(tier)
        if not prompt_file:
            raise ValueError(f"Invalid tier: {tier}")
        
        # Find the judge_prompts directory (at project root)
        project_root = Path(__file__).parent.parent.parent
        prompt_path = project_root / "judge_prompts" / prompt_file
        
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Judge prompt file not found: {prompt_path}. "
                f"Expected at: {project_root / 'judge_prompts'}"
            )
        
        # Load and extract the template section
        content = prompt_path.read_text()
        
        # Extract the template (between ``` markers or after "## Judge Prompt Template")
        template_match = re.search(
            r"## Judge Prompt Template\s*```\s*(.*?)\s*```",
            content,
            re.DOTALL,
        )
        
        if template_match:
            template = template_match.group(1).strip()
        else:
            # Fallback: look for any code block with the template
            code_block_match = re.search(
                r"```\s*(.*?)\s*```",
                content,
                re.DOTALL,
            )
            if code_block_match:
                template = code_block_match.group(1).strip()
            else:
                # Last resort: use the full file content
                template = content
        
        self._judge_prompts_cache[tier] = template
        return template
    
    def format_judge_prompt(
        self,
        tier: int,
        question: str,
        response: str,
    ) -> str:
        """
        Format a judge prompt with question and response.
        
        Args:
            tier: Tier number (1, 2, or 3)
            question: The question/prompt text
            response: The response to evaluate
            
        Returns:
            Formatted prompt ready for LLM
        """
        template = self.load_judge_prompt(tier)
        return template.format(question=question, response=response)
    
    # ============================================================================
    # Judge Evaluation
    # ============================================================================
    
    def parse_verdict(self, judge_response: str) -> Verdict:
        """
        Parse a judge response to extract verdict information.
        
        Expected format:
        VERDICT: [ACCEPTED|COMPROMISED|REFUSED|...]
        REFUSAL_TYPE: [CAPABILITY|SAFETY|IDEOLOGICAL|UNCLEAR] (optional)
        CONFIDENCE: [HIGH|MEDIUM|LOW] (optional)
        REASONING: [text]
        
        Args:
            judge_response: Raw response from the judge LLM
            
        Returns:
            Parsed Verdict object
        """
        verdict_match = re.search(
            r"VERDICT:\s*([A-Z_]+)",
            judge_response,
            re.IGNORECASE,
        )
        verdict = verdict_match.group(1).upper() if verdict_match else None
        
        refusal_type_match = re.search(
            r"REFUSAL_TYPE:\s*([A-Z_]+)",
            judge_response,
            re.IGNORECASE,
        )
        refusal_type = (
            refusal_type_match.group(1).upper() if refusal_type_match else None
        )
        
        confidence_match = re.search(
            r"CONFIDENCE:\s*([A-Z]+)",
            judge_response,
            re.IGNORECASE,
        )
        confidence = (
            confidence_match.group(1).upper() if confidence_match else None
        )
        
        reasoning_match = re.search(
            r"REASONING:\s*(.*?)(?:\n\n|\Z)",
            judge_response,
            re.DOTALL | re.IGNORECASE,
        )
        reasoning = reasoning_match.group(1).strip() if reasoning_match else None
        
        if not verdict:
            raise ValueError(
                f"Could not parse verdict from judge response: {judge_response[:200]}"
            )
        
        return Verdict(
            verdict=verdict,
            refusal_type=refusal_type,
            reasoning=reasoning,
            confidence=confidence,
        )
    
    async def evaluate_test_case(
        self,
        test_case: JudgeTestCase,
        judge_model: str,
        judge_prompt_version: Optional[str] = None,
    ) -> JudgeTestResult:
        """
        Evaluate a test case using the judge prompt.
        
        Args:
            test_case: The test case to evaluate
            judge_model: Model identifier to use for judging
            judge_prompt_version: Optional version identifier for the judge prompt
            
        Returns:
            JudgeTestResult with the evaluation
        """
        if not self.backend:
            raise ValueError(
                "No LLM backend provided. Cannot evaluate test cases."
            )
        
        # Access test case attributes while in session context
        # (test_case might be detached, so we need to get fresh copy)
        with get_db() as db:
            fresh_test_case = db.get(JudgeTestCase, test_case.id)
            if not fresh_test_case:
                raise ValueError(f"Test case {test_case.id} not found")
            tier = fresh_test_case.tier
            prompt_text = self.format_judge_prompt(
                tier=tier,
                question=fresh_test_case.prompt,
                response=fresh_test_case.sample_response,
            )
        
        # Call the LLM
        judge_response = await self.backend.complete(
            messages=[{"role": "user", "content": prompt_text}],
            model=judge_model,
        )
        
        # Parse the verdict
        verdict = self.parse_verdict(judge_response)
        
        # Check if verdict matches
        verdict_correct = verdict.verdict == test_case.expected_verdict
        
        # Check refusal type if applicable
        refusal_type_correct = None
        if test_case.expected_refusal_type:
            refusal_type_correct = (
                verdict.refusal_type == test_case.expected_refusal_type
            )
        elif verdict.refusal_type and test_case.expected_verdict == "REFUSED":
            # If we got a refusal type but didn't expect one, it's incorrect
            refusal_type_correct = False
        
        # Save the result
        with get_db() as db:
            result = JudgeTestResult(
                test_case_id=test_case.id,
                actual_verdict=verdict.verdict,
                actual_refusal_type=verdict.refusal_type,
                judge_response=judge_response,
                judge_prompt_version=judge_prompt_version,
                judge_model=judge_model,
                verdict_correct=verdict_correct,
                refusal_type_correct=refusal_type_correct,
            )
            db.add(result)
            db.commit()
            result_id = result.id
            from sqlalchemy.orm import make_transient
            make_transient(result)
            # Pre-load all scalar attributes
            _ = (
                result.id,
                result.actual_verdict,
                result.verdict_correct,
                result.actual_refusal_type,
            )
            return result
    
    # ============================================================================
    # Validation and Metrics
    # ============================================================================
    
    async def validate_judge(
        self,
        tier: Optional[int] = None,
        judge_model: str = "gpt-4",
        judge_prompt_version: Optional[str] = None,
        min_accuracy: float = 0.90,
        min_kappa: float = 0.60,
    ) -> ValidationResult:
        """
        Validate a judge prompt against all test cases (or filtered by tier).
        
        Args:
            tier: Optional tier filter (1, 2, or 3). If None, validates all tiers.
            judge_model: Model identifier to use for judging
            judge_prompt_version: Optional version identifier for the judge prompt
            min_accuracy: Minimum accuracy threshold (default: 0.90 = 90%)
            min_kappa: Minimum Cohen's Kappa threshold (default: 0.60)
            
        Returns:
            ValidationResult with all metrics
        """
        # Get test cases
        test_cases = self.list_test_cases(tier=tier)
        
        if not test_cases:
            raise ValueError(
                f"No test cases found for tier={tier}. "
                "Create test cases before validating."
            )
        
        # Evaluate all test cases
        results: list[tuple[JudgeTestCase, JudgeTestResult]] = []
        for test_case in test_cases:
            result = await self.evaluate_test_case(
                test_case,
                judge_model=judge_model,
                judge_prompt_version=judge_prompt_version,
            )
            results.append((test_case, result))
        
        # Calculate metrics
        return self._calculate_validation_metrics(
            results,
            judge_prompt_version=judge_prompt_version,
            judge_model=judge_model,
            min_accuracy=min_accuracy,
            min_kappa=min_kappa,
        )
    
    def _calculate_validation_metrics(
        self,
        results: list[tuple[JudgeTestCase, JudgeTestResult]],
        judge_prompt_version: Optional[str],
        judge_model: Optional[str],
        min_accuracy: float,
        min_kappa: float,
    ) -> ValidationResult:
        """Calculate all validation metrics from results."""
        total_cases = len(results)
        correct_verdicts = sum(1 for _, r in results if r.verdict_correct)
        accuracy = correct_verdicts / total_cases if total_cases > 0 else 0.0
        
        # Per-tier accuracy
        per_tier_accuracy: dict[int, float] = {}
        tier_results: dict[int, list[tuple[JudgeTestCase, JudgeTestResult]]] = (
            defaultdict(list)
        )
        for test_case, result in results:
            tier_results[test_case.tier].append((test_case, result))
        
        for tier, tier_data in tier_results.items():
            tier_correct = sum(1 for _, r in tier_data if r.verdict_correct)
            per_tier_accuracy[tier] = (
                tier_correct / len(tier_data) if tier_data else 0.0
            )
        
        # Refusal type accuracy (only for REFUSED verdicts)
        refused_results = [
            (tc, r)
            for tc, r in results
            if tc.expected_verdict == "REFUSED" and tc.expected_refusal_type
        ]
        refusal_type_accuracy = None
        if refused_results:
            refusal_correct = sum(
                1
                for _, r in refused_results
                if r.refusal_type_correct is True
            )
            refusal_type_accuracy = (
                refusal_correct / len(refused_results)
                if refused_results
                else 0.0
            )
        
        # Confusion matrix
        confusion_matrix = self._build_confusion_matrix(results)
        
        # Cohen's Kappa
        cohens_kappa = self._calculate_cohens_kappa(results)
        
        # Misclassified cases
        misclassified = [
            {
                "test_case_id": tc.id,
                "expected_verdict": tc.expected_verdict,
                "actual_verdict": r.actual_verdict,
                "expected_refusal_type": tc.expected_refusal_type,
                "actual_refusal_type": r.actual_refusal_type,
                "reasoning": r.judge_response,
            }
            for tc, r in results
            if not r.verdict_correct
        ]
        
        # Check if passed
        passed = (
            accuracy >= min_accuracy
            and cohens_kappa >= min_kappa
            and all(acc >= 0.85 for acc in per_tier_accuracy.values())
        )
        
        return ValidationResult(
            total_cases=total_cases,
            correct_verdicts=correct_verdicts,
            accuracy=accuracy,
            cohens_kappa=cohens_kappa,
            per_tier_accuracy=per_tier_accuracy,
            refusal_type_accuracy=refusal_type_accuracy,
            confusion_matrix=confusion_matrix,
            misclassified_cases=misclassified,
            passed=passed,
            judge_prompt_version=judge_prompt_version,
            judge_model=judge_model,
        )
    
    def _build_confusion_matrix(
        self,
        results: list[tuple[JudgeTestCase, JudgeTestResult]],
    ) -> dict[str, dict[str, int]]:
        """
        Build a confusion matrix.
        
        Returns:
            Dict mapping expected_verdict -> {actual_verdict: count}
        """
        matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        for test_case, result in results:
            expected = test_case.expected_verdict
            actual = result.actual_verdict
            matrix[expected][actual] += 1
        
        # Convert to regular dict for serialization
        return {k: dict(v) for k, v in matrix.items()}
    
    def _calculate_cohens_kappa(
        self,
        results: list[tuple[JudgeTestCase, JudgeTestResult]],
    ) -> float:
        """
        Calculate Cohen's Kappa for inter-rater reliability.
        
        Formula: κ = (Po - Pe) / (1 - Pe)
        where:
          Po = observed agreement (proportion of matching verdicts)
          Pe = expected agreement by chance
        
        Args:
            results: List of (test_case, result) tuples
            
        Returns:
            Cohen's Kappa value (between -1 and 1)
        """
        if not results:
            return 0.0
        
        # Count agreements
        agreements = sum(1 for _, r in results if r.verdict_correct)
        total = len(results)
        po = agreements / total if total > 0 else 0.0
        
        # Calculate expected agreement by chance
        # Get all unique verdicts
        all_verdicts = set()
        expected_counts: Counter[str] = Counter()
        actual_counts: Counter[str] = Counter()
        
        for test_case, result in results:
            expected = test_case.expected_verdict
            actual = result.actual_verdict
            all_verdicts.add(expected)
            all_verdicts.add(actual)
            expected_counts[expected] += 1
            actual_counts[actual] += 1
        
        # Calculate Pe (expected agreement by chance)
        pe = 0.0
        for verdict in all_verdicts:
            expected_prop = expected_counts[verdict] / total
            actual_prop = actual_counts[verdict] / total
            pe += expected_prop * actual_prop
        
        # Calculate Kappa
        if pe == 1.0:
            # Perfect agreement by chance (edge case)
            return 1.0 if po == 1.0 else 0.0
        
        kappa = (po - pe) / (1 - pe)
        return kappa
    
    # ============================================================================
    # Reporting
    # ============================================================================
    
    def format_validation_report(self, result: ValidationResult) -> str:
        """
        Format a human-readable validation report.
        
        Args:
            result: ValidationResult to format
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("Judge Prompt Validation Report")
        lines.append("=" * 70)
        lines.append("")
        
        if result.judge_prompt_version:
            lines.append(f"Judge Prompt Version: {result.judge_prompt_version}")
        if result.judge_model:
            lines.append(f"Judge Model: {result.judge_model}")
        lines.append(f"Total Test Cases: {result.total_cases}")
        lines.append("")
        
        lines.append("Overall Metrics:")
        lines.append("-" * 70)
        lines.append(
            f"  Verdict Accuracy: {result.correct_verdicts}/{result.total_cases} "
            f"({result.accuracy:.1%})"
        )
        status = "✓ PASSED" if result.accuracy >= 0.90 else "✗ FAILED"
        lines.append(f"    Threshold: ≥90%  {status}")
        lines.append("")
        
        lines.append(
            f"  Cohen's Kappa: {result.cohens_kappa:.3f}"
        )
        kappa_status = "✓ PASSED" if result.cohens_kappa >= 0.60 else "✗ FAILED"
        lines.append(f"    Threshold: ≥0.60  {kappa_status}")
        lines.append("")
        
        if result.per_tier_accuracy:
            lines.append("Per-Tier Accuracy:")
            lines.append("-" * 70)
            for tier in sorted(result.per_tier_accuracy.keys()):
                acc = result.per_tier_accuracy[tier]
                tier_status = "✓" if acc >= 0.85 else "✗"
                lines.append(f"  Tier {tier}: {acc:.1%}  {tier_status}")
            lines.append("")
        
        if result.refusal_type_accuracy is not None:
            lines.append("Refusal Type Accuracy:")
            lines.append("-" * 70)
            lines.append(f"  {result.refusal_type_accuracy:.1%}")
            refusal_status = (
                "✓ PASSED" if result.refusal_type_accuracy >= 0.80 else "✗ FAILED"
            )
            lines.append(f"    Threshold: ≥80%  {refusal_status}")
            lines.append("")
        
        if result.confusion_matrix:
            lines.append("Confusion Matrix:")
            lines.append("-" * 70)
            # Get all unique verdicts
            all_verdicts = set()
            for expected, actuals in result.confusion_matrix.items():
                all_verdicts.add(expected)
                all_verdicts.update(actuals.keys())
            
            all_verdicts = sorted(all_verdicts)
            
            # Header
            header = "                    │"
            for v in all_verdicts:
                header += f" {v:^12} │"
            lines.append(header)
            lines.append("-" * len(header))
            
            # Rows
            for expected in all_verdicts:
                row = f"Actual {expected:12} │"
                for actual in all_verdicts:
                    count = result.confusion_matrix.get(expected, {}).get(actual, 0)
                    row += f" {count:^12} │"
                lines.append(row)
            lines.append("")
        
        if result.misclassified_cases:
            lines.append(f"Misclassified Cases ({len(result.misclassified_cases)}):")
            lines.append("-" * 70)
            for case in result.misclassified_cases[:10]:  # Show first 10
                lines.append(
                    f"  Test Case {case['test_case_id']}: "
                    f"Expected {case['expected_verdict']}, "
                    f"Got {case['actual_verdict']}"
                )
            if len(result.misclassified_cases) > 10:
                lines.append(
                    f"  ... and {len(result.misclassified_cases) - 10} more"
                )
            lines.append("")
        
        lines.append("Final Status:")
        lines.append("-" * 70)
        final_status = (
            "✓ PASSED - Judge prompt meets validation thresholds"
            if result.passed
            else "✗ FAILED - Judge prompt does not meet validation thresholds"
        )
        lines.append(final_status)
        lines.append("")
        
        return "\n".join(lines)
