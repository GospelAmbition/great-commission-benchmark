"""User API endpoints"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db
from app.core.auth import require_auth
from app.db.models.user import User
from app.db.models.community_submission import CommunitySubmission
from app.db.models.sponsorship_request import SponsorshipRequest
from app.schemas.user import (
    UserProfileResponse,
    UserProfile,
    UserStats,
    UpdateProfileRequest,
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
    # Calculate stats (platform tests removed - only CLI submissions now)
    stats = UserStats(
        total_tests=0,
        completed_tests=0,
        pending_tests=0,
        running_tests=0,
        total_submissions=db.query(CommunitySubmission).filter(
            CommunitySubmission.user_id == current_user.id
        ).count(),
        approved_submissions=db.query(CommunitySubmission).filter(
            CommunitySubmission.user_id == current_user.id,
            CommunitySubmission.status == "approved"
        ).count(),
        total_contribution=0  # Platform tests removed - contribution tracking no longer applies
    )
    
    from app.core.auth import has_permission
    
    return UserProfileResponse(
        user=UserProfile(
            id=current_user.id,
            auth0_id=current_user.auth0_id,
            email=current_user.email,
            name=current_user.name,
            role=current_user.role,
            organization=None,  # DEFERRED: Organization field not yet in User model schema
            tester_agreement_accepted=current_user.tester_agreement_accepted,
            created_at=current_user.created_at,
            can_view_benchmark=has_permission(current_user, "can_view_benchmark"),
            can_edit_benchmark=has_permission(current_user, "can_edit_benchmark"),
            can_moderate=has_permission(current_user, "can_moderate"),
            can_manage_blog=has_permission(current_user, "can_manage_blog"),
            can_admin=has_permission(current_user, "can_admin")
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


@router.get("/submissions", response_model=UserSubmissionsResponse)
async def get_user_submissions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user's community submissions and sponsorship requests"""
    # Get community submissions
    community_submissions = db.query(CommunitySubmission).filter(
        CommunitySubmission.user_id == current_user.id
    ).all()
    
    # Get sponsorship requests
    sponsorship_requests = db.query(SponsorshipRequest).filter(
        SponsorshipRequest.user_id == current_user.id
    ).all()
    
    submission_items = []
    
    # Add community submissions
    for sub in community_submissions:
        submission_items.append(SubmissionListItem(
            id=sub.id,
            model_name=sub.model_name or "Unknown",
            model_provider="Unknown",  # Not stored in model
            status=sub.status,
            submitted_at=sub.submitted_at,
            reviewed_at=sub.reviewed_at,
            reviewer_notes=sub.reviewer_notes,
            submission_type="community",
            payment_status=None
        ))
    
    # Add sponsorship requests
    for sp in sponsorship_requests:
        model_name = sp.openrouter_model_id or sp.custom_model_name or "Unknown"
        submission_items.append(SubmissionListItem(
            id=sp.id,
            model_name=model_name,
            model_provider="Unknown",  # Could extract from openrouter_model_id if needed
            status=sp.status,
            submitted_at=sp.created_at,
            reviewed_at=sp.reviewed_at,
            reviewer_notes=sp.reviewer_notes,
            submission_type="sponsorship",
            payment_status=sp.payment_status
        ))
    
    # Sort by submitted_at (most recent first) and apply pagination
    submission_items.sort(key=lambda x: x.submitted_at, reverse=True)
    
    total = len(submission_items)
    paginated_items = submission_items[offset:offset + limit]
    
    return UserSubmissionsResponse(
        submissions=paginated_items,
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
    # Platform tests removed - activity feed now only includes CLI submissions
    # CLI submission activities are handled in the submissions endpoint
    activities = []
    
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