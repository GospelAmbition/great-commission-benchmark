"""
Shared question and question set management service.

This module contains the core business logic for managing questions
and question sets, used by both admin and benchmark_developer endpoints.
"""
import logging
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)

from app.db.models.question import Question
from app.db.models.question_set import QuestionSet
from app.db.models.test_run import TestRun
from app.core.benchmark_config import (
    TIER_PERCENTAGES,
    DIFFICULTY_PERCENTAGES,
    BALANCE_TOLERANCE,
    CATEGORY_WEIGHTS,
    calculate_targets,
)
from app.schemas.admin import (
    QuestionSetStatsResponse,
    CategoryStats,
    TierStats,
    DifficultyStats,
    DifficultyCount,
    CategoryDifficultyBreakdown,
)


class QuestionManagementService:
    """Service for managing questions and question sets."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Question Set Operations
    # =========================================================================
    
    def list_question_sets(
        self,
        status: Optional[str] = None,
        include_question_count: bool = False
    ) -> Dict[str, Any]:
        """List all question sets with optional filtering."""
        query = self.db.query(QuestionSet)
        
        if status:
            query = query.filter(QuestionSet.status == status)
        
        question_sets = query.order_by(QuestionSet.created_at.desc()).all()
        
        items = []
        for qs in question_sets:
            item = {
                "id": str(qs.id),
                "semantic_version": qs.semantic_version,
                "marketing_version": qs.marketing_version,
                "status": qs.status,
                "created_at": qs.created_at.isoformat() if qs.created_at else None,
                "locked_at": qs.locked_at.isoformat() if qs.locked_at else None,
                "archived_at": qs.archived_at.isoformat() if qs.archived_at else None,
            }
            
            if include_question_count:
                question_count = self.db.query(Question).filter(
                    Question.question_set_id == qs.id
                ).count()
                item["question_count"] = question_count
                item["target_question_count"] = qs.target_question_count
            
            items.append(item)
        
        return {
            "items": items,
            "total": len(question_sets)
        }
    
    def create_question_set(
        self,
        semantic_version: str,
        marketing_version: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new empty question set."""
        # Check if version already exists
        existing = self.db.query(QuestionSet).filter(
            QuestionSet.semantic_version == semantic_version
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Question set with version {semantic_version} already exists"
            )
        
        question_set = QuestionSet(
            semantic_version=semantic_version,
            marketing_version=marketing_version,
            status="draft",
            notes=notes
        )
        self.db.add(question_set)
        self.db.commit()
        self.db.refresh(question_set)
        
        return {
            "id": str(question_set.id),
            "semantic_version": question_set.semantic_version,
            "marketing_version": question_set.marketing_version,
            "status": question_set.status,
            "created_at": question_set.created_at.isoformat() if question_set.created_at else None,
        }
    
    def get_question_set(self, question_set_id: UUID) -> QuestionSet:
        """Get a question set by ID, raises 404 if not found."""
        question_set = self.db.query(QuestionSet).filter(
            QuestionSet.id == question_set_id
        ).first()
        
        if not question_set:
            raise HTTPException(status_code=404, detail="Question set not found")
        
        return question_set
    
    def delete_question_set(self, question_set_id: UUID) -> Dict[str, Any]:
        """Delete a question set and all its questions.
        
        Deletion rules:
        - Active versions cannot be deleted (must archive first)
        - Locked draft versions cannot be deleted (must unlock first)
        - Archived versions can be deleted if they have no test runs
        - Versions with test runs cannot be deleted (to preserve historical data)
        """
        question_set = self.get_question_set(question_set_id)
        
        # Prevent deleting active/published versions
        if question_set.status == "active":
            raise HTTPException(
                status_code=400,
                detail="Cannot delete an active version. Archive it first."
            )
        
        # Prevent deleting locked draft versions (but allow archived versions even if they were locked)
        if question_set.locked_at is not None and question_set.status != "archived":
            raise HTTPException(
                status_code=400,
                detail="Cannot delete a locked version. Unlock it first or archive it."
            )
        
        # Check if any test runs exist for this question set
        test_run_count = self.db.query(TestRun).filter(
            TestRun.question_set_id == question_set_id
        ).count()
        
        if test_run_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete version {question_set.semantic_version}: {test_run_count} test run(s) exist for this version. Historical test data must be preserved."
            )
        
        try:
            # Delete all questions first
            deleted_questions = self.db.query(Question).filter(
                Question.question_set_id == question_set_id
            ).delete(synchronize_session=False)
            
            version = question_set.semantic_version
            self.db.delete(question_set)
            self.db.commit()
            
            return {
                "message": f"Question set {version} deleted",
                "deleted_questions": deleted_questions
            }
        except Exception as e:
            # Rollback on any error
            self.db.rollback()
            # Re-raise HTTPException as-is, but wrap other exceptions
            if isinstance(e, HTTPException):
                raise
            # Log the error and raise a more user-friendly message
            logger.error(f"Error deleting question set {question_set_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete question set: {str(e)}"
            )
    
    def empty_question_set(self, question_set_id: UUID) -> Dict[str, Any]:
        """Remove all questions from a question set."""
        question_set = self.get_question_set(question_set_id)
        
        if question_set.status == "active":
            raise HTTPException(
                status_code=400,
                detail="Cannot empty an active version"
            )
        
        if question_set.locked_at is not None:
            raise HTTPException(
                status_code=400,
                detail="Cannot empty a locked version"
            )
        
        deleted_count = self.db.query(Question).filter(
            Question.question_set_id == question_set_id
        ).delete(synchronize_session=False)
        
        self.db.commit()
        
        return {
            "message": f"Removed all questions from version {question_set.semantic_version}",
            "deleted_questions": deleted_count
        }
    
    def get_question_set_stats(self, question_set_id: UUID) -> QuestionSetStatsResponse:
        """Get statistics for a question set."""
        question_set = self.get_question_set(question_set_id)
        
        questions = self.db.query(Question).filter(
            Question.question_set_id == question_set_id
        ).all()
        
        # Count by tier, category, and difficulty
        tier_counts = {1: 0, 2: 0, 3: 0}
        category_counts = {1: {}, 2: {}, 3: {}}
        difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
        category_difficulty = {}
        
        for q in questions:
            tier = q.tier
            category = q.category
            
            # Get difficulty from metadata
            difficulty = ""
            if q.question_metadata and isinstance(q.question_metadata, dict):
                difficulty = q.question_metadata.get("difficulty", "").lower()
                if difficulty in difficulty_counts:
                    difficulty_counts[difficulty] += 1
            
            if tier is None or category is None:
                continue
            
            if tier not in [1, 2, 3]:
                continue
            
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            if category not in category_counts[tier]:
                category_counts[tier][category] = 0
            category_counts[tier][category] += 1
            
            if category not in category_difficulty:
                category_difficulty[category] = {"easy": 0, "medium": 0, "hard": 0}
            if difficulty in category_difficulty[category]:
                category_difficulty[category][difficulty] += 1
        
        total_questions = len(questions)
        target_is_auto = question_set.target_question_count is None
        target_total = question_set.target_question_count if question_set.target_question_count else total_questions
        targets = calculate_targets(target_total)
        
        # Build tier stats
        tier_stats = {}
        for tier in [1, 2, 3]:
            categories_dict = {}
            for category, weight in CATEGORY_WEIGHTS[tier].items():
                count = category_counts[tier].get(category, 0)
                target = targets["category_targets"][tier].get(category, 0)
                cat_diff = category_difficulty.get(category, {"easy": 0, "medium": 0, "hard": 0})
                categories_dict[category] = CategoryStats(
                    count=count,
                    target=target,
                    difficulty=CategoryDifficultyBreakdown(
                        easy=cat_diff["easy"],
                        medium=cat_diff["medium"],
                        hard=cat_diff["hard"]
                    )
                )
            
            tier_stats[tier] = TierStats(
                count=tier_counts[tier],
                target=targets["tier_targets"][tier],
                categories=categories_dict
            )
        
        # Build difficulty stats
        difficulty_stats = DifficultyStats(
            easy=DifficultyCount(
                count=difficulty_counts["easy"],
                percentage=round((difficulty_counts["easy"] / total_questions * 100) if total_questions > 0 else 0, 1)
            ),
            medium=DifficultyCount(
                count=difficulty_counts["medium"],
                percentage=round((difficulty_counts["medium"] / total_questions * 100) if total_questions > 0 else 0, 1)
            ),
            hard=DifficultyCount(
                count=difficulty_counts["hard"],
                percentage=round((difficulty_counts["hard"] / total_questions * 100) if total_questions > 0 else 0, 1)
            )
        )
        
        # Build category difficulty matrix
        category_difficulty_matrix = {}
        for tier in [1, 2, 3]:
            for category in CATEGORY_WEIGHTS[tier].keys():
                cat_diff = category_difficulty.get(category, {"easy": 0, "medium": 0, "hard": 0})
                category_difficulty_matrix[category] = CategoryDifficultyBreakdown(
                    easy=cat_diff["easy"],
                    medium=cat_diff["medium"],
                    hard=cat_diff["hard"]
                )
        
        return QuestionSetStatsResponse(
            question_set_id=question_set.id,
            semantic_version=question_set.semantic_version,
            marketing_version=question_set.marketing_version,
            total_questions=total_questions,
            target_total=target_total,
            target_is_auto=target_is_auto,
            tier_stats=tier_stats,
            difficulty_stats=difficulty_stats,
            category_difficulty_matrix=category_difficulty_matrix
        )
    
    def copy_question_set(
        self,
        source_question_set_id: UUID,
        new_semantic_version: str,
        new_marketing_version: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Copy a question set to create a new version."""
        source = self.get_question_set(source_question_set_id)
        
        # Check if version already exists
        existing = self.db.query(QuestionSet).filter(
            QuestionSet.semantic_version == new_semantic_version
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Question set with version {new_semantic_version} already exists"
            )
        
        source_questions = self.db.query(Question).filter(
            Question.question_set_id == source_question_set_id
        ).all()
        
        new_question_set = QuestionSet(
            semantic_version=new_semantic_version,
            marketing_version=new_marketing_version,
            status="draft",
            notes=notes
        )
        self.db.add(new_question_set)
        self.db.flush()
        
        copied_count = 0
        for source_q in source_questions:
            new_question = Question(
                question_set_id=new_question_set.id,
                tier=source_q.tier,
                category=source_q.category,
                content=source_q.content,
                subcategory=source_q.subcategory,
                expected_verdict=source_q.expected_verdict,
                question_metadata=source_q.question_metadata,
                notes=source_q.notes
            )
            self.db.add(new_question)
            copied_count += 1
        
        self.db.commit()
        self.db.refresh(new_question_set)
        
        return {
            "id": str(new_question_set.id),
            "semantic_version": new_question_set.semantic_version,
            "marketing_version": new_question_set.marketing_version,
            "status": new_question_set.status,
            "created_at": new_question_set.created_at.isoformat() if new_question_set.created_at else None,
            "questions_copied": copied_count
        }
    
    def lock_question_set(self, question_set_id: UUID) -> Dict[str, Any]:
        """Lock a question set to prevent further editing."""
        question_set = self.get_question_set(question_set_id)
        
        if question_set.status != "draft":
            raise HTTPException(
                status_code=400,
                detail="Only draft versions can be locked"
            )
        
        if question_set.locked_at is not None:
            raise HTTPException(
                status_code=400,
                detail="Question set is already locked"
            )
        
        question_set.locked_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(question_set)
        
        return {
            "message": f"Question set {question_set.semantic_version} locked",
            "locked_at": question_set.locked_at.isoformat()
        }
    
    def unlock_question_set(self, question_set_id: UUID) -> Dict[str, Any]:
        """Unlock a question set to allow editing again."""
        question_set = self.get_question_set(question_set_id)
        
        if question_set.locked_at is None:
            raise HTTPException(
                status_code=400,
                detail="Question set is not locked"
            )
        
        if question_set.status == "active":
            raise HTTPException(
                status_code=400,
                detail="Cannot unlock an active version"
            )
        
        question_set.locked_at = None
        self.db.commit()
        self.db.refresh(question_set)
        
        return {
            "message": f"Question set {question_set.semantic_version} unlocked"
        }
    
    def archive_question_set(self, question_set_id: UUID) -> Dict[str, Any]:
        """Archive a question set."""
        question_set = self.get_question_set(question_set_id)
        
        if question_set.status == "archived":
            raise HTTPException(
                status_code=400,
                detail="Question set is already archived"
            )
        
        question_set.status = "archived"
        question_set.archived_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(question_set)
        
        return {
            "message": f"Question set {question_set.semantic_version} archived",
            "archived_at": question_set.archived_at.isoformat()
        }
    
    def update_question_set_target(
        self,
        question_set_id: UUID,
        target_question_count: Optional[int]
    ) -> Dict[str, Any]:
        """Update the target question count for a question set."""
        question_set = self.get_question_set(question_set_id)
        
        if question_set.locked_at is not None:
            raise HTTPException(
                status_code=400,
                detail="Cannot update target for a locked question set"
            )
        
        question_set.target_question_count = target_question_count
        self.db.commit()
        self.db.refresh(question_set)
        
        return {
            "question_set_id": str(question_set.id),
            "target_question_count": question_set.target_question_count
        }
    
    # =========================================================================
    # Question Operations
    # =========================================================================
    
    def list_questions(
        self,
        question_set_id: Optional[UUID] = None,
        tier: Optional[int] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List questions with filtering."""
        base_query = self.db.query(Question)
        
        if question_set_id:
            base_query = base_query.filter(Question.question_set_id == question_set_id)
        if tier:
            base_query = base_query.filter(Question.tier == tier)
        if category:
            base_query = base_query.filter(Question.category == category)
        
        total = base_query.count()
        
        query = base_query.options(joinedload(Question.question_set)).order_by(
            Question.tier, Question.category
        )
        questions = query.offset(offset).limit(limit).all()
        
        items = []
        for q in questions:
            is_locked = False
            if q.question_set:
                is_locked = q.question_set.locked_at is not None
            
            metadata = None
            if hasattr(q, 'question_metadata') and q.question_metadata:
                metadata = q.question_metadata if isinstance(q.question_metadata, dict) else None
            
            items.append({
                "id": str(q.id),
                "question_set_id": str(q.question_set_id),
                "tier": q.tier,
                "category": q.category,
                "content": q.content,
                "metadata": metadata,
                "expected_verdict": q.expected_verdict,
                "is_locked": is_locked,
                "notes": q.notes
            })
        
        return {
            "items": items,
            "total": total
        }
    
    def get_question(self, question_id: UUID) -> Tuple[Question, bool]:
        """Get a question by ID with its lock status."""
        question = self.db.query(Question).options(
            joinedload(Question.question_set)
        ).filter(Question.id == question_id).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        is_locked = False
        if question.question_set:
            is_locked = question.question_set.locked_at is not None
        
        return question, is_locked
    
    def create_question(
        self,
        question_set_id: UUID,
        tier: int,
        category: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        expected_verdict: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[Question, bool]:
        """Create a new question."""
        question_set = self.get_question_set(question_set_id)
        
        if question_set.locked_at is not None:
            raise HTTPException(
                status_code=400,
                detail="Cannot add questions to a locked question set"
            )
        
        clean_metadata = None
        if metadata and isinstance(metadata, dict) and "difficulty" in metadata:
            clean_metadata = {"difficulty": metadata["difficulty"]}
        
        question = Question(
            question_set_id=question_set_id,
            tier=tier,
            category=category,
            content=content,
            expected_verdict=expected_verdict,
            question_metadata=clean_metadata,
            notes=notes
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        
        return question, False
    
    def update_question(
        self,
        question_id: UUID,
        tier: Optional[int] = None,
        category: Optional[str] = None,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expected_verdict: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[Question, bool]:
        """Update a question."""
        question, is_locked = self.get_question(question_id)
        
        if is_locked:
            raise HTTPException(status_code=400, detail="Question set is locked")
        
        if tier is not None:
            question.tier = tier
        if category is not None:
            question.category = category
        if content is not None:
            question.content = content
        if metadata is not None:
            if isinstance(metadata, dict) and "difficulty" in metadata:
                question.question_metadata = {"difficulty": metadata["difficulty"]}
            else:
                question.question_metadata = None
        if expected_verdict is not None:
            question.expected_verdict = expected_verdict
        if notes is not None:
            question.notes = notes
        
        self.db.commit()
        self.db.refresh(question)
        
        # Re-check lock status after refresh
        is_locked = False
        if question.question_set:
            is_locked = question.question_set.locked_at is not None
        
        return question, is_locked
    
    def delete_question(self, question_id: UUID) -> Dict[str, str]:
        """Delete a question."""
        question, is_locked = self.get_question(question_id)
        
        if is_locked:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete question from locked question set"
            )
        
        self.db.delete(question)
        self.db.commit()
        
        return {"message": "Question deleted"}
    
    def import_questions(
        self,
        questions: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Import multiple questions."""
        imported = 0
        errors = []
        
        if dry_run:
            for idx, q_data in enumerate(questions):
                try:
                    question_set_id = q_data.get("question_set_id")
                    tier = q_data.get("tier")
                    category = q_data.get("category")
                    content = q_data.get("content")
                    
                    if not all([question_set_id, tier, category, content]):
                        errors.append(f"Question {idx}: missing required fields")
                        continue
                    
                    question_set = self.db.query(QuestionSet).filter(
                        QuestionSet.id == question_set_id
                    ).first()
                    if not question_set:
                        errors.append(f"Question {idx}: question_set_id not found")
                        continue
                    
                    if question_set.locked_at is not None:
                        errors.append(f"Question {idx}: question set is locked")
                        continue
                    
                    imported += 1
                except Exception as e:
                    errors.append(f"Question {idx}: {str(e)}")
        else:
            for idx, q_data in enumerate(questions):
                try:
                    question_set_id = q_data.get("question_set_id")
                    tier = q_data.get("tier")
                    category = q_data.get("category")
                    content = q_data.get("content")
                    metadata = q_data.get("metadata")
                    
                    if not all([question_set_id, tier, category, content]):
                        errors.append(f"Question {idx}: missing required fields")
                        continue
                    
                    question_set = self.db.query(QuestionSet).filter(
                        QuestionSet.id == question_set_id
                    ).first()
                    if not question_set:
                        errors.append(f"Question {idx}: question_set_id not found")
                        continue
                    
                    if question_set.locked_at is not None:
                        errors.append(f"Question {idx}: question set is locked")
                        continue
                    
                    expected_verdict = None
                    clean_metadata = None
                    if metadata and isinstance(metadata, dict):
                        expected_verdict = metadata.get("expected_verdict")
                        if "difficulty" in metadata:
                            clean_metadata = {"difficulty": metadata["difficulty"]}
                    
                    notes = q_data.get("notes")
                    
                    question = Question(
                        question_set_id=question_set_id,
                        tier=tier,
                        category=category,
                        content=content,
                        expected_verdict=expected_verdict,
                        question_metadata=clean_metadata,
                        notes=notes
                    )
                    self.db.add(question)
                    imported += 1
                except Exception as e:
                    errors.append(f"Question {idx}: {str(e)}")
            
            if imported > 0:
                self.db.commit()
        
        return {
            "imported": imported,
            "errors": errors,
            "dry_run": dry_run
        }

