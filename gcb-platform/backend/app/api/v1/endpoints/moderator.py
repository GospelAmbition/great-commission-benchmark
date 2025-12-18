"""Moderator API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from uuid import UUID
from datetime import datetime, timedelta
import random

from app.db.base import get_db
from app.core.auth import require_moderator
from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.result import Result
from app.db.models.moderation_log import ModerationLog
from app.db.models.community_submission import CommunitySubmission
from app.services.scoring import ScoringService
from app.schemas.moderator import (
    QueueItem,
    QueueResponse,
    ReviewSubmissionRequest,
    ReviewSubmissionResponse,
    ModeratorActivityItem,
    ModeratorActivityResponse,
    ModeratorStatsResponse,
    CommunitySubmissionReviewRequest,
    CommunitySubmissionReviewResponse
)

router = APIRouter()


@router.get("/queue", response_model=QueueResponse)
async def get_moderation_queue(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get moderation queue"""
    # Query test runs that need moderation
    query = db.query(TestRun).filter(
        TestRun.status == "completed"
    )
    
    if status:
        query = query.filter(TestRun.trust_tier == status)
    else:
        # Default: show pending_review and automated (needs first review)
        query = query.filter(
            TestRun.trust_tier.in_(["pending_review", "automated"])
        )
    
    # Order by priority (pending_review first, then by creation date)
    query = query.order_by(
        desc(TestRun.trust_tier == "pending_review"),
        TestRun.created_at.asc()
    )
    
    total = query.count()
    test_runs = query.offset(offset).limit(limit).all()
    
    items = []
    for test_run in test_runs:
        # Get scores
        scores = None
        try:
            scores = ScoringService.calculate_scores(db, str(test_run.id))
        except:
            pass
        
        # Calculate priority (higher = more urgent)
        priority = 0
        if test_run.trust_tier == "pending_review":
            priority = 10
        elif test_run.trust_tier == "automated":
            priority = 5
        
        items.append(QueueItem(
            test_id=test_run.id,
            model_name=test_run.model.name,
            user_name=test_run.user.name or test_run.user.email,
            overall_score=scores["overall"] if scores else None,
            status=test_run.status,
            trust_tier=test_run.trust_tier or "automated",
            created_at=test_run.created_at,
            priority=priority
        ))
    
    return QueueResponse(items=items, total=total)


