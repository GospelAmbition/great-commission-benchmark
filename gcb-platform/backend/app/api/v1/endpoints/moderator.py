"""Moderator API endpoints"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from uuid import UUID
from datetime import datetime, timedelta
import random

from app.core.auth import get_db
from app.core.auth import require_moderator
from app.db.models.user import User
from app.db.models.community_submission import CommunitySubmission
from app.db.models.sponsorship_request import SponsorshipRequest
from app.db.models.question_set import QuestionSet
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.question import Question
from app.services.judge import TIER1_JUDGE_PROMPT
from app.services.submission_processor import SubmissionProcessorService
from app.schemas.moderator import (
    ModeratorActivityItem,
    ModeratorActivityResponse,
    ModeratorStatsResponse,
    CommunitySubmissionReviewRequest,
    CommunitySubmissionReviewResponse
)

router = APIRouter()


@router.get("/activity", response_model=ModeratorActivityResponse)
async def get_moderator_activity(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    moderator_id: Optional[UUID] = Query(None, description="Filter by specific moderator ID (default: all moderators)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get moderator activity history (all moderators by default, or filter by moderator_id)
    
    Returns CLI submission reviews (CommunitySubmission) and sponsorship reviews (SponsorshipRequest)
    """
    from sqlalchemy.orm import joinedload
    
    items = []
    
    # Get CLI submission reviews (CommunitySubmission with reviewer_id set)
    submission_query = db.query(CommunitySubmission).options(
        joinedload(CommunitySubmission.reviewer)
    ).filter(
        CommunitySubmission.reviewer_id.isnot(None),
        CommunitySubmission.reviewed_at.isnot(None)
    )
    
    if moderator_id:
        submission_query = submission_query.filter(CommunitySubmission.reviewer_id == moderator_id)
    
    if start_date:
        submission_query = submission_query.filter(CommunitySubmission.reviewed_at >= start_date)
    if end_date:
        submission_query = submission_query.filter(CommunitySubmission.reviewed_at <= end_date)
    
    submissions = submission_query.order_by(desc(CommunitySubmission.reviewed_at)).all()
    
    for submission in submissions:
        # Map submission status to action
        action = submission.status  # 'approved' or 'rejected'
        
        items.append(ModeratorActivityItem(
            review_id=submission.id,  # Use submission ID as review_id for CLI submissions
            test_id=None,
            submission_id=submission.id,
            model_name=submission.model_name,
            action=action,
            review_type="cli_submission",
            duration_seconds=None,
            benchmark_version=submission.question_set_version,
            created_at=submission.reviewed_at  # Use reviewed_at as the activity timestamp
        ))
    
    # Get sponsorship reviews (SponsorshipRequest with reviewer_id set)
    sponsorship_query = db.query(SponsorshipRequest).options(
        joinedload(SponsorshipRequest.reviewer)
    ).filter(
        SponsorshipRequest.reviewer_id.isnot(None),
        SponsorshipRequest.reviewed_at.isnot(None)
    )
    
    if moderator_id:
        sponsorship_query = sponsorship_query.filter(SponsorshipRequest.reviewer_id == moderator_id)
    
    if start_date:
        sponsorship_query = sponsorship_query.filter(SponsorshipRequest.reviewed_at >= start_date)
    if end_date:
        sponsorship_query = sponsorship_query.filter(SponsorshipRequest.reviewed_at <= end_date)
    
    sponsorships = sponsorship_query.order_by(desc(SponsorshipRequest.reviewed_at)).all()
    
    for sponsorship in sponsorships:
        # Map sponsorship status to action
        action = sponsorship.status  # 'approved' or 'rejected'
        
        # Get model name
        model_name = sponsorship.openrouter_model_id or sponsorship.custom_model_name or "Unknown"
        
        items.append(ModeratorActivityItem(
            review_id=sponsorship.id,  # Use sponsorship ID as review_id
            test_id=None,
            submission_id=None,
            model_name=model_name,
            action=action,
            review_type="sponsorship_review",
            duration_seconds=None,
            benchmark_version=None,  # Sponsorships don't have a benchmark version yet
            created_at=sponsorship.reviewed_at  # Use reviewed_at as the activity timestamp
        ))
    
    # Sort all items by created_at/reviewed_at descending
    items.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply pagination
    total = len(items)
    paginated_items = items[offset:offset + limit]
    
    return ModeratorActivityResponse(items=paginated_items, total=total)


