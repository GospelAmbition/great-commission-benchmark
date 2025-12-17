"""
Version validator for GCB Builder.

Validates benchmark versions before publishing:
- Category coverage
- Tier distribution
- Question completeness
- Metadata coverage
"""

from dataclasses import dataclass, field
from typing import Optional

from gcb_builder.core.categories import (
    CATEGORIES,
    QUESTION_TARGETS,
    get_categories_by_tier,
)
from gcb_builder.versioning.builder import VersionBuilder


@dataclass
class ValidationIssue:
    """A validation issue."""
    
    severity: str  # "error", "warning", "info"
    category: str  # Category of issue
    message: str
    details: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of version validation."""
    
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    stats: Optional[dict] = None
    
    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]
    
    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]
    
    @property
    def info(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "info"]


class VersionValidator:
    """
    Validates benchmark versions for publication.
    
    Checks:
    - All 19 categories represented
    - Minimum questions per category
    - Tier distribution (70/20/10 ± tolerance)
    - Capability vs willingness balance
    - Metadata coverage
    - No duplicate questions
    - Expected refusal types set for negative verdicts
    """
    
    def __init__(
        self,
        min_questions_per_category: int = 4,
        tier_tolerance: float = 5.0,  # Percentage points
        min_metadata_coverage: float = 0.75,  # 75%
    ):
        self.min_questions_per_category = min_questions_per_category
        self.tier_tolerance = tier_tolerance
        self.min_metadata_coverage = min_metadata_coverage
    
    def validate(self, version_id: int) -> ValidationResult:
        """
        Validate a version for publication.
        
        Args:
            version_id: Version ID to validate
            
        Returns:
            ValidationResult with issues and validity status
        """
        builder = VersionBuilder()
        version = builder.get_version(version_id)
        
        if not version:
            return ValidationResult(
                is_valid=False,
                issues=[ValidationIssue(
                    severity="error",
                    category="version",
                    message=f"Version {version_id} not found",
                )]
            )
        
        questions = builder.get_version_questions(version_id)
        stats = builder.get_version_stats(version_id)
        
        issues = []
        
        # Check minimum questions
        if stats.total_questions < 30:
            issues.append(ValidationIssue(
                severity="error",
                category="count",
                message=f"Insufficient questions: {stats.total_questions} (minimum 30)",
            ))
        
        # Check category coverage
        category_issues = self._check_category_coverage(stats.category_counts)
        issues.extend(category_issues)
        
        # Check tier distribution
        tier_issues = self._check_tier_distribution(stats.tier_percentages)
        issues.extend(tier_issues)
        
        # Check capability/willingness balance
        balance_issues = self._check_capability_willingness_balance(
            stats.capability_only,
            stats.willingness_only,
            stats.both,
            stats.total_questions,
        )
        issues.extend(balance_issues)
        
        # Check metadata coverage
        metadata_issues = self._check_metadata_coverage(questions)
        issues.extend(metadata_issues)
        
        # Check refusal types
        refusal_issues = self._check_refusal_types(questions)
        issues.extend(refusal_issues)
        
        # Check for duplicates
        duplicate_issues = self._check_duplicates(questions)
        issues.extend(duplicate_issues)
        
        # Add info about locked questions
        if stats.locked_questions > 0:
            pct = stats.locked_questions / stats.total_questions * 100
            issues.append(ValidationIssue(
                severity="info",
                category="quality",
                message=f"{stats.locked_questions} locked questions ({pct:.0f}% - high confidence)",
            ))
        
        # Determine overall validity
        has_errors = any(i.severity == "error" for i in issues)
        
        return ValidationResult(
            is_valid=not has_errors,
            issues=issues,
            stats={
                "total": stats.total_questions,
                "locked": stats.locked_questions,
                "tier_counts": stats.tier_counts,
                "tier_percentages": stats.tier_percentages,
                "category_counts": stats.category_counts,
            },
        )
    
    def _check_category_coverage(
        self,
        category_counts: dict[str, int],
    ) -> list[ValidationIssue]:
        """Check that all categories are represented with minimum counts."""
        issues = []
        
        for cat_id in CATEGORIES.keys():
            count = category_counts.get(cat_id, 0)
            target = QUESTION_TARGETS.get(cat_id, {})
            min_count = target.get("min", self.min_questions_per_category)
            
            if count == 0:
                issues.append(ValidationIssue(
                    severity="error",
                    category="coverage",
                    message=f"Category {cat_id} ({CATEGORIES[cat_id].name}) has no questions",
                ))
            elif count < min_count:
                issues.append(ValidationIssue(
                    severity="warning",
                    category="coverage",
                    message=f"Category {cat_id} ({CATEGORIES[cat_id].name}) has {count} questions (target: {min_count}+)",
                ))
        
        # Check for all categories present
        present = sum(1 for c in CATEGORIES.keys() if category_counts.get(c, 0) > 0)
        if present == 19:
            issues.append(ValidationIssue(
                severity="info",
                category="coverage",
                message="All 19 categories represented",
            ))
        
        return issues
    
    def _check_tier_distribution(
        self,
        tier_percentages: dict[int, float],
    ) -> list[ValidationIssue]:
        """Check tier distribution matches 70/20/10 target."""
        issues = []
        
        targets = {1: 70.0, 2: 20.0, 3: 10.0}
        
        all_good = True
        for tier, target in targets.items():
            actual = tier_percentages.get(tier, 0)
            diff = abs(actual - target)
            
            if diff > self.tier_tolerance:
                issues.append(ValidationIssue(
                    severity="error",
                    category="distribution",
                    message=f"Tier {tier} is {actual:.1f}% (target: {target}%, tolerance: ±{self.tier_tolerance}%)",
                ))
                all_good = False
        
        if all_good:
            issues.append(ValidationIssue(
                severity="info",
                category="distribution",
                message=f"Tier distribution meets 70/20/10 target (±{self.tier_tolerance}%)",
            ))
        
        return issues
    
    def _check_capability_willingness_balance(
        self,
        capability_only: int,
        willingness_only: int,
        both: int,
        total: int,
    ) -> list[ValidationIssue]:
        """Check capability vs willingness balance."""
        issues = []
        
        if total == 0:
            return issues
        
        # We want a mix of all three types
        if capability_only == 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="balance",
                message="No capability-only questions (tests_capability=true, tests_willingness=false)",
            ))
        
        if willingness_only == 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="balance",
                message="No willingness-only questions (tests_capability=false, tests_willingness=true)",
            ))
        
        if both == 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="balance",
                message="No combined questions (tests_capability=true, tests_willingness=true)",
            ))
        
        # Check that at least one flag is set for all
        neither = total - capability_only - willingness_only - both
        if neither > 0:
            issues.append(ValidationIssue(
                severity="warning",
                category="balance",
                message=f"{neither} questions have neither capability nor willingness flag set",
            ))
        
        if capability_only > 0 and willingness_only > 0 and both > 0:
            issues.append(ValidationIssue(
                severity="info",
                category="balance",
                message=f"Capability/willingness balance: {capability_only} cap-only, {willingness_only} wil-only, {both} both",
            ))
        
        return issues
    
    def _check_metadata_coverage(
        self,
        questions: list,
    ) -> list[ValidationIssue]:
        """Check metadata coverage."""
        issues = []
        
        if not questions:
            return issues
        
        total = len(questions)
        
        # Check use_case_tags
        has_tags = sum(1 for q in questions if q.use_case_tags)
        tags_pct = has_tags / total
        
        if tags_pct < self.min_metadata_coverage:
            issues.append(ValidationIssue(
                severity="warning",
                category="metadata",
                message=f"use_case_tags coverage: {tags_pct:.0%} (target: {self.min_metadata_coverage:.0%})",
            ))
        else:
            issues.append(ValidationIssue(
                severity="info",
                category="metadata",
                message=f"use_case_tags: {tags_pct:.0%} coverage",
            ))
        
        # Check audience_context
        has_audience = sum(1 for q in questions if q.audience_context)
        audience_pct = has_audience / total
        
        issues.append(ValidationIssue(
            severity="info" if audience_pct >= 0.5 else "warning",
            category="metadata",
            message=f"audience_context: {audience_pct:.0%} specified",
        ))
        
        # Check ministry_type
        has_ministry = sum(1 for q in questions if q.ministry_type)
        ministry_pct = has_ministry / total
        
        issues.append(ValidationIssue(
            severity="info" if ministry_pct >= 0.5 else "warning",
            category="metadata",
            message=f"ministry_type: {ministry_pct:.0%} specified",
        ))
        
        return issues
    
    def _check_refusal_types(
        self,
        questions: list,
    ) -> list[ValidationIssue]:
        """Check that refusal types are set for negative verdicts."""
        issues = []
        
        negative_verdicts = {"REFUSED", "DISLOYAL", "DENIED"}
        
        missing_refusal = []
        for q in questions:
            if q.expected_verdict in negative_verdicts and not q.expected_refusal_type:
                missing_refusal.append(q.id)
        
        if missing_refusal:
            issues.append(ValidationIssue(
                severity="warning",
                category="refusal",
                message=f"{len(missing_refusal)} questions with negative verdicts missing refusal type",
                details=f"Question IDs: {missing_refusal[:10]}{'...' if len(missing_refusal) > 10 else ''}",
            ))
        else:
            refusal_count = sum(1 for q in questions if q.expected_verdict in negative_verdicts)
            if refusal_count > 0:
                issues.append(ValidationIssue(
                    severity="info",
                    category="refusal",
                    message=f"All {refusal_count} negative verdict questions have refusal types set",
                ))
        
        return issues
    
    def _check_duplicates(
        self,
        questions: list,
    ) -> list[ValidationIssue]:
        """Check for duplicate questions."""
        issues = []
        
        seen_content = {}
        duplicates = []
        
        for q in questions:
            content_key = q.content.strip().lower()
            if content_key in seen_content:
                duplicates.append((seen_content[content_key], q.id))
            else:
                seen_content[content_key] = q.id
        
        if duplicates:
            issues.append(ValidationIssue(
                severity="error",
                category="duplicates",
                message=f"{len(duplicates)} duplicate questions found",
                details=f"Pairs: {duplicates[:5]}{'...' if len(duplicates) > 5 else ''}",
            ))
        else:
            issues.append(ValidationIssue(
                severity="info",
                category="duplicates",
                message="No duplicate questions",
            ))
        
        return issues


def validate_version(version_id: int) -> ValidationResult:
    """Convenience function to validate a version."""
    validator = VersionValidator()
    return validator.validate(version_id)
