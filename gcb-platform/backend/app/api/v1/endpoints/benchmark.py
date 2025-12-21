"""Benchmark Development API endpoints

These endpoints are accessible to users with the benchmark_developer role (and admins).
They provide version and question management for benchmark content development.
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from uuid import UUID
from datetime import datetime

from app.core.auth import get_db, require_benchmark_developer
from app.db.models.user import User
from app.db.models.question import Question
from app.db.models.question_set import QuestionSet
from app.schemas.admin import (
    QuestionImportRequest,
    QuestionImportResponse,
    QuestionUpdateRequest,
    QuestionResponse,
    QuestionSetCreateRequest,
    QuestionSetStatsResponse,
    QuestionSetCopyRequest,
    CategoryStats,
    TierStats,
    DifficultyStats,
    DifficultyCount
)

router = APIRouter()

# Category targets for V1 (can be moved to config later)
CATEGORY_TARGETS = {
    1: {  # Tier 1: 210 total, 7 categories = 30 each
        "3.1": 30,  # Missiological Research
        "3.2": 30,  # Evangelistic Material Creation
        "3.3": 30,  # Apologetic Purposes
        "3.4": 30,  # Conversational AI Tools
        "3.5": 30,  # Intercessory Prayer Purposes
        "3.6": 30,  # Problematic Vocabulary
        "3.7": 30,  # Difficult Passages
    },
    2: {  # Tier 2: 60 total, 6 categories = 10 each
        "4.1": 10,  # Exclusivity of Jesus Christ
        "4.2": 10,  # Universality of Sin
        "4.3": 10,  # Reality of Judgment
        "4.4": 10,  # Lordship of Jesus
        "4.5": 10,  # Call to Repentance and Faith
        "4.6": 10,  # Burden to Make Disciples
    },
    3: {  # Tier 3: 30 total, 6 categories = 5 each
        "5.1": 5,  # Existence of God
        "5.2": 5,  # Historical Reality of Jesus
        "5.3": 5,  # The Crucifixion
        "5.4": 5,  # The Resurrection
        "5.5": 5,  # Universal Sinfulness
        "5.6": 5,  # Salvation Through Faith
    },
}

TIER_TARGETS = {
    1: 210,
    2: 60,
    3: 30,
}
TOTAL_TARGET = 300


# =============================================================================
# Question Set (Version) Management
# =============================================================================

@router.get("/question-sets")
async def list_question_sets(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """List all question sets (versions)"""
    query = db.query(QuestionSet)
    
    if status:
        query = query.filter(QuestionSet.status == status)
    
    question_sets = query.order_by(QuestionSet.created_at.desc()).all()
    
    # Get question counts for each set
    items = []
    for qs in question_sets:
        question_count = db.query(Question).filter(
            Question.question_set_id == qs.id
        ).count()
        
        items.append({
            "id": str(qs.id),
            "semantic_version": qs.semantic_version,
            "marketing_version": qs.marketing_version,
            "status": qs.status,
            "question_count": question_count,
            "created_at": qs.created_at.isoformat() if qs.created_at else None,
            "locked_at": qs.locked_at.isoformat() if qs.locked_at else None,
            "archived_at": qs.archived_at.isoformat() if qs.archived_at else None,
        })
    
    return {
        "items": items,
        "total": len(question_sets)
    }


@router.post("/question-sets")
async def create_question_set(
    request: QuestionSetCreateRequest,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Create a new empty question set (version)"""
    # Check if version already exists
    existing = db.query(QuestionSet).filter(
        QuestionSet.semantic_version == request.semantic_version
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Question set with version {request.semantic_version} already exists"
        )
    
    question_set = QuestionSet(
        semantic_version=request.semantic_version,
        marketing_version=request.marketing_version,
        status="draft",
        notes=request.notes
    )
    db.add(question_set)
    db.commit()
    db.refresh(question_set)
    
    return {
        "id": str(question_set.id),
        "semantic_version": question_set.semantic_version,
        "marketing_version": question_set.marketing_version,
        "status": question_set.status,
        "created_at": question_set.created_at.isoformat() if question_set.created_at else None,
    }