@router.get("/stats", response_model=ModeratorStatsResponse)
async def get_moderator_stats(
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get moderator statistics"""
    # Personal stats - CLI submissions only
    personal_reviews = db.query(CommunitySubmission).filter(
        CommunitySubmission.reviewer_id == current_user.id,
        CommunitySubmission.reviewed_at.isnot(None)
    ).count()
    
    # For CLI submissions, we don't track agreements/disagreements
    # These fields are kept for API compatibility but will be 0
    personal_agreements = 0
    personal_disagreements = 0
    personal_agreement_rate = 0
    
    # System-wide stats - CLI submissions only
    total_reviews = db.query(CommunitySubmission).filter(
        CommunitySubmission.reviewer_id.isnot(None),
        CommunitySubmission.reviewed_at.isnot(None)
    ).count()
    
    total_pending = db.query(CommunitySubmission).filter(
        CommunitySubmission.status.in_(["pending", "reviewing"])
    ).count()
    
    system_agreements = 0
    system_disagreements = 0
    system_agreement_rate = 0
    
    # Calculate completed reviews this month (current calendar month)
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    completed_this_month = db.query(CommunitySubmission).filter(
        CommunitySubmission.reviewed_at >= month_start,
        CommunitySubmission.reviewed_at.isnot(None)
    ).count()
    
    return ModeratorStatsResponse(
        personal={
            "total_reviews": personal_reviews,
            "agreement_rate": personal_agreement_rate,
            "agreements": personal_agreements,
            "disagreements": personal_disagreements
        },
        system_wide={
            "total_reviews": total_reviews,
            "pending_tests": total_pending,
            "agreement_rate": system_agreement_rate,
            "agreements": system_agreements,
            "disagreements": system_disagreements,
            "completed_this_month": completed_this_month
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


@router.get("/community/all")
async def get_all_community_submissions(
    status: Optional[str] = Query(None, description="Filter by status (pending, reviewing, approved, rejected)"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get all community submissions (including approved/rejected) for verification"""
    query = db.query(CommunitySubmission)
    
    if status:
        query = query.filter(CommunitySubmission.status == status)
    
    query = query.order_by(CommunitySubmission.submitted_at.desc())
    
    total = query.count()
    submissions = query.offset(offset).limit(limit).all()
    
    return {
        "items": [
            {
                "submission_id": str(s.id),
                "model_name": s.model_name,
                "user_name": s.user.name or s.user.email,
                "user_email": s.user.email,
                "overall_score": s.overall_score,
                "status": s.status,
                "reviewer_id": str(s.reviewer_id) if s.reviewer_id else None,
                "reviewer_name": s.reviewer.name if s.reviewer else None,
                "reviewer_notes": s.reviewer_notes,
                "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
                "reviewed_at": s.reviewed_at.isoformat() if s.reviewed_at else None,
            }
            for s in submissions
        ],
        "total": total
    }


@router.get("/community/{submission_id}")
async def get_community_submission_detail(
    submission_id: UUID,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get community submission details for review"""
    submission = db.query(CommunitySubmission).filter(
        CommunitySubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Extract data from results_package (JSONB)
    results_package = submission.results_package or {}
    test_run = results_package.get("test_run", {})
    summary = results_package.get("summary", {})
    responses = results_package.get("responses", [])
    
    # Build response with sample responses for review
    # For CLI submissions, moderators review a sample of responses
    sample_size = min(20, len(responses))  # Review up to 20 responses
    
    import random
    if len(responses) <= sample_size:
        sample_responses = responses
    else:
        # Sample responses, ensuring we get some from each tier
        tier_responses = {1: [], 2: [], 3: []}
        for resp in responses:
            tier = resp.get("tier", 1)
            if tier in tier_responses:
                tier_responses[tier].append(resp)
        
        sample_responses = []
        responses_per_tier = max(1, sample_size // 3)  # Distribute across 3 tiers
        
        for tier in [1, 2, 3]:
            tier_list = tier_responses[tier]
            if tier_list:
                if len(tier_list) <= responses_per_tier:
                    sample_responses.extend(tier_list)
                else:
                    sample_responses.extend(random.sample(tier_list, responses_per_tier))
        
        # Fill remaining slots randomly if needed
        if len(sample_responses) < sample_size:
            remaining = [r for r in responses if r not in sample_responses]
            needed = sample_size - len(sample_responses)
            if remaining and needed > 0:
                additional = random.sample(remaining, min(needed, len(remaining)))
                sample_responses.extend(additional)
        
        # Trim to exact sample size if we oversampled
        sample_responses = sample_responses[:sample_size]
    
    return {
        "submission_id": submission.id,
        "model_name": submission.model_name,
        "user_name": submission.user.name or submission.user.email,
        "user_email": submission.user.email,
        "cli_version": submission.cli_version,
        "question_set_version": submission.question_set_version,
        "overall_score": summary.get("score", 0),
        "tier1_score": summary.get("tier_scores", {}).get("tier1", {}).get("raw", 0),
        "tier2_score": summary.get("tier_scores", {}).get("tier2", {}).get("raw", 0),
        "tier3_score": summary.get("tier_scores", {}).get("tier3", {}).get("raw", 0),
        "total_questions": summary.get("total_questions", 0),
        "status": submission.status,
        "submitted_at": submission.submitted_at.isoformat(),
        "results_package": results_package,
        "sample_responses": sample_responses,
        "sample_size": sample_size,
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
        
        # Use the submission processor service to create TestRun and Results
        processor = SubmissionProcessorService(db)
        try:
            test_run, _ = processor.create_test_run_from_submission(submission)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        db.commit()
        
        # Update model version stats for averaging (also handles cache invalidation)
        from app.services.aggregation import AggregationService
        AggregationService.update_stats_for_test_run(db, test_run)
        
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


@router.post("/community/{submission_id}/reprocess")
async def reprocess_community_submission(
    submission_id: UUID,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Reprocess an approved community submission to create TestRun records (for fixing missing leaderboard entries)"""
    submission = db.query(CommunitySubmission).filter(
        CommunitySubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission.status != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Can only reprocess approved submissions. Current status: {submission.status}"
        )
    
    # Use the submission processor service
    processor = SubmissionProcessorService(db)
    
    # Check if TestRun already exists
    existing_test_run = processor.check_existing_test_run(submission)
    if existing_test_run:
        return {
            "submission_id": str(submission.id),
            "status": "already_processed",
            "test_run_id": str(existing_test_run.id),
            "message": "TestRun already exists for this submission"
        }
    
    # Create test run from submission
    try:
        test_run, results_created = processor.create_test_run_from_submission(
            submission,
            judge_prompt=TIER1_JUDGE_PROMPT
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    db.commit()
    
    # Update model version stats for averaging (also handles cache invalidation)
    from app.services.aggregation import AggregationService
    AggregationService.update_stats_for_test_run(db, test_run)
    
    return {
        "submission_id": str(submission.id),
        "status": "processed",
        "test_run_id": str(test_run.id),
        "results_created": results_created,
        "message": f"Created TestRun with {results_created} results"
    }