@router.get("/queue/{test_id}")
async def get_queue_item_detail(
    test_id: UUID,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get detailed information for a queue item"""
    test_run = db.query(TestRun).filter(TestRun.id == test_id).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test_run.status != "completed":
        raise HTTPException(status_code=400, detail="Test is not completed")
    
    # Get scores
    scores = ScoringService.calculate_scores(db, str(test_run.id))
    
    # Get 20 random sample verdicts for review
    all_results = db.query(Result).filter(
        Result.test_run_id == test_id
    ).all()
    
    sample_size = min(20, len(all_results))
    sample_results = random.sample(all_results, sample_size) if all_results else []
    
    # Get existing reviews
    existing_reviews = db.query(ModerationLog).filter(
        ModerationLog.test_run_id == test_id
    ).order_by(ModerationLog.created_at.desc()).all()
    
    return {
        "test_id": test_run.id,
        "model_name": test_run.model.name,
        "user_name": test_run.user.name or test_run.user.email,
        "scores": scores,
        "trust_tier": test_run.trust_tier or "automated",
        "sample_verdicts": [
            {
                "result_id": r.id,
                "question_id": str(r.question_id),
                "verdict": r.verdict,
                "response": r.response[:200] + "..." if len(r.response) > 200 else r.response,
                "reasoning": r.reasoning[:200] + "..." if r.reasoning and len(r.reasoning) > 200 else r.reasoning
            }
            for r in sample_results
        ],
        "existing_reviews": [
            {
                "review_id": r.id,
                "moderator_name": r.moderator.name or r.moderator.email,
                "action": r.action,
                "created_at": r.created_at.isoformat(),
                "notes": r.notes
            }
            for r in existing_reviews
        ]
    }


@router.post("/reviews", response_model=ReviewSubmissionResponse)
async def submit_review(
    request: ReviewSubmissionRequest,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Submit a moderation review"""
    test_run = db.query(TestRun).filter(TestRun.id == request.test_id).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test_run.status != "completed":
        raise HTTPException(status_code=400, detail="Test is not completed")
    
    # Calculate agreement statistics
    agreements = sum(1 for v in request.verdict_reviews if v.verdict == "agree")
    disagreements = sum(1 for v in request.verdict_reviews if v.verdict == "disagree")
    total_reviews = len(request.verdict_reviews)
    
    # Create moderation log
    moderation_log = ModerationLog(
        test_run_id=test_run.id,
        moderator_id=current_user.id,
        action=request.overall_assessment,
        sample_size=total_reviews,
        agreements=agreements,
        disagreements=disagreements,
        notes=request.notes
    )
    db.add(moderation_log)
    
    # Update trust tier based on review count
    review_count = db.query(ModerationLog).filter(
        ModerationLog.test_run_id == test_run.id
    ).count()
    
    if review_count == 1:
        test_run.trust_tier = "reviewed"
    elif review_count >= 3:
        test_run.trust_tier = "validated"
    
    # Check if concerns require second review
    requires_second_review = False
    if request.overall_assessment == "concerns":
        # Check if this is the first "concerns" review
        concerns_count = db.query(ModerationLog).filter(
            ModerationLog.test_run_id == test_run.id,
            ModerationLog.action == "concerns"
        ).count()
        
        if concerns_count == 1:
            requires_second_review = True
            test_run.trust_tier = "pending_review"
    
    # Escalation handling
    if request.overall_assessment == "escalated":
        test_run.trust_tier = "pending_review"
        test_run.admin_notes = f"Escalated by moderator {current_user.name or current_user.email}: {request.notes}"
        # TODO: Send notification to admin committee
    
    db.commit()
    
    return ReviewSubmissionResponse(
        review_id=moderation_log.id,
        test_id=test_run.id,
        trust_tier=test_run.trust_tier,
        requires_second_review=requires_second_review
    )


@router.get("/activity", response_model=ModeratorActivityResponse)
async def get_moderator_activity(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get moderator activity history"""
    query = db.query(ModerationLog).filter(
        ModerationLog.moderator_id == current_user.id
    )
    
    if start_date:
        query = query.filter(ModerationLog.created_at >= start_date)
    if end_date:
        query = query.filter(ModerationLog.created_at <= end_date)
    
    query = query.order_by(desc(ModerationLog.created_at))
    
    total = query.count()
    logs = query.offset(offset).limit(limit).all()
    
    items = []
    for log in logs:
        # Calculate duration (simplified - would need start time tracking)
        duration_seconds = None
        
        items.append(ModeratorActivityItem(
            review_id=log.id,
            test_id=log.test_run_id,
            model_name=log.test_run.model.name,
            action=log.action,
            duration_seconds=duration_seconds,
            created_at=log.created_at
        ))
    
    return ModeratorActivityResponse(items=items, total=total)


@router.get("/stats", response_model=ModeratorStatsResponse)
async def get_moderator_stats(
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get moderator statistics"""
    # Personal stats
    personal_reviews = db.query(ModerationLog).filter(
        ModerationLog.moderator_id == current_user.id
    ).count()
    
    personal_agreements = db.query(func.sum(ModerationLog.agreements)).filter(
        ModerationLog.moderator_id == current_user.id
    ).scalar() or 0
    
    personal_disagreements = db.query(func.sum(ModerationLog.disagreements)).filter(
        ModerationLog.moderator_id == current_user.id
    ).scalar() or 0
    
    personal_total = personal_agreements + personal_disagreements
    personal_agreement_rate = (personal_agreements / personal_total * 100) if personal_total > 0 else 0
    
    # System-wide stats
    total_reviews = db.query(ModerationLog).count()
    total_pending = db.query(TestRun).filter(
        TestRun.status == "completed",
        TestRun.trust_tier.in_(["pending_review", "automated"])
    ).count()
    
    system_agreements = db.query(func.sum(ModerationLog.agreements)).scalar() or 0
    system_disagreements = db.query(func.sum(ModerationLog.disagreements)).scalar() or 0
    system_total = system_agreements + system_disagreements
    system_agreement_rate = (system_agreements / system_total * 100) if system_total > 0 else 0
    
    return ModeratorStatsResponse(
        personal={
            "total_reviews": personal_reviews,
            "agreement_rate": round(personal_agreement_rate, 2),
            "agreements": personal_agreements,
            "disagreements": personal_disagreements
        },
        system_wide={
            "total_reviews": total_reviews,
            "pending_tests": total_pending,
            "agreement_rate": round(system_agreement_rate, 2),
            "agreements": system_agreements,
            "disagreements": system_disagreements
        }
    )


@router.get("/community")
async def get_community_submission_queue(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get community submission review queue"""
    query = db.query(CommunitySubmission)
    
    if status:
        query = query.filter(CommunitySubmission.status == status)
    else:
        query = query.filter(CommunitySubmission.status.in_(["pending", "reviewing"]))
    
    query = query.order_by(CommunitySubmission.submitted_at.asc())
    
    total = query.count()
    submissions = query.offset(offset).limit(limit).all()
    
    return {
        "items": [
            {
                "submission_id": s.id,
                "model_name": s.model_name,
                "user_name": s.user.name or s.user.email,
                "overall_score": s.overall_score,
                "status": s.status,
                "submitted_at": s.submitted_at.isoformat()
            }
            for s in submissions
        ],
        "total": total
    }


@router.post("/community/{submission_id}/review", response_model=CommunitySubmissionReviewResponse)
async def review_community_submission(
    submission_id: UUID,
    request: CommunitySubmissionReviewRequest,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Review a community submission"""
    submission = db.query(CommunitySubmission).filter(
        CommunitySubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission.status not in ["pending", "reviewing"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot review submission with status: {submission.status}"
        )
    
    from datetime import datetime
    
    if request.action == "approve":
        submission.status = "approved"
        submission.reviewer_id = current_user.id
        submission.reviewer_notes = request.notes
        submission.reviewed_at = datetime.utcnow()
        
        # TODO: Create test run from submission and add to leaderboard
        # For now, just mark as approved
        
        db.commit()
        
        # Send approval email
        from app.services.email import EmailService
        await EmailService.send_submission_approved_email(
            submission.user.email,
            str(submission.id),
            submission.model_name
        )
        
        return CommunitySubmissionReviewResponse(
            submission_id=submission.id,
            status="approved",
            message="Submission approved and will appear on leaderboard"
        )
    
    elif request.action == "reject":
        submission.status = "rejected"
        submission.reviewer_id = current_user.id
        submission.reviewer_notes = request.notes
        submission.reviewed_at = datetime.utcnow()
        
        db.commit()
        
        # Send rejection email
        from app.services.email import EmailService
        await EmailService.send_submission_rejected_email(
            submission.user.email,
            str(submission.id),
            submission.model_name,
            request.notes
        )
        
        return CommunitySubmissionReviewResponse(
            submission_id=submission.id,
            status="rejected",
            message="Submission rejected"
        )
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'approve' or 'reject'")
