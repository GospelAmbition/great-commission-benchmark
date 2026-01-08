"""User API endpoints"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db
from app.core.auth import require_auth
from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.community_submission import CommunitySubmission
from app.db.models.result import Result
from app.db.models.question import Question
from app.services.scoring import ScoringService
from app.schemas.user import (
    UserProfileResponse,
    UserProfile,
    UserStats,
    UpdateProfileRequest,
    UserTestsResponse,
    TestListItem,
    UserSubmissionsResponse,
    SubmissionListItem,
    UserActivityResponse,
    ActivityItem,
    NotificationPreferencesResponse,
    NotificationPreferences
)

router = APIRouter()


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    # Calculate stats
    test_runs = db.query(TestRun).filter(TestRun.user_id == current_user.id).all()
    
    stats = UserStats(
        total_tests=len(test_runs),
        completed_tests=sum(1 for t in test_runs if t.status == "completed"),
        pending_tests=sum(1 for t in test_runs if t.status == "pending_payment"),
        running_tests=sum(1 for t in test_runs if t.status == "running"),
        total_submissions=db.query(CommunitySubmission).filter(
            CommunitySubmission.user_id == current_user.id
        ).count(),
        approved_submissions=db.query(CommunitySubmission).filter(
            CommunitySubmission.user_id == current_user.id,
            CommunitySubmission.status == "approved"
        ).count(),
        total_contribution=sum(float(t.total_cost or 0) for t in test_runs)
    )
    
    return UserProfileResponse(
        user=UserProfile(
            id=current_user.id,
            auth0_id=current_user.auth0_id,
            email=current_user.email,
            name=current_user.name,
            role=current_user.role,
            organization=None,  # DEFERRED: Organization field not yet in User model schema
            tester_agreement_accepted=current_user.tester_agreement_accepted,
            created_at=current_user.created_at
        ),
        stats=stats
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if request.name is not None:
        current_user.name = request.name
    
    # DEFERRED: Organization field support
    # When the User model is updated with an organization field, enable this:
    # if request.organization is not None:
    #     current_user.organization = request.organization
    
    db.commit()
    db.refresh(current_user)
    
    # Return updated profile
    return await get_profile(current_user, db)


@router.get("/tests", response_model=UserTestsResponse)
async def get_user_tests(
    status: Optional[str] = Query(None),
    model_id: Optional[UUID] = Query(None),
    version: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("created_at", regex="^(created_at|completed_at|score)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user's test run history"""
    query = db.query(TestRun).filter(TestRun.user_id == current_user.id)
    
    if status:
        query = query.filter(TestRun.status == status)
    
    if model_id:
        query = query.filter(TestRun.model_id == model_id)
    
    # Apply sorting
    if sort == "created_at":
        query = query.order_by(TestRun.created_at.desc() if order == "desc" else TestRun.created_at.asc())
    elif sort == "completed_at":
        query = query.order_by(TestRun.completed_at.desc() if order == "desc" else TestRun.completed_at.asc())
    
    test_runs = query.offset(offset).limit(limit).all()
    total = query.count()
    
    # Build test list items
    tests = []
    for test_run in test_runs:
        scores = None
        if test_run.status == "completed":
            try:
                scores_data = ScoringService.calculate_scores(db, str(test_run.id))
                scores = {
                    "overall": scores_data["overall"],
                    "tier1": scores_data["tier1"],
                    "tier2": scores_data["tier2"],
                    "tier3": scores_data["tier3"]
                }
            except:
                pass
        
        # Calculate progress
        completed_questions = db.query(Result).filter(Result.test_run_id == test_run.id).count()
        # Get actual total from question_set
        question_set_total = db.query(Question).filter(
            Question.question_set_id == test_run.question_set_id
        ).count()
        progress = {
            "completed": completed_questions,
            "total": question_set_total,
            "percentage": int((completed_questions / question_set_total) * 100) if question_set_total > 0 else 0
        }
        
        tests.append(TestListItem(
            id=test_run.id,
            model={
                "id": str(test_run.model.id),
                "name": test_run.model.name,
                "provider": test_run.model.provider
            },
            status=test_run.status,
            payment_status=test_run.payment_status or "pending",
            scores=scores,
            progress=progress,
            benchmark_version=test_run.question_set.semantic_version,
            created_at=test_run.created_at,
            started_at=test_run.started_at,
            completed_at=test_run.completed_at,
            trust_tier=test_run.trust_tier,
            leaderboard_rank=None  # DEFERRED: Rank calculation would require additional DB queries per test
        ))
    
    return UserTestsResponse(
        tests=tests,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (offset + limit) < total
        }
    )


