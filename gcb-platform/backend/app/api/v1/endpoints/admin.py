"""Admin API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
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
from app.schemas.admin import (
    UserListItem,
    UserListResponse,
    UpdateUserRoleRequest,
    UpdateUserRoleResponse,
    QuestionImportRequest,
    QuestionImportResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionResponse,
    VersionCreateRequest,
    VersionPublishRequest,
    AdminStatsResponse
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
            test_count=test_count
        ))
    
    return UserListResponse(users=user_items, total=total)


@router.put("/users/{user_id}/role", response_model=UpdateUserRoleResponse)
async def update_user_role(
    user_id: UUID,
    request: UpdateUserRoleRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user role"""
    if request.role not in ["user", "moderator", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent removing last admin
    if user.role == "admin" and request.role != "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove last admin user"
            )
    
    old_role = user.role
    user.role = request.role
    db.commit()
    
    return UpdateUserRoleResponse(
        user_id=user.id,
        role=user.role,
        message=f"User role updated from {old_role} to {request.role}"
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
                if question_set.status == "locked":
                    errors.append(f"Question {idx}: question set is locked")
                    continue
                
                # Create question
                question = Question(
                    question_set_id=question_set_id,
                    tier=tier,
                    category=category,
                    content=content,
                    metadata=metadata
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
    query = db.query(Question)
    
    if question_set_id:
        query = query.filter(Question.question_set_id == question_set_id)
    if tier:
        query = query.filter(Question.tier == tier)
    if category:
        query = query.filter(Question.category == category)
    
    query = query.order_by(Question.tier, Question.category)
    
    total = query.count()
    questions = query.offset(offset).limit(limit).all()
    
    return {
        "items": [
            {
                "id": q.id,
                "question_set_id": q.question_set_id,
                "tier": q.tier,
                "category": q.category,
                "content": q.content[:200] + "..." if len(q.content) > 200 else q.content,
                "metadata": q.metadata,
                "is_locked": q.question_set.status == "locked"
            }
            for q in questions
        ],
        "total": total
    }


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get question details"""
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return QuestionResponse(
        id=question.id,
        question_set_id=question.question_set_id,
        tier=question.tier,
        category=question.category,
        content=question.content,
        metadata=question.metadata,
        is_locked=question.question_set.status == "locked"
    )


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: UUID,
    request: QuestionUpdateRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if question set is locked
    if question.question_set.status == "locked":
        raise HTTPException(status_code=400, detail="Question set is locked")
    
    if request.tier is not None:
        question.tier = request.tier
    if request.category is not None:
        question.category = request.category
    if request.content is not None:
        question.content = request.content
    if request.metadata is not None:
        question.metadata = request.metadata
    
    db.commit()
    db.refresh(question)
    
    return QuestionResponse(
        id=question.id,
        question_set_id=question.question_set_id,
        tier=question.tier,
        category=question.category,
        content=question.content,
        metadata=question.metadata,
        is_locked=question.question_set.status == "locked"
    )


@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a question"""
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if question set is locked
    if question.question_set.status == "locked":
        raise HTTPException(status_code=400, detail="Cannot delete question from locked question set")
    
    db.delete(question)
    db.commit()
    
    return {"message": "Question deleted"}


@router.post("/questions/{question_id}/approve")
async def approve_question(
    question_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Approve a question (if approval workflow exists)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # For now, just return success
    # In a full implementation, this would update an approval status field
    return {"message": "Question approved"}


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
    
    if question_set.status == "locked":
        raise HTTPException(status_code=400, detail="Version is already published")
    
    # Deactivate other active versions
    db.query(QuestionSet).filter(
        QuestionSet.status == "active"
    ).update({"status": "archived"})
    
    # Activate this version
    question_set.status = "active"
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
        }
    )