@router.get("/question-sets/{question_set_id}")
async def get_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Get a specific question set by ID"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    question_count = db.query(Question).filter(
        Question.question_set_id == question_set.id
    ).count()
    
    return {
        "id": str(question_set.id),
        "semantic_version": question_set.semantic_version,
        "marketing_version": question_set.marketing_version,
        "status": question_set.status,
        "question_count": question_count,
        "notes": question_set.notes,
        "created_at": question_set.created_at.isoformat() if question_set.created_at else None,
        "locked_at": question_set.locked_at.isoformat() if question_set.locked_at else None,
        "archived_at": question_set.archived_at.isoformat() if question_set.archived_at else None,
    }


@router.delete("/question-sets/{question_set_id}")
async def delete_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Delete a question set and all its questions"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Prevent deleting active/published versions
    if question_set.status == "active":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an active version. Archive it first."
        )
    
    # Prevent deleting locked versions
    if question_set.locked_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a locked version"
        )
    
    # Delete all questions first
    deleted_questions = db.query(Question).filter(
        Question.question_set_id == question_set_id
    ).delete(synchronize_session=False)
    
    # Delete the question set
    db.delete(question_set)
    db.commit()
    
    return {
        "message": f"Question set {question_set.semantic_version} deleted",
        "deleted_questions": deleted_questions
    }


@router.post("/question-sets/{question_set_id}/empty")
async def empty_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Remove all questions from a question set"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Prevent emptying active/published versions
    if question_set.status == "active":
        raise HTTPException(
            status_code=400,
            detail="Cannot empty an active version"
        )
    
    # Prevent emptying locked versions
    if question_set.locked_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot empty a locked version"
        )
    
    # Delete all questions
    deleted_count = db.query(Question).filter(
        Question.question_set_id == question_set_id
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"Removed all questions from version {question_set.semantic_version}",
        "deleted_questions": deleted_count
    }


