"""Admin API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from uuid import UUID
from datetime import datetime, timedelta
import json

from app.core.auth import get_db
from app.core.auth import require_admin
from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.question import Question
from app.db.models.question_set import QuestionSet
from app.db.models.moderation_log import ModerationLog
from app.db.models.user_api_key import UserAPIKey
from app.db.models.result import Result
from app.db.models.community_submission import CommunitySubmission
from app.schemas.admin import (
    UserListItem,
    UserListResponse,
    UpdateUserRoleRequest,
    UpdateUserRoleResponse,
    UpdateUserPermissionsRequest,
    UserPermissionsResponse,
    UpdateFeeWaiverRequest,
    UpdateFeeWaiverResponse,
    QuestionImportRequest,
    QuestionImportResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionResponse,
    QuestionSetCreateRequest,
    QuestionSetUpdateTargetRequest,
    VersionCreateRequest,
    VersionPublishRequest,
    AdminStatsResponse,
    QuestionSetStatsResponse,
    QuestionSetCopyRequest,
    CategoryStats,
    TierStats,
    DifficultyStats,
    DifficultyCount,
    CategoryDifficultyBreakdown
)

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def list_users(
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.name.ilike(f"%{search}%"))
        )
    
    if role:
        query = query.filter(User.role == role)
    
    query = query.order_by(desc(User.created_at))
    
    total = query.count()
    users = query.offset(offset).limit(limit).all()
    
    user_items = []
    for user in users:
        test_count = db.query(TestRun).filter(TestRun.user_id == user.id).count()
        
        user_items.append(UserListItem(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            created_at=user.created_at.isoformat() if user.created_at else "",
            test_count=test_count,
            fee_waived=user.fee_waived,
            fee_waived_reason=user.fee_waived_reason,
            can_view_benchmark=user.can_view_benchmark,
            can_edit_benchmark=user.can_edit_benchmark,
            can_moderate=user.can_moderate,
            can_manage_blog=user.can_manage_blog,
            can_admin=user.can_admin
        ))
    
    return UserListResponse(users=user_items, total=total)


@router.put("/users/{user_id}/role", response_model=UpdateUserRoleResponse)
async def update_user_role(
    user_id: UUID,
    request: UpdateUserRoleRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user role and apply default permissions for that role"""
    valid_roles = ["user", "moderator", "blog_manager", "benchmark_viewer", "benchmark_administrator", "admin"]
    if request.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent removing last admin
    if user.can_admin and request.role != "admin":
        admin_count = db.query(User).filter(User.can_admin == True).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove last admin user"
            )
    
    old_role = user.role
    user.role = request.role
    
    # Apply default permissions based on role
    # Note: This sets defaults, but permissions can be overridden via the permissions endpoint
    if request.role == "user":
        user.can_view_benchmark = False
        user.can_edit_benchmark = False
        user.can_moderate = False
        user.can_manage_blog = False
        user.can_admin = False
    elif request.role == "moderator":
        user.can_moderate = True
        user.can_view_benchmark = False
        user.can_edit_benchmark = False
        user.can_manage_blog = False
        user.can_admin = False
    elif request.role == "benchmark_viewer":
        user.can_view_benchmark = True
        user.can_edit_benchmark = False
        user.can_moderate = False
        user.can_manage_blog = False
        user.can_admin = False
    elif request.role == "benchmark_administrator":
        user.can_view_benchmark = True
        user.can_edit_benchmark = True
        user.can_moderate = False
        user.can_manage_blog = False
        user.can_admin = False
    elif request.role == "blog_manager":
        user.can_manage_blog = True
        user.can_view_benchmark = False
        user.can_edit_benchmark = False
        user.can_moderate = False
        user.can_admin = False
    elif request.role == "admin":
        user.can_admin = True
        # Admin gets all permissions (cascades)
        user.can_view_benchmark = True
        user.can_edit_benchmark = True
        user.can_moderate = True
        user.can_manage_blog = True
    
    db.commit()
    
    return UpdateUserRoleResponse(
        user_id=user.id,
        role=user.role,
        message=f"User role updated from {old_role} to {request.role}"
    )


