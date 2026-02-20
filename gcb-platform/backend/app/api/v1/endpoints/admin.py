"""Admin API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, or_, and_
from uuid import UUID
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

from app.core.auth import get_db, get_current_user, has_permission
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
from app.db.models.stripe_config import StripeConfig
from app.db.models.sponsorship_request import SponsorshipRequest
from app.db.models.action_log import ActionLog
from app.services.payment import PaymentService, EncryptionService
from app.services.model_sync import sync_all_model_descriptions
from app.services.action_log import ActionLogService
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
    CategoryDifficultyBreakdown,
    # Stripe schemas
    StripeConfigStatusResponse,
    StripeConfigCreateRequest,
    StripeConfigTestRequest,
    StripeConfigTestResponse,
    StripeBalanceResponse,
    StripeTransactionsResponse,
    StripePaymentIntentsResponse,
    StripeChargesResponse,
    StripeRefundsResponse,
    # Newsletter admin schemas
    NewsletterSubscriberListItem,
    NewsletterSubscriberListResponse,
    NewsletterSubscriberDetail,
    NewsletterStatsResponse,
    MailerLiteSubscriberItem,
    MailerLiteSubscriberListResponse,
)
from app.schemas.sponsorship import (
    AdminSponsorshipItem,
    AdminSponsorshipListResponse,
    AssignModeratorRequest,
    AssignModeratorResponse,
    ModeratorListItem,
    ModeratorListResponse,
)
from app.schemas.action_log import ActionLogListItem, ActionLogListResponse, ActionLogActor

router = APIRouter()

_optional_bearer = HTTPBearer(auto_error=False)


@router.get("/action-logs", response_model=ActionLogListResponse)
async def list_action_logs(
    action: Optional[str] = Query(None, description="Filter by action code"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    actor_user_id: Optional[UUID] = Query(None, description="Filter by actor user ID"),
    since: Optional[datetime] = Query(None, description="Start of date range (inclusive)"),
    until: Optional[datetime] = Query(None, description="End of date range (inclusive)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List action logs (audit trail) with optional filters. Admin only."""
    query = db.query(ActionLog).options(
        joinedload(ActionLog.actor_user)
    )
    if action:
        query = query.filter(ActionLog.action == action)
    if entity_type:
        query = query.filter(ActionLog.entity_type == entity_type)
    if actor_user_id:
        query = query.filter(ActionLog.actor_user_id == actor_user_id)
    if since:
        query = query.filter(ActionLog.created_at >= since)
    if until:
        query = query.filter(ActionLog.created_at <= until)

    total = query.count()
    query = query.order_by(desc(ActionLog.created_at))
    logs = query.offset(offset).limit(limit).all()

    items = []
    for log in logs:
        actor_user = None
        if log.actor_user:
            actor_user = ActionLogActor(
                id=log.actor_user.id,
                name=log.actor_user.name,
                email=log.actor_user.email,
            )
        items.append(ActionLogListItem(
            id=log.id,
            action=log.action,
            actor_type=log.actor_type,
            actor_user=actor_user,
            actor_api_key_id=log.actor_api_key_id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            metadata=log.extra_data,
            created_at=log.created_at,
        ))

    return ActionLogListResponse(items=items, total=total)


