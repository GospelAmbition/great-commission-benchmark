"""
Version builder for GCB Builder.

Assembles questions into benchmark versions:
- Question selection and assembly
- Tier distribution validation
- Category coverage checking
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select

from gcb_builder.core.categories import (
    CATEGORIES,
    QUESTION_TARGETS,
    TIER_WEIGHTS,
    get_categories_by_tier,
)
from gcb_builder.core.database import get_db
from gcb_builder.core.models import BenchmarkVersion, Question, VersionQuestion


@dataclass
class VersionStats:
    """Statistics about a version."""
    
    total_questions: int
    locked_questions: int
    tier_counts: dict[int, int]
    tier_percentages: dict[int, float]
    category_counts: dict[str, int]
    capability_only: int
    willingness_only: int
    both: int
    meets_distribution: bool


class VersionBuilder:
    """
    Builds benchmark versions from approved questions.
    
    Usage:
        builder = VersionBuilder()
        version = builder.create_version("1.0.0", "Initial Release")
        builder.add_locked_questions(version.id)
        stats = builder.get_version_stats(version.id)
    """
    
    def create_version(
        self,
        version_number: str,
        name: str,
        description: Optional[str] = None,
    ) -> BenchmarkVersion:
        """
        Create a new benchmark version.
        
        Args:
            version_number: Semantic version (e.g., "1.0.0")
            name: Human-readable name
            description: Optional description
            
        Returns:
            Created BenchmarkVersion
        """
        with get_db() as db:
            # Check for duplicate version
            existing = db.scalar(
                select(BenchmarkVersion).where(
                    BenchmarkVersion.version == version_number
                )
            )
            if existing:
                raise ValueError(f"Version {version_number} already exists")
            
            version = BenchmarkVersion(
                version=version_number,
                name=name,
                description=description,
                status="building",
            )
            db.add(version)
            db.commit()
            version_id = version.id
        
        # Return fresh copy
        with get_db() as db:
            result = db.get(BenchmarkVersion, version_id)
            from sqlalchemy.orm import make_transient
            make_transient(result)
            _ = result.id, result.version, result.name, result.status
            return result
    
    def get_version(self, version_id: int) -> Optional[BenchmarkVersion]:
        """Get a version by ID."""
        with get_db() as db:
            result = db.get(BenchmarkVersion, version_id)
            if result:
                from sqlalchemy.orm import make_transient
                make_transient(result)
                _ = result.id, result.version, result.name, result.status
            return result
    
    def get_version_by_number(self, version_number: str) -> Optional[BenchmarkVersion]:
        """Get a version by its version number."""
        with get_db() as db:
            result = db.scalar(
                select(BenchmarkVersion).where(
                    BenchmarkVersion.version == version_number
                )
            )
            if result:
                from sqlalchemy.orm import make_transient
                make_transient(result)
                _ = result.id, result.version, result.name, result.status
            return result
    
    def list_versions(self) -> list[BenchmarkVersion]:
        """List all versions."""
        with get_db() as db:
            results = list(db.scalars(
                select(BenchmarkVersion).order_by(BenchmarkVersion.created_at.desc())
            ).all())
            
            from sqlalchemy.orm import make_transient
            for v in results:
                make_transient(v)
                _ = v.id, v.version, v.name, v.status
            
            return results
    
    def add_question(self, version_id: int, question_id: int) -> bool:
        """
        Add a question to a version.
        
        Args:
            version_id: Version ID
            question_id: Question ID
            
        Returns:
            True if added, False if already exists or error
        """
        with get_db() as db:
            version = db.get(BenchmarkVersion, version_id)
            if not version or version.status not in ("building", "validating"):
                return False
            
            question = db.get(Question, question_id)
            if not question or question.status != "approved":
                return False
            
            # Check if already added
            existing = db.scalar(
                select(VersionQuestion).where(
                    VersionQuestion.version_id == version_id,
                    VersionQuestion.question_id == question_id,
                )
            )
            if existing:
                return False
            
            # Get next order
            max_order = db.scalar(
                select(func.max(VersionQuestion.order)).where(
                    VersionQuestion.version_id == version_id
                )
            ) or 0
            
            link = VersionQuestion(
                version_id=version_id,
                question_id=question_id,
                order=max_order + 1,
            )
            db.add(link)
            db.commit()
            return True
    
    def remove_question(self, version_id: int, question_id: int) -> bool:
        """Remove a question from a version."""
        with get_db() as db:
            version = db.get(BenchmarkVersion, version_id)
            if not version or version.status not in ("building", "validating"):
                return False
            
            link = db.scalar(
                select(VersionQuestion).where(
                    VersionQuestion.version_id == version_id,
                    VersionQuestion.question_id == question_id,
                )
            )
            if link:
                db.delete(link)
                db.commit()
                return True
            return False
    
    def add_locked_questions(self, version_id: int) -> int:
        """
        Add all locked questions to a version.
        
        Returns:
            Number of questions added
        """
        with get_db() as db:
            version = db.get(BenchmarkVersion, version_id)
            if not version or version.status not in ("building", "validating"):
                return 0
            
            # Get locked, approved questions not already in version
            locked_questions = db.scalars(
                select(Question).where(
                    Question.locked == True,
                    Question.status == "approved",
                )
            ).all()
            
            existing_ids = set(db.scalars(
                select(VersionQuestion.question_id).where(
                    VersionQuestion.version_id == version_id
                )
            ).all())
            
            # Get starting order
            max_order = db.scalar(
                select(func.max(VersionQuestion.order)).where(
                    VersionQuestion.version_id == version_id
                )
            ) or 0
            
            added = 0
            for q in locked_questions:
                if q.id not in existing_ids:
                    max_order += 1
                    link = VersionQuestion(
                        version_id=version_id,
                        question_id=q.id,
                        order=max_order,
                    )
                    db.add(link)
                    added += 1
            
            db.commit()
            return added
    
    def add_approved_questions(self, version_id: int) -> int:
        """
        Add all approved questions to a version.
        
        Returns:
            Number of questions added
        """
        with get_db() as db:
            version = db.get(BenchmarkVersion, version_id)
            if not version or version.status not in ("building", "validating"):
                return 0
            
            approved_questions = db.scalars(
                select(Question).where(Question.status == "approved")
            ).all()
            
            existing_ids = set(db.scalars(
                select(VersionQuestion.question_id).where(
                    VersionQuestion.version_id == version_id
                )
            ).all())
            
            max_order = db.scalar(
                select(func.max(VersionQuestion.order)).where(
                    VersionQuestion.version_id == version_id
                )
            ) or 0
            
            added = 0
            for q in approved_questions:
                if q.id not in existing_ids:
                    max_order += 1
                    link = VersionQuestion(
                        version_id=version_id,
                        question_id=q.id,
                        order=max_order,
                    )
                    db.add(link)
                    added += 1
            
            db.commit()
            return added
    
    def add_questions_by_category(
        self,
        version_id: int,
        category_id: str,
        limit: Optional[int] = None,
    ) -> int:
        """
        Add approved questions from a specific category.
        
        Args:
            version_id: Version ID
            category_id: Category ID (e.g., "3.2")
            limit: Maximum questions to add
            
        Returns:
            Number of questions added
        """
        with get_db() as db:
            version = db.get(BenchmarkVersion, version_id)
            if not version or version.status not in ("building", "validating"):
                return 0
            
            query = select(Question).where(
                Question.status == "approved",
                Question.category == category_id,
            )
            
            if limit:
                query = query.limit(limit)
            
            questions = db.scalars(query).all()
            
            existing_ids = set(db.scalars(
                select(VersionQuestion.question_id).where(
                    VersionQuestion.version_id == version_id
                )
            ).all())
            
            max_order = db.scalar(
                select(func.max(VersionQuestion.order)).where(
                    VersionQuestion.version_id == version_id
                )
            ) or 0
            
            added = 0
            for q in questions:
                if q.id not in existing_ids:
                    max_order += 1
                    link = VersionQuestion(
                        version_id=version_id,
                        question_id=q.id,
                        order=max_order,
                    )
                    db.add(link)
                    added += 1
            
            db.commit()
            return added
    
    def get_version_questions(self, version_id: int) -> list[Question]:
        """Get all questions in a version."""
        with get_db() as db:
            links = db.scalars(
                select(VersionQuestion).where(
                    VersionQuestion.version_id == version_id
                ).order_by(VersionQuestion.order)
            ).all()
            
            questions = []
            from sqlalchemy.orm import make_transient
            for link in links:
                q = db.get(Question, link.question_id)
                if q:
                    make_transient(q)
                    _ = q.id, q.content, q.category, q.tier
                    questions.append(q)
            
            return questions
    
    def get_version_stats(self, version_id: int) -> VersionStats:
        """Get statistics for a version."""
        questions = self.get_version_questions(version_id)
        
        total = len(questions)
        locked = sum(1 for q in questions if q.locked)
        
        # Tier counts
        tier_counts = {1: 0, 2: 0, 3: 0}
        for q in questions:
            tier_counts[q.tier] = tier_counts.get(q.tier, 0) + 1
        
        # Tier percentages
        tier_percentages = {}
        for tier, count in tier_counts.items():
            tier_percentages[tier] = (count / total * 100) if total > 0 else 0.0
        
        # Category counts
        category_counts = {}
        for q in questions:
            category_counts[q.category] = category_counts.get(q.category, 0) + 1
        
        # Capability vs willingness
        capability_only = sum(
            1 for q in questions
            if q.tests_capability and not q.tests_willingness
        )
        willingness_only = sum(
            1 for q in questions
            if q.tests_willingness and not q.tests_capability
        )
        both = sum(
            1 for q in questions
            if q.tests_capability and q.tests_willingness
        )
        
        # Check distribution (70/20/10 target)
        meets_distribution = (
            total >= 30 and
            abs(tier_percentages.get(1, 0) - 70) <= 5 and
            abs(tier_percentages.get(2, 0) - 20) <= 5 and
            abs(tier_percentages.get(3, 0) - 10) <= 5
        )
        
        return VersionStats(
            total_questions=total,
            locked_questions=locked,
            tier_counts=tier_counts,
            tier_percentages=tier_percentages,
            category_counts=category_counts,
            capability_only=capability_only,
            willingness_only=willingness_only,
            both=both,
            meets_distribution=meets_distribution,
        )
    
    def update_status(self, version_id: int, new_status: str) -> bool:
        """Update a version's status."""
        valid_statuses = {"building", "validating", "locked", "published"}
        if new_status not in valid_statuses:
            return False
        
        with get_db() as db:
            version = db.get(BenchmarkVersion, version_id)
            if not version:
                return False
            
            # Validate transitions
            valid_transitions = {
                "building": {"validating"},
                "validating": {"building", "locked"},
                "locked": {"published"},
                "published": set(),  # No transitions from published
            }
            
            if new_status not in valid_transitions.get(version.status, set()):
                return False
            
            version.status = new_status
            
            if new_status == "locked":
                version.locked_at = datetime.utcnow()
            elif new_status == "published":
                version.published_at = datetime.utcnow()
            
            db.commit()
            return True
    
    def delete_version(self, version_id: int) -> bool:
        """Delete a version (only if building or validating)."""
        with get_db() as db:
            version = db.get(BenchmarkVersion, version_id)
            if not version:
                return False
            
            if version.status not in ("building", "validating"):
                return False
            
            # Delete question links first
            links = db.scalars(
                select(VersionQuestion).where(
                    VersionQuestion.version_id == version_id
                )
            ).all()
            for link in links:
                db.delete(link)
            
            db.delete(version)
            db.commit()
            return True