@router.get("/tests/{test_id}")
async def get_test_detail(
    test_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get detailed test run information"""
    test_run = db.query(TestRun).filter(
        TestRun.id == test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    scores = None
    if test_run.status == "completed":
        try:
            scores_data = ScoringService.calculate_scores(db, str(test_run.id))
            scores = scores_data
        except:
            pass
    
    return {
        "test": {
            "id": str(test_run.id),
            "model": {
                "id": str(test_run.model.id),
                "name": test_run.model.name,
                "provider": test_run.model.provider,
                "model_id": test_run.model.model_id
            },
            "status": test_run.status,
            "payment": {
                "status": test_run.payment_status or "pending",
                "amount": float(test_run.total_cost or 0),
                "currency": "USD"
            },
            "scores": scores,
            "benchmark_version": test_run.question_set.semantic_version,
            "created_at": test_run.created_at.isoformat(),
            "started_at": test_run.started_at.isoformat() if test_run.started_at else None,
            "completed_at": test_run.completed_at.isoformat() if test_run.completed_at else None,
            "trust_tier": test_run.trust_tier
        }
    }


@router.get("/submissions", response_model=UserSubmissionsResponse)
async def get_user_submissions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user's community submissions"""
    submissions = db.query(CommunitySubmission).filter(
        CommunitySubmission.user_id == current_user.id
    ).order_by(CommunitySubmission.submitted_at.desc()).offset(offset).limit(limit).all()
    
    total = db.query(CommunitySubmission).filter(
        CommunitySubmission.user_id == current_user.id
    ).count()
    
    submission_items = []
    for sub in submissions:
        submission_items.append(SubmissionListItem(
            id=sub.id,
            model_name=sub.model_name or "Unknown",
            model_provider="Unknown",  # Not stored in model
            status=sub.status,
            submitted_at=sub.submitted_at,
            reviewed_at=sub.reviewed_at,
            reviewer_notes=sub.reviewer_notes
        ))
    
    return UserSubmissionsResponse(
        submissions=submission_items,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": total,
            "has_more": (offset + limit) < total
        }
    )


@router.get("/submissions/{submission_id}")
async def get_user_submission_detail(
    submission_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get detailed submission information for the current user"""
    submission = db.query(CommunitySubmission).filter(
        CommunitySubmission.id == submission_id,
        CommunitySubmission.user_id == current_user.id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Extract summary from results_package
    results_package = submission.results_package or {}
    summary = results_package.get("summary", {})
    tier_scores = summary.get("tier_scores", {})
    test_run = results_package.get("test_run", {})
    
    # Get responses for display
    responses = results_package.get("responses", [])
    
    return {
        "id": str(submission.id),
        "model_name": submission.model_name,
        "status": submission.status,
        "cli_version": submission.cli_version,
        "question_set_version": submission.question_set_version,
        "overall_score": submission.overall_score or summary.get("score", 0),
        "tier1_score": submission.tier1_score or tier_scores.get("tier1", {}).get("raw", 0),
        "tier2_score": submission.tier2_score or tier_scores.get("tier2", {}).get("raw", 0),
        "tier3_score": submission.tier3_score or tier_scores.get("tier3", {}).get("raw", 0),
        "total_questions": summary.get("total_questions", len(responses)),
        "verdict_counts": summary.get("verdict_counts", {}),
        "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
        "reviewed_at": submission.reviewed_at.isoformat() if submission.reviewed_at else None,
        "reviewer_notes": submission.reviewer_notes,
        "judge_model": test_run.get("judge_model"),
        "backend": test_run.get("backend"),
        "completed_at": test_run.get("completed_at"),
        "responses": responses,
        "fee_waived": submission.fee_waived
    }


@router.get("/activity", response_model=UserActivityResponse)
async def get_user_activity(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user activity feed"""
    activities = []
    
    # Get recent test runs
    test_runs = db.query(TestRun).filter(
        TestRun.user_id == current_user.id
    ).order_by(TestRun.created_at.desc()).limit(limit).all()
    
    for test_run in test_runs:
        activities.append(ActivityItem(
            type="test_created",
            timestamp=test_run.created_at,
            title=f"Test created for {test_run.model.name}",
            description=f"Test run {test_run.id} created",
            link=f"/tests/{test_run.id}"
        ))
        
        if test_run.completed_at:
            activities.append(ActivityItem(
                type="test_completed",
                timestamp=test_run.completed_at,
                title=f"Test completed for {test_run.model.name}",
                description=f"Test run {test_run.id} completed",
                link=f"/tests/{test_run.id}"
            ))
    
    # Sort by timestamp descending
    activities.sort(key=lambda a: a.timestamp, reverse=True)
    
    return UserActivityResponse(activities=activities[:limit])


@router.get("/notifications", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get notification preferences"""
    from app.db.models.notification_preference import NotificationPreference
    
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        # Create defaults
        prefs = NotificationPreference(
            user_id=current_user.id,
            test_completion=True,
            publication=True,
            moderation_updates=True,
            newsletter=False
        )
        db.add(prefs)
        db.commit()
    
    return NotificationPreferencesResponse(
        preferences=NotificationPreferences(
            test_completed=prefs.test_completion,
            test_failed=prefs.test_completion,  # Map to test_completion
            submission_approved=prefs.publication,
            submission_rejected=prefs.publication,  # Map to publication
            payment_confirmation=prefs.moderation_updates,  # Map to moderation_updates
            newsletter=prefs.newsletter
        )
    )


@router.put("/notifications", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update notification preferences"""
    from app.db.models.notification_preference import NotificationPreference
    
    prefs = db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)
    
    prefs.test_completion = preferences.test_completed
    prefs.publication = preferences.submission_approved  # Map to publication
    prefs.moderation_updates = preferences.payment_confirmation  # Map to moderation_updates
    prefs.newsletter = preferences.newsletter
    
    db.commit()
    db.refresh(prefs)
    
    return NotificationPreferencesResponse(
        preferences=NotificationPreferences(
            test_completed=prefs.test_completion,
            test_failed=prefs.test_completion,  # Map to test_completion
            submission_approved=prefs.publication,
            submission_rejected=prefs.publication,  # Map to publication
            payment_confirmation=prefs.moderation_updates,  # Map to moderation_updates
            newsletter=prefs.newsletter
        )
    )


@router.post("/tester-agreement/accept")
async def accept_tester_agreement(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Accept the tester agreement"""
    if current_user.tester_agreement_accepted:
        return {"message": "Agreement already accepted", "accepted": True}
    
    current_user.tester_agreement_accepted = True
    current_user.tester_agreement_accepted_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Tester agreement accepted", "accepted": True}