async def require_admin_flexible(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_optional_bearer),
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    """Accept either a Bearer (NextAuth JWT) or an X-API-Key for admin-level access."""
    from app.api.v1.endpoints.api_keys import validate_api_key

    if x_api_key:
        api_key_record, user = validate_api_key(db, x_api_key)
        if not api_key_record or not user:
            raise HTTPException(status_code=401, detail="Invalid or expired API key")
        if not has_permission(user, "can_admin"):
            raise HTTPException(status_code=403, detail="Admin permission required")
        return user

    if credentials:
        return await get_current_user(credentials, db)

    raise HTTPException(status_code=401, detail="Authentication required")


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

    ActionLogService.log_action(
        db, "question_set.archive", "user",
        actor_user_id=current_user.id,
        entity_type="question_set", entity_id=str(question_set.id),
        metadata={"version": question_set.semantic_version, "is_publicly_visible": is_publicly_visible}
    )
    
    # Invalidate cache for versions endpoint since visibility/status changed
    from app.core.cache import invalidate_cache
    await invalidate_cache("versions")
    
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

    ActionLogService.log_action(
        db, "question_set.toggle_visibility", "user",
        actor_user_id=current_user.id,
        entity_type="question_set", entity_id=str(question_set.id),
        metadata={"version": question_set.semantic_version, "is_publicly_visible": is_publicly_visible}
    )
    
    # Invalidate cache for versions endpoint since visibility changed
    from app.core.cache import invalidate_cache
    await invalidate_cache("versions")
    
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

    ActionLogService.log_action(
        db, "question_set.status_update", "user",
        actor_user_id=current_user.id,
        entity_type="question_set", entity_id=str(question_set.id),
        metadata={"old_status": old_status, "new_status": new_status, "version": question_set.semantic_version}
    )

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
    """Get admin statistics. Each section is independently protected so a
    single DB or external-service failure doesn't take down the whole response."""

    total_users = 0
    new_users_30d = 0
    try:
        total_users = db.query(User).count()
        new_users_30d = db.query(User).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
    except Exception as e:
        logger.error(f"Admin stats - user stats failed: {e}")
        db.rollback()

    total_tests = 0
    completed_tests = 0
    running_tests = 0
    try:
        total_tests = db.query(TestRun).count()
        completed_tests = db.query(TestRun).filter(TestRun.status == "completed").count()
        running_tests = db.query(TestRun).filter(TestRun.status == "running").count()
    except Exception as e:
        logger.error(f"Admin stats - test stats failed: {e}")
        db.rollback()

    test_run_revenue = 0
    test_run_revenue_30d = 0
    try:
        test_run_revenue = db.query(func.sum(TestRun.total_cost)).filter(
            TestRun.payment_status == "succeeded"
        ).scalar() or 0
        test_run_revenue_30d = db.query(func.sum(TestRun.total_cost)).filter(
            TestRun.payment_status == "succeeded",
            TestRun.created_at >= datetime.utcnow() - timedelta(days=30)
        ).scalar() or 0
    except Exception as e:
        logger.error(f"Admin stats - test run revenue failed: {e}")
        db.rollback()

    sponsorship_revenue = 0
    sponsorship_revenue_30d = 0
    try:
        succeeded_sponsorships = db.query(SponsorshipRequest).filter(
            SponsorshipRequest.payment_status == "succeeded",
            SponsorshipRequest.payment_id.isnot(None),
            SponsorshipRequest.request_type == "sponsorship"
        ).all()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        for sponsorship in succeeded_sponsorships:
            try:
                payment_intent = PaymentService.get_payment_intent(
                    sponsorship.payment_id,
                    db=db
                )
                amount = payment_intent.get("amount", 0)
                sponsorship_revenue += amount
                if sponsorship.created_at >= thirty_days_ago:
                    sponsorship_revenue_30d += amount
            except Exception as e:
                logger.warning(f"Failed to retrieve payment for sponsorship {sponsorship.id}: {e}")
                continue
    except Exception as e:
        logger.error(f"Admin stats - sponsorship revenue failed: {e}")
        db.rollback()

    total_revenue = float(test_run_revenue) + sponsorship_revenue
    revenue_30d = float(test_run_revenue_30d) + sponsorship_revenue_30d

    pending_reviews = 0
    total_moderation_logs = 0
    community_queue = 0
    sponsorship_queue = 0
    try:
        pending_reviews = db.query(TestRun).filter(
            TestRun.status == "completed",
            TestRun.trust_tier.in_(["pending_review", "automated"])
        ).count()
        total_moderation_logs = db.query(ModerationLog).count()
        # Community submissions awaiting review (matches moderator queue)
        community_queue = db.query(CommunitySubmission).filter(
            CommunitySubmission.status.in_(["pending", "reviewing"])
        ).count()
        # Sponsorship requests awaiting review (same filter as moderator get_sponsorship_queue)
        sponsorship_queue = db.query(SponsorshipRequest).filter(
            or_(
                SponsorshipRequest.status == "pending",
                and_(
                    SponsorshipRequest.status == "pending_payment",
                    or_(
                        SponsorshipRequest.payment_status == "succeeded",
                        and_(
                            SponsorshipRequest.payment_id.isnot(None),
                            or_(
                                SponsorshipRequest.payment_status.is_(None),
                                SponsorshipRequest.payment_status == "pending"
                            )
                        )
                    )
                )
            )
        ).count()
    except Exception as e:
        logger.error(f"Admin stats - moderation stats failed: {e}")
        db.rollback()

    total_api_keys = 0
    active_api_keys = 0
    try:
        total_api_keys = db.query(UserAPIKey).count()
        active_api_keys = db.query(UserAPIKey).filter(UserAPIKey.is_active == True).count()
    except Exception as e:
        logger.error(f"Admin stats - API key stats failed: {e}")
        db.rollback()

    total_newsletter = 0
    active_newsletter = 0
    try:
        from app.db.models.newsletter_subscriber import NewsletterSubscriber as NS
        total_newsletter = db.query(NS).count()
        active_newsletter = db.query(NS).filter(NS.is_active == True).count()
    except Exception as e:
        logger.error(f"Admin stats - newsletter stats failed: {e}")
        db.rollback()

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
            "total_reviews": total_moderation_logs,
            "community_queue": community_queue,
            "sponsorship_queue": sponsorship_queue,
        },
        api_keys={
            "total": total_api_keys,
            "active": active_api_keys
        },
        newsletter={
            "total": total_newsletter,
            "active": active_newsletter,
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
    """Delete a test run and all its results. Removes moderation logs. Recalculates leaderboard stats for the affected model."""
    test_run = db.query(TestRun).filter(TestRun.id == test_run_id).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    model_id = test_run.model_id
    question_set_id = test_run.question_set_id
    community_submission_id = test_run.community_submission_id
    
    # Delete moderation logs (must precede test run delete due to FK)
    deleted_logs = db.query(ModerationLog).filter(ModerationLog.test_run_id == test_run_id).delete(synchronize_session=False)
    
    # Delete all results for this test run
    deleted_results = db.query(Result).filter(
        Result.test_run_id == test_run_id
    ).delete(synchronize_session=False)
    
    # Revert linked community submission to rejected so it's not orphaned approved
    if community_submission_id:
        submission = db.query(CommunitySubmission).filter(CommunitySubmission.id == community_submission_id).first()
        if submission and submission.status == "approved":
            submission.status = "rejected"
            submission.reviewer_id = None
            submission.reviewed_at = None
            submission.reviewer_notes = (
                (submission.reviewer_notes or "") + "\n[Review cleared: associated test run was deleted]"
            ).strip() or None
    
    # Delete the test run
    db.delete(test_run)
    db.commit()
    
    # Recalculate model_version_stats so leaderboard reflects the removal
    try:
        from app.services.aggregation import AggregationService
        AggregationService.recalculate_model_stats(db, model_id, question_set_id)
    except Exception as e:
        logger.warning("Stats recalculation after test run delete failed: %s", e)
    
    try:
        from app.core.cache import invalidate_cache
        await invalidate_cache("leaderboard")
    except Exception as e:
        logger.warning("Leaderboard cache invalidation after test run delete failed: %s", e)
    
    return {
        "message": "Test run deleted",
        "test_run_id": str(test_run_id),
        "deleted_results": deleted_results,
        "deleted_moderation_logs": deleted_logs,
    }


@router.post("/cleanup/orphaned-approved-submissions")
async def cleanup_orphaned_approved_submissions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Revert approved community submissions that have no associated test run (orphaned after run deletion)."""
    # Use left outer join: approved submissions with no matching test run (TestRun.id IS NULL)
    orphaned = (
        db.query(CommunitySubmission)
        .outerjoin(TestRun, TestRun.community_submission_id == CommunitySubmission.id)
        .filter(CommunitySubmission.status == "approved", TestRun.id.is_(None))
        .all()
    )
    reverted = []
    for submission in orphaned:
        submission.status = "rejected"
        submission.reviewer_id = None
        submission.reviewed_at = None
        submission.reviewer_notes = (
            (submission.reviewer_notes or "") + "\n[Review cleared: no associated test run found]"
        ).strip() or None
        reverted.append(str(submission.id))
    db.commit()
    return {
        "message": "Orphaned approved submissions reverted",
        "count": len(reverted),
        "submission_ids": reverted,
    }


@router.post("/cleanup/orphaned-moderation-logs")
async def cleanup_orphaned_moderation_logs(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete ModerationLog rows whose test_run_id no longer exists (orphaned after run deletion)."""
    # Subquery: test_run_ids that exist
    existing_run_ids = db.query(TestRun.id).subquery()
    deleted = db.query(ModerationLog).filter(
        ~ModerationLog.test_run_id.in_(existing_run_ids)
    ).delete(synchronize_session=False)
    db.commit()
    return {
        "message": "Orphaned moderation logs deleted",
        "deleted_count": deleted,
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


@router.post("/models/{model_id}/recalculate-scores")
async def recalculate_model_scores(
    model_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Recalculate and store scores for all completed test runs of a model.
    Use this to backfill or fix test runs with null overall_score.
    Invalidates caches after update.
    """
    from app.services.scoring import compute_and_store_test_run_scores
    from app.services.aggregation import AggregationService
    from app.core.cache import cache

    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    # Find completed test runs with null scores (or all completed - we overwrite)
    test_runs = db.query(TestRun).filter(
        TestRun.model_id == model_id,
        TestRun.status == "completed",
    ).all()

    updated_count = 0
    affected_versions = set()
    for test_run in test_runs:
        try:
            compute_and_store_test_run_scores(db, test_run)
            db.commit()
            updated_count += 1
            affected_versions.add((test_run.model_id, test_run.question_set_id))
        except Exception as e:
            logger.warning(f"Failed to recalculate scores for test run {test_run.id}: {e}")
            db.rollback()

    # Update ModelVersionStats for each affected model+version
    for mid, qsid in affected_versions:
        try:
            AggregationService.recalculate_model_stats(db, mid, qsid)
        except Exception as e:
            logger.warning(f"Failed to update ModelVersionStats for model {mid}: {e}")

    # Invalidate caches so leaderboard reflects updated scores
    await cache.clear()

    return {
        "message": f"Recalculated scores for {updated_count} test run(s)",
        "model_id": str(model_id),
        "model_name": model.name,
        "updated_count": updated_count
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


# =============================================================================
# Stripe Configuration & Transaction Endpoints
# =============================================================================

@router.get("/stripe/config", response_model=StripeConfigStatusResponse)
async def get_stripe_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get current Stripe configuration status (with masked keys)"""
    keys = PaymentService.get_stripe_keys(db)
    
    # Get additional info if from database
    updated_at = None
    updated_by_email = None
    
    if keys["source"] == "database":
        config = PaymentService.get_active_config(db)
        if config:
            updated_at = config.updated_at.isoformat() if config.updated_at else None
            if config.updated_by:
                updated_by_email = config.updated_by.email
    
    return StripeConfigStatusResponse(
        is_configured=bool(keys.get("secret_key")),
        source=keys["source"],
        is_live_mode=keys.get("is_live_mode", False),
        config_name=keys.get("config_name"),
        config_id=keys.get("config_id"),
        secret_key_masked=PaymentService.mask_key(keys["secret_key"]) if keys.get("secret_key") else None,
        publishable_key_masked=PaymentService.mask_key(keys["publishable_key"]) if keys.get("publishable_key") else None,
        webhook_secret_masked=PaymentService.mask_key(keys["webhook_secret"]) if keys.get("webhook_secret") else None,
        updated_at=updated_at,
        updated_by_email=updated_by_email,
    )


@router.post("/stripe/config", response_model=StripeConfigStatusResponse)
async def create_or_update_stripe_config(
    request: StripeConfigCreateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create or update Stripe configuration (encrypted storage)"""
    # Validate keys by testing the secret key
    test_result = PaymentService.test_connection(request.secret_key)
    if not test_result["success"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Stripe credentials: {test_result.get('error', 'Unknown error')}"
        )
    
    # Determine if live mode based on key prefix
    is_live_mode = request.secret_key.startswith("sk_live_")
    
    # Validate publishable key matches mode
    if is_live_mode and not request.publishable_key.startswith("pk_live_"):
        raise HTTPException(
            status_code=400,
            detail="Publishable key must be a live key (pk_live_) when using a live secret key"
        )
    if not is_live_mode and not request.publishable_key.startswith("pk_test_"):
        raise HTTPException(
            status_code=400,
            detail="Publishable key must be a test key (pk_test_) when using a test secret key"
        )
    
    # Encrypt sensitive keys
    encrypted_secret = EncryptionService.encrypt(request.secret_key)
    encrypted_webhook = None
    if request.webhook_secret:
        encrypted_webhook = EncryptionService.encrypt(request.webhook_secret)
    
    # Deactivate existing configs
    db.query(StripeConfig).filter(StripeConfig.is_active == True).update(
        {"is_active": False}
    )
    
    # Create new config
    new_config = StripeConfig(
        secret_key_encrypted=encrypted_secret,
        publishable_key=request.publishable_key,
        webhook_secret_encrypted=encrypted_webhook,
        is_active=True,
        is_live_mode=is_live_mode,
        name=request.name,
        updated_by_id=current_user.id,
    )
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    return StripeConfigStatusResponse(
        is_configured=True,
        source="database",
        is_live_mode=is_live_mode,
        config_name=new_config.name,
        config_id=str(new_config.id),
        secret_key_masked=PaymentService.mask_key(request.secret_key),
        publishable_key_masked=PaymentService.mask_key(request.publishable_key),
        webhook_secret_masked=PaymentService.mask_key(request.webhook_secret) if request.webhook_secret else None,
        updated_at=new_config.updated_at.isoformat() if new_config.updated_at else None,
        updated_by_email=current_user.email,
    )


@router.post("/stripe/config/test", response_model=StripeConfigTestResponse)
async def test_stripe_credentials(
    request: StripeConfigTestRequest,
    current_user: User = Depends(require_admin),
):
    """Test Stripe credentials without saving them"""
    result = PaymentService.test_connection(request.secret_key)
    return StripeConfigTestResponse(**result)


@router.get("/stripe/config/test-current", response_model=StripeConfigTestResponse)
async def test_current_stripe_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Test the currently active Stripe configuration (from DB or environment)"""
    keys = PaymentService.get_stripe_keys(db)
    
    if not keys.get("secret_key"):
        return StripeConfigTestResponse(
            success=False,
            error="No Stripe API key configured. Please configure Stripe credentials first."
        )
    
    result = PaymentService.test_connection(keys["secret_key"])
    # Add source information to the result
    result["config_source"] = keys.get("source", "unknown")
    return StripeConfigTestResponse(**result)


@router.delete("/stripe/config")
async def delete_stripe_config(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete the active Stripe configuration (reverts to environment variables)"""
    config = PaymentService.get_active_config(db)
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="No active Stripe configuration found in database"
        )
    
    db.delete(config)
    db.commit()
    
    return {"message": "Stripe configuration deleted. System will now use environment variables."}


@router.get("/stripe/balance", response_model=StripeBalanceResponse)
async def get_stripe_balance(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get current Stripe account balance"""
    try:
        balance = PaymentService.get_balance(db)
        return StripeBalanceResponse(**balance)
    except Exception as e:
        logger.error(f"Error getting Stripe balance: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/transactions", response_model=StripeTransactionsResponse)
async def list_stripe_transactions(
    limit: int = Query(25, ge=1, le=100),
    starting_after: Optional[str] = Query(None, description="Pagination cursor"),
    created_gte: Optional[datetime] = Query(None, description="Filter by created date (on or after)"),
    created_lte: Optional[datetime] = Query(None, description="Filter by created date (on or before)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List balance transactions from Stripe"""
    try:
        transactions = PaymentService.list_balance_transactions(
            limit=limit,
            starting_after=starting_after,
            created_gte=created_gte,
            created_lte=created_lte,
            db=db
        )
        return StripeTransactionsResponse(**transactions)
    except Exception as e:
        logger.error(f"Error listing Stripe transactions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/payments", response_model=StripePaymentIntentsResponse)
async def list_stripe_payment_intents(
    limit: int = Query(25, ge=1, le=100),
    starting_after: Optional[str] = Query(None, description="Pagination cursor"),
    created_gte: Optional[datetime] = Query(None, description="Filter by created date (on or after)"),
    created_lte: Optional[datetime] = Query(None, description="Filter by created date (on or before)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List payment intents from Stripe"""
    try:
        intents = PaymentService.list_payment_intents(
            limit=limit,
            starting_after=starting_after,
            created_gte=created_gte,
            created_lte=created_lte,
            db=db
        )
        return StripePaymentIntentsResponse(**intents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/charges", response_model=StripeChargesResponse)
async def list_stripe_charges(
    limit: int = Query(25, ge=1, le=100),
    starting_after: Optional[str] = Query(None, description="Pagination cursor"),
    created_gte: Optional[datetime] = Query(None, description="Filter by created date (on or after)"),
    created_lte: Optional[datetime] = Query(None, description="Filter by created date (on or before)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List charges from Stripe"""
    try:
        charges = PaymentService.list_charges(
            limit=limit,
            starting_after=starting_after,
            created_gte=created_gte,
            created_lte=created_lte,
            db=db
        )
        return StripeChargesResponse(**charges)
    except Exception as e:
        logger.error(f"Error listing Stripe charges: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stripe/refunds", response_model=StripeRefundsResponse)
async def list_stripe_refunds(
    limit: int = Query(25, ge=1, le=100),
    starting_after: Optional[str] = Query(None, description="Pagination cursor"),
    created_gte: Optional[datetime] = Query(None, description="Filter by created date (on or after)"),
    created_lte: Optional[datetime] = Query(None, description="Filter by created date (on or before)"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List refunds from Stripe"""
    try:
        refunds = PaymentService.list_refunds(
            limit=limit,
            starting_after=starting_after,
            created_gte=created_gte,
            created_lte=created_lte,
            db=db
        )
        return StripeRefundsResponse(**refunds)
    except Exception as e:
        logger.error(f"Error listing Stripe refunds: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/sync-descriptions")
async def sync_model_descriptions(
    all_models: bool = Query(False, description="Sync all models, even if they already have descriptions"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Sync model descriptions from OpenRouter API"""
    try:
        if all_models:
            # Sync all models
            models = db.query(Model).all()
            updated_count = 0
            errors = []
            
            from app.services.model_sync import sync_model_description
            
            for model in models:
                try:
                    result = await sync_model_description(db, model)
                    if result:
                        updated_count += 1
                except Exception as e:
                    errors.append(f"{model.name}: {str(e)}")
                    continue
            
            return {
                "success": True,
                "message": f"Synced {updated_count} model(s)",
                "updated_count": updated_count,
                "total_models": len(models),
                "errors": errors if errors else None
            }
        else:
            # Sync only models without descriptions
            updated_count = await sync_all_model_descriptions(db)
            return {
                "success": True,
                "message": f"Synced {updated_count} model(s)",
                "updated_count": updated_count
            }
    except Exception as e:
        logger.error(f"Error syncing model descriptions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/refresh")
async def refresh_cache(
    current_user: User = Depends(require_admin_flexible)
):
    """Manually refresh all caches"""
    from app.services.cache_warmer import warm_all_caches
    from app.core.cache import cache
    
    try:
        # Clear existing cache first
        await cache.clear()
        
        # Re-warm all caches
        await warm_all_caches()
        
        return {"message": "Cache refreshed successfully"}
    except Exception as e:
        logger.error(f"Failed to refresh cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh cache: {str(e)}")


@router.post("/email/test")
async def send_test_email(
    current_user: User = Depends(require_admin)
):
    """Send a test email to verify email service is working"""
    from app.services.email import EmailService
    
    try:
        success = await EmailService.send_test_email(
            to_email=current_user.email,
            user_name=current_user.name
        )
        
        if success:
            return {
                "success": True,
                "message": f"Test email sent successfully to {current_user.email}"
            }
        else:
            return {
                "success": False,
                "message": "Failed to send test email. Check email service configuration."
            }
    except Exception as e:
        logger.error(f"Failed to send test email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test email: {str(e)}"
        )


@router.get("/sponsorships", response_model=AdminSponsorshipListResponse)
async def list_admin_sponsorships(
    status: Optional[str] = Query(None, description="Filter by status"),
    request_type: Optional[str] = Query(None, description="Filter by type (sponsorship or request)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all sponsorship requests for admin management"""
    query = db.query(SponsorshipRequest).options(
        joinedload(SponsorshipRequest.user),
        joinedload(SponsorshipRequest.assigned_moderator)
    )
    
    if status:
        query = query.filter(SponsorshipRequest.status == status)
    
    if request_type:
        query = query.filter(SponsorshipRequest.request_type == request_type)
    
    query = query.order_by(desc(SponsorshipRequest.created_at))
    
    total = query.count()
    sponsorships = query.offset(offset).limit(limit).all()
    
    items = []
    for s in sponsorships:
        model_name = s.openrouter_model_id or s.custom_model_name or "Unknown"
        assigned_moderator_name = None
        if s.assigned_moderator:
            assigned_moderator_name = s.assigned_moderator.name or s.assigned_moderator.email
        
        items.append(AdminSponsorshipItem(
            id=s.id,
            request_type=s.request_type,
            model_name=model_name,
            user_id=s.user_id,
            user_name=s.user.name or s.user.email,
            user_email=s.user.email,
            message=s.message,
            status=s.status,
            payment_id=s.payment_id,
            payment_status=s.payment_status,
            created_at=s.created_at,
            reviewed_at=s.reviewed_at,
            reviewer_notes=s.reviewer_notes,
            assigned_moderator_id=s.assigned_moderator_id,
            assigned_moderator_name=assigned_moderator_name,
            assigned_at=s.assigned_at
        ))
    
    return AdminSponsorshipListResponse(items=items, total=total)


@router.get("/moderators", response_model=ModeratorListResponse)
async def list_moderators(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users with moderator permissions"""
    moderators = db.query(User).filter(
        User.can_moderate == True
    ).order_by(User.name, User.email).all()
    
    items = []
    for moderator in moderators:
        items.append(ModeratorListItem(
            id=moderator.id,
            name=moderator.name,
            email=moderator.email
        ))
    
    return ModeratorListResponse(moderators=items)


@router.post("/sponsorships/{sponsorship_id}/assign", response_model=AssignModeratorResponse)
async def assign_sponsorship_moderator(
    sponsorship_id: UUID,
    request: AssignModeratorRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign a moderator to a sponsorship request"""
    from app.services.email import EmailService
    from datetime import datetime
    
    # Get sponsorship
    sponsorship = db.query(SponsorshipRequest).options(
        joinedload(SponsorshipRequest.assigned_moderator)
    ).filter(SponsorshipRequest.id == sponsorship_id).first()
    
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship request not found")
    
    # Get moderator
    moderator = db.query(User).filter(User.id == request.moderator_id).first()
    if not moderator:
        raise HTTPException(status_code=404, detail="Moderator not found")
    
    if not moderator.can_moderate:
        raise HTTPException(
            status_code=400,
            detail="User does not have moderator permissions"
        )
    
    # Update assignment
    sponsorship.assigned_moderator_id = request.moderator_id
    sponsorship.assigned_at = datetime.utcnow()
    db.commit()
    db.refresh(sponsorship)

    ActionLogService.log_action(
        db, "sponsorship.assign", "user",
        actor_user_id=current_user.id,
        entity_type="sponsorship_request", entity_id=str(sponsorship.id),
        metadata={"moderator_id": str(request.moderator_id)}
    )
    
    # Send email notification to moderator
    model_name = sponsorship.openrouter_model_id or sponsorship.custom_model_name or "Unknown"
    try:
        await EmailService.send_sponsorship_assigned_email(
            moderator_email=moderator.email,
            moderator_name=moderator.name or moderator.email,
            model_name=model_name,
            sponsorship_id=str(sponsorship.id),
            request_type=sponsorship.request_type
        )
    except Exception as e:
        logger.warning(f"Failed to send assignment email to moderator: {e}")
        # Don't fail the assignment if email fails
    
    moderator_name = moderator.name or moderator.email
    
    return AssignModeratorResponse(
        id=sponsorship.id,
        assigned_moderator_id=sponsorship.assigned_moderator_id,
        assigned_moderator_name=moderator_name,
        assigned_at=sponsorship.assigned_at,
        message=f"Sponsorship assigned to {moderator_name}"
    )


# =============================================================================
# Contact Submissions Management Endpoints
# =============================================================================

from app.db.models.contact_submission import ContactSubmission, ContactStatus
from app.schemas.contact import (
    ContactSubmissionListItem,
    ContactSubmissionListResponse,
    ContactSubmissionDetail,
    ContactStatusUpdateRequest,
    ContactStatusUpdateResponse
)


@router.get("/contacts", response_model=ContactSubmissionListResponse)
async def list_contact_submissions(
    status: Optional[str] = Query(None, description="Filter by status: new, read, responded"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all contact form submissions (admin only)"""
    query = db.query(ContactSubmission)
    
    if status:
        query = query.filter(ContactSubmission.status == status)
    
    total = query.count()
    submissions = query.order_by(desc(ContactSubmission.created_at)).offset(offset).limit(limit).all()
    
    items = []
    for sub in submissions:
        items.append(ContactSubmissionListItem(
            id=sub.id,
            name=sub.name,
            email=sub.email,
            subject=sub.subject.value,
            message=sub.message,
            status=sub.status.value,
            admin_notes=sub.admin_notes,
            responded_at=sub.responded_at,
            responded_by=sub.responded_by,
            created_at=sub.created_at,
            updated_at=sub.updated_at
        ))
    
    return ContactSubmissionListResponse(items=items, total=total)


@router.get("/contacts/{contact_id}", response_model=ContactSubmissionDetail)
async def get_contact_submission(
    contact_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get a specific contact submission (admin only)"""
    submission = db.query(ContactSubmission).filter(ContactSubmission.id == contact_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Contact submission not found")
    
    # Get the name of who responded, if applicable
    responded_by_name = None
    if submission.responded_by:
        responder = db.query(User).filter(User.id == submission.responded_by).first()
        if responder:
            responded_by_name = responder.name or responder.email
    
    return ContactSubmissionDetail(
        id=submission.id,
        name=submission.name,
        email=submission.email,
        subject=submission.subject.value,
        message=submission.message,
        status=submission.status.value,
        admin_notes=submission.admin_notes,
        responded_at=submission.responded_at,
        responded_by=submission.responded_by,
        responded_by_name=responded_by_name,
        created_at=submission.created_at,
        updated_at=submission.updated_at
    )


@router.put("/contacts/{contact_id}/status", response_model=ContactStatusUpdateResponse)
async def update_contact_status(
    contact_id: UUID,
    request: ContactStatusUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update contact submission status (admin only)"""
    submission = db.query(ContactSubmission).filter(ContactSubmission.id == contact_id).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Contact submission not found")
    
    submission.status = request.status
    if request.admin_notes is not None:
        submission.admin_notes = request.admin_notes
    
    # Track who responded and when
    if request.status == ContactStatus.RESPONDED:
        submission.responded_at = datetime.utcnow()
        submission.responded_by = current_user.id
    
    db.commit()
    db.refresh(submission)

    ActionLogService.log_action(
        db, "contact.status_update", "user",
        actor_user_id=current_user.id,
        entity_type="contact_submission", entity_id=str(submission.id),
        metadata={"status": request.status.value}
    )
    
    return ContactStatusUpdateResponse(
        id=submission.id,
        status=submission.status.value,
        message=f"Contact submission status updated to {request.status.value}"
    )


# =============================================================================
# Notification Settings Management Endpoints
# =============================================================================

from app.db.models.notification_setting import NotificationSetting, NotificationType
from app.schemas.notification import (
    NotificationSettingItem,
    NotificationSettingsListResponse,
    NotificationSettingUpdateRequest,
    NotificationSettingUpdateResponse
)


@router.get("/notification-settings", response_model=NotificationSettingsListResponse)
async def list_notification_settings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all notification settings (admin only)"""
    settings_list = db.query(NotificationSetting).all()
    
    items = []
    for setting in settings_list:
        # Get the name of who last updated, if applicable
        updated_by_name = None
        if setting.updated_by_id:
            updater = db.query(User).filter(User.id == setting.updated_by_id).first()
            if updater:
                updated_by_name = updater.name or updater.email
        
        items.append(NotificationSettingItem(
            id=setting.id,
            notification_type=setting.notification_type.value,
            recipient_email=setting.recipient_email,
            is_enabled=setting.is_enabled,
            description=setting.description,
            updated_at=setting.updated_at,
            updated_by_id=setting.updated_by_id,
            updated_by_name=updated_by_name
        ))
    
    return NotificationSettingsListResponse(settings=items)


@router.put("/notification-settings/{notification_type}", response_model=NotificationSettingUpdateResponse)
async def update_notification_setting(
    notification_type: str,
    request: NotificationSettingUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a notification setting (admin only)"""
    # Validate notification type
    try:
        notif_type = NotificationType(notification_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid notification type. Must be one of: {', '.join([t.value for t in NotificationType])}"
        )
    
    setting = db.query(NotificationSetting).filter(
        NotificationSetting.notification_type == notif_type
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Notification setting not found")
    
    # Update fields if provided
    if request.recipient_email is not None:
        setting.recipient_email = request.recipient_email
    if request.is_enabled is not None:
        setting.is_enabled = request.is_enabled
    
    setting.updated_by_id = current_user.id
    
    db.commit()
    db.refresh(setting)
    
    return NotificationSettingUpdateResponse(
        id=setting.id,
        notification_type=setting.notification_type.value,
        recipient_email=setting.recipient_email,
        is_enabled=setting.is_enabled,
        message=f"Notification setting for {notification_type} updated successfully"
    )


# =============================================================================
# Newsletter Admin Endpoints
# =============================================================================

from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.services.newsletter import NewsletterService


@router.get("/newsletter/stats", response_model=NewsletterStatsResponse)
async def get_newsletter_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get newsletter subscriber statistics (admin only)"""
    total = db.query(NewsletterSubscriber).count()
    active = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.is_active == True
    ).count()
    unsubscribed = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.is_active == False
    ).count()
    synced = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.mailerlite_subscriber_id.isnot(None)
    ).count()

    return NewsletterStatsResponse(
        total=total,
        active=active,
        unsubscribed=unsubscribed,
        synced_to_mailerlite=synced,
        mailerlite_configured=NewsletterService.is_configured()
    )


@router.get("/newsletter/subscribers", response_model=NewsletterSubscriberListResponse)
async def list_newsletter_subscribers(
    status: Optional[str] = Query(None, description="Filter by status: active, unsubscribed"),
    search: Optional[str] = Query(None, description="Search by email"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List newsletter subscribers from platform database (admin only)"""
    query = db.query(NewsletterSubscriber)

    if status == "active":
        query = query.filter(NewsletterSubscriber.is_active == True)
    elif status == "unsubscribed":
        query = query.filter(NewsletterSubscriber.is_active == False)

    if search:
        query = query.filter(NewsletterSubscriber.email.ilike(f"%{search}%"))

    total = query.count()
    subscribers = query.order_by(desc(NewsletterSubscriber.subscribed_at)).offset(offset).limit(limit).all()

    items = [
        NewsletterSubscriberListItem(
            id=sub.id,
            email=sub.email,
            is_active=sub.is_active,
            mailerlite_subscriber_id=sub.mailerlite_subscriber_id,
            subscribed_at=sub.subscribed_at,
            unsubscribed_at=sub.unsubscribed_at,
        )
        for sub in subscribers
    ]

    return NewsletterSubscriberListResponse(items=items, total=total)


@router.get("/newsletter/subscribers/export")
async def export_newsletter_subscribers(
    status: Optional[str] = Query(None, description="Filter by status: active, unsubscribed"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Export newsletter subscribers as CSV (admin only)"""
    import csv
    import io
    from fastapi.responses import StreamingResponse

    query = db.query(NewsletterSubscriber)

    if status == "active":
        query = query.filter(NewsletterSubscriber.is_active == True)
    elif status == "unsubscribed":
        query = query.filter(NewsletterSubscriber.is_active == False)

    subscribers = query.order_by(desc(NewsletterSubscriber.subscribed_at)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["email", "status", "subscribed_at", "unsubscribed_at", "mailerlite_subscriber_id"])

    for sub in subscribers:
        writer.writerow([
            sub.email,
            "active" if sub.is_active else "unsubscribed",
            sub.subscribed_at.isoformat() if sub.subscribed_at else "",
            sub.unsubscribed_at.isoformat() if sub.unsubscribed_at else "",
            sub.mailerlite_subscriber_id or "",
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="newsletter_subscribers.csv"'},
    )


@router.get("/newsletter/subscribers/{subscriber_id}", response_model=NewsletterSubscriberDetail)
async def get_newsletter_subscriber(
    subscriber_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed newsletter subscriber info, including live MailerLite data (admin only)"""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    detail = NewsletterSubscriberDetail(
        id=subscriber.id,
        email=subscriber.email,
        is_active=subscriber.is_active,
        mailerlite_subscriber_id=subscriber.mailerlite_subscriber_id,
        subscribed_at=subscriber.subscribed_at,
        unsubscribed_at=subscriber.unsubscribed_at,
    )

    # Fetch live data from MailerLite if configured
    if NewsletterService.is_configured():
        try:
            ml_data = await NewsletterService.get_mailerlite_subscriber(subscriber.email)
            if ml_data:
                detail.mailerlite_status = ml_data.get("status")
                detail.mailerlite_subscribed_at = ml_data.get("subscribed_datetime")
                detail.mailerlite_opens_count = ml_data.get("opens_count")
                detail.mailerlite_clicks_count = ml_data.get("clicks_count")
        except Exception as e:
            logger.warning(f"Failed to fetch MailerLite data for {subscriber.email}: {e}")

    return detail


@router.get("/newsletter/mailerlite", response_model=MailerLiteSubscriberListResponse)
async def list_mailerlite_subscribers(
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(50, ge=1, le=50),
    current_user: User = Depends(require_admin),
):
    """List subscribers directly from MailerLite API (admin only)"""
    if not NewsletterService.is_configured():
        raise HTTPException(
            status_code=400,
            detail="MailerLite is not configured. Set MAILERLITE_API_KEY to enable."
        )

    raw_subscribers, next_cursor = await NewsletterService.list_mailerlite_subscribers(
        cursor=cursor, limit=limit
    )

    items = [
        MailerLiteSubscriberItem(
            id=str(sub.get("id", "")),
            email=sub.get("email", ""),
            status=sub.get("status", "unknown"),
            subscribed_at=sub.get("subscribed_datetime"),
            opens_count=sub.get("opens_count"),
            clicks_count=sub.get("clicks_count"),
        )
        for sub in raw_subscribers
    ]

    return MailerLiteSubscriberListResponse(
        items=items,
        next_cursor=next_cursor,
        has_more=next_cursor is not None,
    )


@router.post("/newsletter/subscribers/{subscriber_id}/sync")
async def sync_newsletter_subscriber(
    subscriber_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Force re-sync a subscriber to MailerLite (admin only)"""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    if not NewsletterService.is_configured():
        raise HTTPException(
            status_code=400,
            detail="MailerLite is not configured. Set MAILERLITE_API_KEY to enable."
        )

    if subscriber.is_active:
        mailerlite_id = await NewsletterService.sync_subscriber_to_mailerlite(subscriber.email)
    else:
        # For inactive subscribers, update MailerLite status to unsubscribed
        await NewsletterService.remove_subscriber_from_mailerlite(subscriber.email)
        mailerlite_id = subscriber.mailerlite_subscriber_id

    if mailerlite_id:
        subscriber.mailerlite_subscriber_id = str(mailerlite_id)
        db.commit()

    return {
        "success": True,
        "message": f"Subscriber {subscriber.email} synced to MailerLite",
        "mailerlite_subscriber_id": subscriber.mailerlite_subscriber_id,
    }


@router.delete("/newsletter/subscribers/{subscriber_id}")
async def delete_newsletter_subscriber(
    subscriber_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove a subscriber from the platform and unsubscribe from MailerLite (admin only)"""
    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.id == subscriber_id
    ).first()

    if not subscriber:
        raise HTTPException(status_code=404, detail="Subscriber not found")

    email = subscriber.email

    # Unsubscribe from MailerLite first
    if NewsletterService.is_configured():
        try:
            await NewsletterService.remove_subscriber_from_mailerlite(email)
        except Exception as e:
            logger.warning(f"Failed to remove {email} from MailerLite: {e}")

    # Remove from database
    db.delete(subscriber)
    db.commit()

    return {
        "success": True,
        "message": f"Subscriber {email} removed",
    }


# =============================================================================
# Model archive (admin-level, supports X-API-Key for scheduler access)
# =============================================================================


@router.patch("/models/{model_id}/archive")
async def archive_model(
    model_id: UUID,
    current_user: User = Depends(require_admin_flexible),
    db: Session = Depends(get_db),
):
    """Archive a model. Archived models are excluded from the leaderboard.

    Uses require_admin_flexible so the scheduler can call this with X-API-Key.
    """
    model = db.query(Model).filter(Model.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    model.is_active = False
    db.commit()
    from app.core.cache import invalidate_cache
    await invalidate_cache("leaderboard")
    return {
        "model_id": str(model.id),
        "model_id_str": model.model_id,
        "name": model.name,
        "archived": True,
        "message": f"Model '{model.name}' archived successfully",
    }