@router.put("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
async def update_user_permissions(
    user_id: UUID,
    request: UpdateUserPermissionsRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user permissions directly"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent removing last admin
    if user.can_admin and request.can_admin is False:
        admin_count = db.query(User).filter(User.can_admin == True).count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove last admin user"
            )
    
    # Update permissions (only update if explicitly provided)
    if request.can_view_benchmark is not None:
        user.can_view_benchmark = request.can_view_benchmark
    if request.can_edit_benchmark is not None:
        user.can_edit_benchmark = request.can_edit_benchmark
        # Editing implies viewing
        if request.can_edit_benchmark:
            user.can_view_benchmark = True
    if request.can_moderate is not None:
        user.can_moderate = request.can_moderate
    if request.can_manage_blog is not None:
        user.can_manage_blog = request.can_manage_blog
    if request.can_admin is not None:
        user.can_admin = request.can_admin
        # Admin cascades to all permissions
        if request.can_admin:
            user.can_view_benchmark = True
            user.can_edit_benchmark = True
            user.can_moderate = True
            user.can_manage_blog = True
    
    db.commit()
    db.refresh(user)
    
    return UserPermissionsResponse(
        user_id=user.id,
        can_view_benchmark=user.can_view_benchmark,
        can_edit_benchmark=user.can_edit_benchmark,
        can_moderate=user.can_moderate,
        can_manage_blog=user.can_manage_blog,
        can_admin=user.can_admin,
        message="User permissions updated successfully"
    )


@router.put("/users/{user_id}/fee-waiver", response_model=UpdateFeeWaiverResponse)
async def update_fee_waiver(
    user_id: UUID,
    request: UpdateFeeWaiverRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user fee waiver status"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Note: Moderators and admins automatically have fee waived by role
    # This flag is for granting waiver to regular users (e.g., stewardship team)
    
    user.fee_waived = request.waived
    user.fee_waived_reason = request.reason
    user.fee_waived_at = datetime.utcnow() if request.waived else None
    user.fee_waived_by = current_user.id if request.waived else None
    
    db.commit()
    db.refresh(user)
    
    message = f"Fee waiver {'granted' if request.waived else 'revoked'}"
    if request.reason:
        message += f": {request.reason}"
    
    return UpdateFeeWaiverResponse(
        user_id=user.id,
        fee_waived=user.fee_waived,
        fee_waived_reason=user.fee_waived_reason,
        message=message
    )


@router.post("/questions/import", response_model=QuestionImportResponse)
async def import_questions(
    request: QuestionImportRequest,
    current_user: User = Depends(require_admin),
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
                
                # Extract expected_verdict from metadata to column
                expected_verdict = None
                clean_metadata = None
                if metadata and isinstance(metadata, dict):
                    expected_verdict = metadata.get("expected_verdict")
                    # Keep only difficulty in metadata
                    if "difficulty" in metadata:
                        clean_metadata = {"difficulty": metadata["difficulty"]}
                
                # Get notes if present
                notes = q_data.get("notes")
                
                # Create question
                question = Question(
                    question_set_id=question_set_id,
                    tier=tier,
                    category=category,
                    content=content,
                    expected_verdict=expected_verdict,
                    question_metadata=clean_metadata,
                    notes=notes
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


@router.get("/questions")
async def list_questions(
    question_set_id: Optional[UUID] = Query(None),
    tier: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List questions"""
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
            "content": q.content,  # Return full content, not truncated
            "metadata": metadata,
            "expected_verdict": q.expected_verdict,
            "is_locked": is_locked,
            "notes": q.notes
        })
    
    return {
        "items": items,
        "total": total
    }


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    current_user: User = Depends(require_admin),
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
        expected_verdict=question.expected_verdict,
        is_locked=is_locked,
        notes=question.notes
    )


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: UUID,
    request: QuestionUpdateRequest,
    current_user: User = Depends(require_admin),
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
        # Keep only difficulty in metadata
        if isinstance(request.metadata, dict) and "difficulty" in request.metadata:
            question.question_metadata = {"difficulty": request.metadata["difficulty"]}
        else:
            question.question_metadata = None
    if request.expected_verdict is not None:
        question.expected_verdict = request.expected_verdict

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
        expected_verdict=question.expected_verdict,
        is_locked=is_locked,
        notes=question.notes
    )


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: UUID,
    current_user: User = Depends(require_admin),
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


@router.get("/question-sets")
async def list_question_sets(
    status: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all question sets"""
    query = db.query(QuestionSet)
    
    if status:
        query = query.filter(QuestionSet.status == status)
    
    question_sets = query.order_by(QuestionSet.created_at.desc()).all()
    
    return {
        "items": [
            {
                "id": str(qs.id),
                "semantic_version": qs.semantic_version,
                "marketing_version": qs.marketing_version,
                "status": qs.status,
                "is_publicly_visible": qs.is_publicly_visible,
                "created_at": qs.created_at.isoformat() if qs.created_at else None,
            }
            for qs in question_sets
        ],
        "total": len(question_sets)
    }


@router.post("/question-sets")
async def create_question_set(
    request: QuestionSetCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new empty question set"""
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


# Import shared benchmark configuration
from app.core.benchmark_config import (
    TIER_PERCENTAGES,
    DIFFICULTY_PERCENTAGES,
    BALANCE_TOLERANCE,
    CATEGORY_WEIGHTS,
    calculate_targets,
)

# Import question management service for shared operations
from app.services.question_management import QuestionManagementService


@router.delete("/question-sets/{question_set_id}")
async def delete_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a question set and all its questions"""
    service = QuestionManagementService(db)
    return service.delete_question_set(question_set_id)


@router.post("/question-sets/{question_set_id}/empty")
async def empty_question_set(
    question_set_id: UUID,
    current_user: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get statistics for a question set"""
    service = QuestionManagementService(db)
    return service.get_question_set_stats(question_set_id)


@router.post("/question-sets/{question_set_id}/copy")
async def copy_question_set(
    question_set_id: UUID,
    request: QuestionSetCopyRequest,
    current_user: User = Depends(require_admin),
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
            question_metadata=source_q.question_metadata,
            notes=source_q.notes
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
    current_user: User = Depends(require_admin),
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
    current_user: User = Depends(require_admin),
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
    is_publicly_visible: bool = Query(False, description="Keep version publicly visible after archiving"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Archive a question set.
    
    By default, archived versions are not publicly visible. Set is_publicly_visible=True
    to keep the version visible in the public API after archiving.
    """
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Only active versions can be archived
    if question_set.status not in ["active", "locked"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot archive a {question_set.status} version. Only active or locked versions can be archived."
        )
    
    question_set.status = "archived"
    question_set.archived_at = datetime.utcnow()
    question_set.is_publicly_visible = is_publicly_visible
    db.commit()
    
    return {
        "message": f"Question set {question_set.semantic_version} archived",
        "version": question_set.semantic_version,
        "status": question_set.status,
        "is_publicly_visible": question_set.is_publicly_visible,
        "archived_at": question_set.archived_at.isoformat()
    }


@router.patch("/question-sets/{question_set_id}/visibility")
async def toggle_question_set_visibility(
    question_set_id: UUID,
    is_publicly_visible: bool = Query(..., description="Whether the version should be publicly visible"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Toggle public visibility for an archived question set.
    
    Only archived versions can have their visibility toggled.
    Active versions are always publicly visible.
    Draft versions are never publicly visible.
    """
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    if question_set.status != "archived":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change visibility of a {question_set.status} version. Only archived versions can have their visibility toggled."
        )
    
    question_set.is_publicly_visible = is_publicly_visible
    db.commit()
    
    return {
        "message": f"Question set {question_set.semantic_version} visibility updated",
        "version": question_set.semantic_version,
        "status": question_set.status,
        "is_publicly_visible": question_set.is_publicly_visible
    }


@router.patch("/question-sets/{question_set_id}/target")
async def update_question_set_target(
    question_set_id: UUID,
    request: QuestionSetUpdateTargetRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update the target question count for a question set"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    # Only allow updating target for draft versions
    if question_set.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Can only update target question count for draft versions"
        )
    
    # Validate target if provided
    if request.target_question_count is not None and request.target_question_count < 1:
        raise HTTPException(
            status_code=400,
            detail="Target question count must be at least 1"
        )
    
    question_set.target_question_count = request.target_question_count
    db.commit()
    
    return {
        "message": "Target question count updated",
        "version": question_set.semantic_version,
        "target_question_count": question_set.target_question_count
    }


@router.put("/question-sets/{question_set_id}/status")
async def update_question_set_status(
    question_set_id: UUID,
    new_status: str = Query(..., description="New status: draft, locked, active, archived"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update the status of a question set"""
    question_set = db.query(QuestionSet).filter(QuestionSet.id == question_set_id).first()
    
    if not question_set:
        raise HTTPException(status_code=404, detail="Question set not found")
    
    valid_statuses = ["draft", "locked", "active", "archived"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    old_status = question_set.status
    
    # Validate transitions
    valid_transitions = {
        "draft": ["locked"],
        "locked": ["draft", "active", "archived"],
        "active": ["archived"],
        "archived": ["active"],  # Allow reactivating
    }
    
    if new_status not in valid_transitions.get(old_status, []) and new_status != old_status:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {old_status} to {new_status}. "
                   f"Valid transitions: {', '.join(valid_transitions.get(old_status, []))}"
        )
    
    # If transitioning to active, deactivate other active versions
    if new_status == "active" and old_status != "active":
        db.query(QuestionSet).filter(
            QuestionSet.status == "active",
            QuestionSet.id != question_set_id
        ).update({
            "status": "archived",
            "archived_at": datetime.utcnow(),
            "is_publicly_visible": False
        })
        # Active versions are always publicly visible
        question_set.is_publicly_visible = True
    
    # Update timestamps based on transition
    if new_status == "locked" and old_status == "draft":
        question_set.locked_at = datetime.utcnow()
    elif new_status == "draft" and old_status == "locked":
        question_set.locked_at = None
    elif new_status == "archived":
        question_set.archived_at = datetime.utcnow()
        # Archived versions are hidden by default
        question_set.is_publicly_visible = False
    
    question_set.status = new_status
    db.commit()
    
    return {
        "message": f"Question set {question_set.semantic_version} status changed from {old_status} to {new_status}",
        "version": question_set.semantic_version,
        "status": question_set.status
    }


@router.post("/versions", response_model=dict)
async def create_version(
    request: VersionCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new version draft"""
    # Validate questions exist
    questions = db.query(Question).filter(Question.id.in_(request.question_ids)).all()
    
    if len(questions) != len(request.question_ids):
        raise HTTPException(status_code=400, detail="Some question IDs not found")
    
    # Check tier distribution (should be 70/20/10)
    tier_counts = {}
    for q in questions:
        tier_counts[q.tier] = tier_counts.get(q.tier, 0) + 1
    
    total = len(questions)
    tier1_pct = (tier_counts.get(1, 0) / total * 100) if total > 0 else 0
    tier2_pct = (tier_counts.get(2, 0) / total * 100) if total > 0 else 0
    tier3_pct = (tier_counts.get(3, 0) / total * 100) if total > 0 else 0
    
    # Create question set
    question_set = QuestionSet(
        semantic_version=request.semantic_version,
        status="draft",
        description=request.description
    )
    db.add(question_set)
    db.flush()
    
    # Associate questions with question set
    for question in questions:
        question.question_set_id = question_set.id
    
    db.commit()
    db.refresh(question_set)
    
    return {
        "version_id": question_set.id,
        "semantic_version": question_set.semantic_version,
        "question_count": len(questions),
        "tier_distribution": {
            "tier1": {"count": tier_counts.get(1, 0), "percentage": round(tier1_pct, 2)},
            "tier2": {"count": tier_counts.get(2, 0), "percentage": round(tier2_pct, 2)},
            "tier3": {"count": tier_counts.get(3, 0), "percentage": round(tier3_pct, 2)}
        },
        "status": question_set.status
    }


@router.put("/versions/{version}/publish", response_model=dict)
async def publish_version(
    version: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Publish a version"""
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
    
    # Deactivate other active versions (set not publicly visible by default)
    db.query(QuestionSet).filter(
        QuestionSet.status == "active"
    ).update({
        "status": "archived",
        "archived_at": datetime.utcnow(),
        "is_publicly_visible": False
    })
    
    # Activate this version (active versions are always publicly visible)
    question_set.status = "active"
    question_set.is_publicly_visible = True
    db.commit()
    
    return {
        "version": question_set.semantic_version,
        "status": question_set.status,
        "message": "Version published successfully"
    }


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin statistics"""
    # User stats
    total_users = db.query(User).count()
    new_users_30d = db.query(User).filter(
        User.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    
    # Test stats
    total_tests = db.query(TestRun).count()
    completed_tests = db.query(TestRun).filter(TestRun.status == "completed").count()
    running_tests = db.query(TestRun).filter(TestRun.status == "running").count()
    
    # Revenue stats (from test runs)
    total_revenue = db.query(func.sum(TestRun.total_cost)).filter(
        TestRun.payment_status == "succeeded"
    ).scalar() or 0
    
    revenue_30d = db.query(func.sum(TestRun.total_cost)).filter(
        TestRun.payment_status == "succeeded",
        TestRun.created_at >= datetime.utcnow() - timedelta(days=30)
    ).scalar() or 0
    
    # Moderation stats
    pending_reviews = db.query(TestRun).filter(
        TestRun.status == "completed",
        TestRun.trust_tier.in_(["pending_review", "automated"])
    ).count()
    
    total_moderation_logs = db.query(ModerationLog).count()
    
    # API key stats
    total_api_keys = db.query(UserAPIKey).count()
    active_api_keys = db.query(UserAPIKey).filter(UserAPIKey.is_active == True).count()
    
    return AdminStatsResponse(
        users={
            "total": total_users,
            "new_last_30_days": new_users_30d
        },
        tests={
            "total": total_tests,
            "completed": completed_tests,
            "running": running_tests
        },
        revenue={
            "total": float(total_revenue),
            "last_30_days": float(revenue_30d)
        },
        moderation={
            "pending_reviews": pending_reviews,
            "total_reviews": total_moderation_logs
        },
        api_keys={
            "total": total_api_keys,
            "active": active_api_keys
        }
    )


# =============================================================================
# Data Management Endpoints (for cleanup/deletion)
# =============================================================================

@router.delete("/test-runs/{test_run_id}")
async def delete_test_run(
    test_run_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a test run and all its results (cascade)"""
    test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    # Delete all results for this test run first
    deleted_results = db.query(Result).filter(
        Result.test_run_id == test_run_id
    ).delete(synchronize_session=False)
    
    # Delete the test run
    db.delete(test_run)
    db.commit()
    
    return {
        "message": f"Test run deleted",
        "test_run_id": str(test_run_id),
        "deleted_results": deleted_results
    }


@router.delete("/community-submissions/{submission_id}")
async def delete_community_submission(
    submission_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a community submission"""
    submission = db.query(CommunitySubmission).filter(
        CommunitySubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Community submission not found")
    
    db.delete(submission)
    db.commit()
    
    return {
        "message": "Community submission deleted",
        "submission_id": str(submission_id)
    }


@router.delete("/results/{result_id}")
async def delete_result(
    result_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an individual result"""
    result = db.query(Result).filter(Result.id == result_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    db.delete(result)
    db.commit()
    
    return {
        "message": "Result deleted",
        "result_id": str(result_id)
    }


@router.delete("/models/{model_id}")
async def delete_model(
    model_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a model (only if no test runs reference it)"""
    model = db.query(Model).filter(Model.id == model_id).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Check if any test runs reference this model
    test_run_count = db.query(TestRun).filter(TestRun.model_id == model_id).count()
    if test_run_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete model. {test_run_count} test run(s) reference this model. Delete those test runs first."
        )
    
    db.delete(model)
    db.commit()
    
    return {
        "message": "Model deleted",
        "model_id": str(model_id),
        "model_name": model.name
    }


@router.get("/test-runs")
async def list_test_runs(
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    model_id: Optional[UUID] = Query(None, description="Filter by model ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List test runs with filters"""
    query = db.query(TestRun).options(
        joinedload(TestRun.user),
        joinedload(TestRun.model),
        joinedload(TestRun.question_set)
    )
    
    if status:
        query = query.filter(TestRun.status == status)
    if user_id:
        query = query.filter(TestRun.user_id == user_id)
    if model_id:
        query = query.filter(TestRun.model_id == model_id)
    
    query = query.order_by(desc(TestRun.created_at))
    
    total = db.query(TestRun).filter(
        *([TestRun.status == status] if status else []),
        *([TestRun.user_id == user_id] if user_id else []),
        *([TestRun.model_id == model_id] if model_id else [])
    ).count()
    
    test_runs = query.offset(offset).limit(limit).all()
    
    # Get result counts for each test run
    items = []
    for tr in test_runs:
        result_count = db.query(Result).filter(Result.test_run_id == tr.id).count()
        items.append({
            "id": str(tr.id),
            "user_id": str(tr.user_id),
            "user_email": tr.user.email if tr.user else None,
            "model_id": str(tr.model_id),
            "model_name": tr.model.name if tr.model else None,
            "question_set_id": str(tr.question_set_id) if tr.question_set_id else None,
            "question_set_version": tr.question_set.semantic_version if tr.question_set else None,
            "status": tr.status,
            "result_count": result_count,
            "created_at": tr.created_at.isoformat() if tr.created_at else None,
            "completed_at": tr.completed_at.isoformat() if tr.completed_at else None,
        })
    
    return {
        "items": items,
        "total": total
    }


@router.get("/community-submissions")
async def list_community_submissions(
    status: Optional[str] = Query(None, description="Filter by status"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List community submissions with filters"""
    query = db.query(CommunitySubmission).options(
        joinedload(CommunitySubmission.user)
    )
    
    if status:
        query = query.filter(CommunitySubmission.status == status)
    if user_id:
        query = query.filter(CommunitySubmission.user_id == user_id)
    
    query = query.order_by(desc(CommunitySubmission.submitted_at))
    
    total = db.query(CommunitySubmission).filter(
        *([CommunitySubmission.status == status] if status else []),
        *([CommunitySubmission.user_id == user_id] if user_id else [])
    ).count()
    
    submissions = query.offset(offset).limit(limit).all()
    
    items = []
    for sub in submissions:
        items.append({
            "id": str(sub.id),
            "user_id": str(sub.user_id),
            "user_email": sub.user.email if sub.user else None,
            "model_name": sub.model_name,
            "organization": sub.organization,
            "status": sub.status,
            "overall_score": sub.overall_score,
            "question_set_version": sub.question_set_version,
            "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
            "reviewed_at": sub.reviewed_at.isoformat() if sub.reviewed_at else None,
        })
    
    return {
        "items": items,
        "total": total
    }


@router.get("/models")
async def list_models(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or provider"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List models with filters"""
    query = db.query(Model)
    
    if is_active is not None:
        query = query.filter(Model.is_active == is_active)
    if search:
        query = query.filter(
            (Model.name.ilike(f"%{search}%")) |
            (Model.provider.ilike(f"%{search}%"))
        )
    
    query = query.order_by(Model.name)
    
    # Build count query with same filters
    count_query = db.query(Model)
    if is_active is not None:
        count_query = count_query.filter(Model.is_active == is_active)
    if search:
        count_query = count_query.filter(
            (Model.name.ilike(f"%{search}%")) |
            (Model.provider.ilike(f"%{search}%"))
        )
    total = count_query.count()
    
    models = query.offset(offset).limit(limit).all()
    
    # Get test run counts for each model
    items = []
    for model in models:
        test_run_count = db.query(TestRun).filter(TestRun.model_id == model.id).count()
        items.append({
            "id": str(model.id),
            "model_id": model.model_id,
            "name": model.name,
            "provider": model.provider,
            "is_active": model.is_active,
            "test_run_count": test_run_count,
            "created_at": model.created_at.isoformat() if model.created_at else None,
        })
    
    return {
        "items": items,
        "total": total
    }