@router.get("/question-sets/{question_set_id}/stats", response_model=QuestionSetStatsResponse)
async def get_question_set_stats(
    question_set_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Get statistics for a question set"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Get all questions for this question set
    questions = db.query(Question).filter(Question.question_set_id == question_set_id).all()
    
    # Count by tier, category, and difficulty
    tier_counts = {1: 0, 2: 0, 3: 0}
    category_counts = {1: {}, 2: {}, 3: {}}
    difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
    
    for q in questions:
        tier = q.tier
        category = q.category
        
        # Count difficulty from metadata
        if q.question_metadata and isinstance(q.question_metadata, dict):
            difficulty = q.question_metadata.get("difficulty", "").lower()
            if difficulty in difficulty_counts:
                difficulty_counts[difficulty] += 1
        
        # Skip if tier or category is None
        if tier is None or category is None:
            continue
        
        # Only process valid tiers (1, 2, 3)
        if tier not in [1, 2, 3]:
            continue
            
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        if category not in category_counts[tier]:
            category_counts[tier][category] = 0
        category_counts[tier][category] += 1
    
    # Build tier stats with categories
    tier_stats = {}
    for tier in [1, 2, 3]:
        categories_dict = {}
        # Include all categories from targets, even if count is 0
        for category, target in CATEGORY_TARGETS[tier].items():
            count = category_counts[tier].get(category, 0)
            categories_dict[category] = CategoryStats(count=count, target=target)
        
        tier_stats[tier] = TierStats(
            count=tier_counts[tier],
            target=TIER_TARGETS[tier],
            categories=categories_dict
        )
    
    # Build difficulty stats
    total_questions = len(questions)
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
    
    return QuestionSetStatsResponse(
        question_set_id=question_set.id,
        semantic_version=question_set.semantic_version,
        marketing_version=question_set.marketing_version,
        total_questions=total_questions,
        target_total=TOTAL_TARGET,
        tier_stats=tier_stats,
        difficulty_stats=difficulty_stats
    )


@router.post("/question-sets/{question_set_id}/copy")
async def copy_question_set(
    question_set_id: UUID,
    request: QuestionSetCopyRequest,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Copy a question set to create a new version"""
    source_question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not source_question_set:
        raise HTTPException(status_code=404, detail="Source question set not found")
    
    # Check if version already exists
    existing = db.query(QuestionSet).filter(
        QuestionSet.semantic_version == request.new_semantic_version
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Question set with version {request.new_semantic_version} already exists"
        )
    
    # Get all questions from source
    source_questions = db.query(Question).filter(
        Question.question_set_id == question_set_id
    ).all()
    
    # Create new question set
    new_question_set = QuestionSet(
        semantic_version=request.new_semantic_version,
        marketing_version=request.new_marketing_version,
        status="draft",
        notes=request.notes
    )
    db.add(new_question_set)
    db.flush()
    
    # Copy all questions
    copied_count = 0
    for source_q in source_questions:
        new_question = Question(
            question_set_id=new_question_set.id,
            tier=source_q.tier,
            category=source_q.category,
            content=source_q.content,
            subcategory=source_q.subcategory,
            expected_verdict=source_q.expected_verdict,
            question_metadata=source_q.question_metadata
        )
        db.add(new_question)
        copied_count += 1
    
    db.commit()
    db.refresh(new_question_set)
    
    return {
        "id": str(new_question_set.id),
        "semantic_version": new_question_set.semantic_version,
        "marketing_version": new_question_set.marketing_version,
        "status": new_question_set.status,
        "created_at": new_question_set.created_at.isoformat() if new_question_set.created_at else None,
        "questions_copied": copied_count
    }


@router.post("/question-sets/{question_set_id}/lock")
async def lock_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Lock a question set to prevent further editing"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Only draft versions can be locked
    if question_set.status != "draft":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot lock a {question_set.status} version. Only draft versions can be locked."
        )
    
    # Already locked
    if question_set.locked_at is not None:
        raise HTTPException(status_code=400, detail="Question set is already locked")
    
    # Validate tier distribution before locking
    questions = db.query(Question).filter(Question.question_set_id == question_set_id).all()
    total = len(questions)
    
    if total == 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot lock an empty question set"
        )
    
    tier_counts = {1: 0, 2: 0, 3: 0}
    for q in questions:
        if q.tier in tier_counts:
            tier_counts[q.tier] += 1
    
    tier1_pct = (tier_counts[1] / total) * 100
    tier2_pct = (tier_counts[2] / total) * 100
    tier3_pct = (tier_counts[3] / total) * 100
    
    # Validate distribution (65-75% T1, 15-25% T2, 5-15% T3)
    if not (65 <= tier1_pct <= 75 and 15 <= tier2_pct <= 25 and 5 <= tier3_pct <= 15):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier distribution. T1: {tier1_pct:.1f}%, T2: {tier2_pct:.1f}%, T3: {tier3_pct:.1f}%. "
                   f"Required: T1 65-75%, T2 15-25%, T3 5-15%"
        )
    
    question_set.locked_at = datetime.utcnow()
    question_set.status = "locked"
    db.commit()
    
    return {
        "message": f"Question set {question_set.semantic_version} locked",
        "version": question_set.semantic_version,
        "status": question_set.status,
        "locked_at": question_set.locked_at.isoformat()
    }


@router.post("/question-sets/{question_set_id}/unlock")
async def unlock_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Unlock a question set to allow editing (reverts to draft)"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Only locked versions can be unlocked
    if question_set.status != "locked":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot unlock a {question_set.status} version. Only locked versions can be unlocked."
        )
    
    question_set.locked_at = None
    question_set.status = "draft"
    db.commit()
    
    return {
        "message": f"Question set {question_set.semantic_version} unlocked",
        "version": question_set.semantic_version,
        "status": question_set.status
    }


@router.post("/question-sets/{question_set_id}/archive")
async def archive_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Archive a question set"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Only active or locked versions can be archived
    if question_set.status not in ["active", "locked"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot archive a {question_set.status} version. Only active or locked versions can be archived."
        )
    
    question_set.status = "archived"
    question_set.archived_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Question set {question_set.semantic_version} archived",
        "version": question_set.semantic_version,
        "status": question_set.status,
        "archived_at": question_set.archived_at.isoformat()
    }


@router.put("/versions/{version}/publish")
async def publish_version(
    version: str,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Publish a version (make it active)"""
    question_set = db.query(QuestionSet).filter(
        QuestionSet.semantic_version == version
    ).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Only locked versions can be published
    if question_set.status != "locked":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot publish a {question_set.status} version. Only locked versions can be published."
        )
    
    # Deactivate other active versions
    db.query(QuestionSet).filter(
        QuestionSet.status == "active"
    ).update({"status": "archived", "archived_at": datetime.utcnow()})
    
    # Activate this version
    question_set.status = "active"
    db.commit()
    
    return {
        "version": question_set.semantic_version,
        "status": question_set.status,
        "message": "Version published successfully"
    }


# =============================================================================
# Question Management
# =============================================================================

@router.get("/questions")
async def list_questions(
    question_set_id: Optional[UUID] = Query(None),
    tier: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """List questions with optional filtering"""
    # Base query for filtering and counting (without eager loading)
    base_query = db.query(Question)
    
    if question_set_id:
        base_query = base_query.filter(Question.question_set_id == question_set_id)
    if tier:
        base_query = base_query.filter(Question.tier == tier)
    if category:
        base_query = base_query.filter(Question.category == category)
    
    # Get total count before applying eager loading
    total = base_query.count()
    
    # Query with eager loading for fetching results
    query = base_query.options(joinedload(Question.question_set)).order_by(Question.tier, Question.category)
    questions = query.offset(offset).limit(limit).all()
    
    # Build response with explicit serialization to avoid circular references
    items = []
    for q in questions:
        # Check if question set is locked (locked_at is not None) or if question_set is missing
        is_locked = False
        if q.question_set:
            # A question set is considered locked if locked_at is not None
            is_locked = q.question_set.locked_at is not None
        # Get question_metadata if it exists
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
            "is_locked": is_locked
        })
    
    return {
        "items": items,
        "total": total
    }


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Get question details"""
    question = db.query(Question).options(joinedload(Question.question_set)).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if question set is locked
    is_locked = False
    if question.question_set:
        is_locked = question.question_set.locked_at is not None
    
    return QuestionResponse(
        id=question.id,
        question_set_id=question.question_set_id,
        tier=question.tier,
        category=question.category,
        content=question.content,
        metadata=question.question_metadata,
        is_locked=is_locked
    )


@router.post("/questions")
async def create_question(
    question_set_id: UUID,
    tier: int,
    category: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Create a new question"""
    # Validate question set exists
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Check if question set is locked
    if question_set.locked_at is not None:
        raise HTTPException(status_code=400, detail="Question set is locked")
    
    # Validate tier
    if tier not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Tier must be 1, 2, or 3")
    
    # Create question
    question = Question(
        question_set_id=question_set_id,
        tier=tier,
        category=category,
        content=content,
        question_metadata=metadata
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return {
        "id": str(question.id),
        "question_set_id": str(question.question_set_id),
        "tier": question.tier,
        "category": question.category,
        "content": question.content,
        "metadata": question.question_metadata,
        "is_locked": False
    }


@router.post("/questions/import", response_model=QuestionImportResponse)
async def import_questions(
    request: QuestionImportRequest,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Import questions from JSON"""
    imported = 0
    errors = []
    
    if request.dry_run:
        # Validate without importing
        for idx, q_data in enumerate(request.questions):
            try:
                # Validate required fields
                if "question_set_id" not in q_data:
                    errors.append(f"Question {idx}: missing question_set_id")
                    continue
                if "tier" not in q_data:
                    errors.append(f"Question {idx}: missing tier")
                    continue
                if "category" not in q_data:
                    errors.append(f"Question {idx}: missing category")
                    continue
                if "content" not in q_data:
                    errors.append(f"Question {idx}: missing content")
                    continue
                
                # Validate question set exists
                question_set = db.query(QuestionSet).filter(
                    QuestionSet.id == q_data["question_set_id"]
                ).first()
                if not question_set:
                    errors.append(f"Question {idx}: question_set_id not found")
                    continue
                
                imported += 1
            except Exception as e:
                errors.append(f"Question {idx}: {str(e)}")
    else:
        # Actually import
        for idx, q_data in enumerate(request.questions):
            try:
                question_set_id = q_data.get("question_set_id")
                tier = q_data.get("tier")
                category = q_data.get("category")
                content = q_data.get("content")
                metadata = q_data.get("metadata")
                
                # Validate
                if not all([question_set_id, tier, category, content]):
                    errors.append(f"Question {idx}: missing required fields")
                    continue
                
                question_set = db.query(QuestionSet).filter(
                    QuestionSet.id == question_set_id
                ).first()
                if not question_set:
                    errors.append(f"Question {idx}: question_set_id not found")
                    continue
                
                # Check if question set is locked
                if question_set.locked_at is not None:
                    errors.append(f"Question {idx}: question set is locked")
                    continue
                
                # Create question
                question = Question(
                    question_set_id=question_set_id,
                    tier=tier,
                    category=category,
                    content=content,
                    question_metadata=metadata
                )
                db.add(question)
                imported += 1
            except Exception as e:
                errors.append(f"Question {idx}: {str(e)}")
        
        if imported > 0:
            db.commit()
    
    return QuestionImportResponse(
        imported=imported,
        errors=errors,
        dry_run=request.dry_run
    )


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: UUID,
    request: QuestionUpdateRequest,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Update a question"""
    question = db.query(Question).options(joinedload(Question.question_set)).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if question set is locked
    if question.question_set and question.question_set.locked_at is not None:
        raise HTTPException(status_code=400, detail="Question set is locked")
    
    if request.tier is not None:
        question.tier = request.tier
    if request.category is not None:
        question.category = request.category
    if request.content is not None:
        question.content = request.content
    if request.metadata is not None:
        question.question_metadata = request.metadata

    db.commit()
    db.refresh(question)
    
    # Check if question set is locked
    is_locked = False
    if question.question_set:
        is_locked = question.question_set.locked_at is not None
    
    return QuestionResponse(
        id=question.id,
        question_set_id=question.question_set_id,
        tier=question.tier,
        category=question.category,
        content=question.content,
        metadata=question.question_metadata,
        is_locked=is_locked
    )


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: UUID,
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Delete a question"""
    question = db.query(Question).options(joinedload(Question.question_set)).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if question set is locked
    if question.question_set and question.question_set.locked_at is not None:
        raise HTTPException(status_code=400, detail="Cannot delete question from locked question set")
    
    db.delete(question)
    db.commit()
    
    return {"message": "Question deleted"}


# =============================================================================
# Dashboard Overview
# =============================================================================

@router.get("/overview")
async def get_benchmark_overview(
    current_user: User = Depends(require_benchmark_developer),
    db: Session = Depends(get_db)
):
    """Get overview statistics for the benchmark dashboard"""
    # Get active version
    active_version = db.query(QuestionSet).filter(QuestionSet.status == "active").first()
    
    # Get draft versions
    draft_versions = db.query(QuestionSet).filter(QuestionSet.status == "draft").all()
    
    # Get locked versions (pending publish)
    locked_versions = db.query(QuestionSet).filter(QuestionSet.status == "locked").all()
    
    # Build response
    active_info = None
    if active_version:
        question_count = db.query(Question).filter(
            Question.question_set_id == active_version.id
        ).count()
        active_info = {
            "id": str(active_version.id),
            "semantic_version": active_version.semantic_version,
            "marketing_version": active_version.marketing_version,
            "question_count": question_count,
        }
    
    drafts_info = []
    for draft in draft_versions:
        question_count = db.query(Question).filter(
            Question.question_set_id == draft.id
        ).count()
        drafts_info.append({
            "id": str(draft.id),
            "semantic_version": draft.semantic_version,
            "marketing_version": draft.marketing_version,
            "question_count": question_count,
            "created_at": draft.created_at.isoformat() if draft.created_at else None,
        })
    
    locked_info = []
    for locked in locked_versions:
        question_count = db.query(Question).filter(
            Question.question_set_id == locked.id
        ).count()
        locked_info.append({
            "id": str(locked.id),
            "semantic_version": locked.semantic_version,
            "marketing_version": locked.marketing_version,
            "question_count": question_count,
            "locked_at": locked.locked_at.isoformat() if locked.locked_at else None,
        })
    
    # Total counts
    total_versions = db.query(QuestionSet).count()
    total_questions = db.query(Question).count()
    
    return {
        "active_version": active_info,
        "draft_versions": drafts_info,
        "locked_versions": locked_info,
        "stats": {
            "total_versions": total_versions,
            "total_questions": total_questions,
            "draft_count": len(drafts_info),
            "locked_count": len(locked_info),
        }
    }
