"""Sponsorship API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from datetime import datetime

from app.core.auth import get_db, require_auth, require_moderator
from app.core.config import settings
from app.db.models.user import User
from app.db.models.sponsorship_request import SponsorshipRequest
from app.services.payment import PaymentService
from app.schemas.sponsorship import (
    CreateSponsorshipRequest,
    CreateSponsorshipResponse,
    SponsorshipItem,
    SponsorshipListResponse,
    SponsorshipQueueItem,
    SponsorshipQueueResponse,
    SponsorshipDetailResponse,
    ReviewSponsorshipRequest,
    ReviewSponsorshipResponse,
)

# User-facing sponsorship endpoints
user_router = APIRouter()

# Moderator sponsorship endpoints
moderator_router = APIRouter()

# Flat fee for sponsorship in cents
SPONSORSHIP_FEE_CENTS = 2000  # $20.00


@user_router.post("", response_model=CreateSponsorshipResponse)
async def create_sponsorship(
    request: CreateSponsorshipRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a new sponsorship or model request"""
    # Determine model name for display
    model_name = request.openrouter_model_id or request.custom_model_name or "Unknown"
    
    # For sponsorship: require payment
    if request.request_type == "sponsorship":
        # Create sponsorship request with pending_payment status
        sponsorship = SponsorshipRequest(
            user_id=current_user.id,
            request_type="sponsorship",
            openrouter_model_id=request.openrouter_model_id,
            message=request.message,
            status="pending_payment",
            payment_status="pending"
        )
        db.add(sponsorship)
        db.flush()
        
        # Create Stripe payment intent
        metadata = {
            "type": "sponsorship",
            "sponsorship_id": str(sponsorship.id),
            "user_id": str(current_user.id),
            "model_id": request.openrouter_model_id
        }
        
        try:
            payment_intent = PaymentService.create_payment_intent(
                amount=SPONSORSHIP_FEE_CENTS,
                metadata=metadata,
                customer_email=current_user.email
            )
            
            # Update sponsorship with payment info
            sponsorship.payment_id = payment_intent["id"]
            sponsorship.payment_status = payment_intent["status"]
            db.commit()
            
            return CreateSponsorshipResponse(
                id=sponsorship.id,
                request_type="sponsorship",
                model_name=model_name,
                status="pending_payment",
                payment_required=True,
                payment_intent_id=payment_intent["id"],
                client_secret=payment_intent["client_secret"],
                message="Please complete payment to submit your sponsorship request"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create payment: {str(e)}"
            )
    
    # For model request (free): create directly with pending status
    else:
        sponsorship = SponsorshipRequest(
            user_id=current_user.id,
            request_type="request",
            custom_model_name=request.custom_model_name,
            message=request.message,
            status="pending"
        )
        db.add(sponsorship)
        db.commit()
        
        return CreateSponsorshipResponse(
            id=sponsorship.id,
            request_type="request",
            model_name=model_name,
            status="pending",
            payment_required=False,
            message="Your model request has been submitted for review"
        )


@user_router.get("", response_model=SponsorshipListResponse)
async def get_user_sponsorships(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user's sponsorship requests"""
    query = db.query(SponsorshipRequest).filter(
        SponsorshipRequest.user_id == current_user.id
    ).order_by(desc(SponsorshipRequest.created_at))
    
    total = query.count()
    sponsorships = query.offset(offset).limit(limit).all()
    
    items = []
    for s in sponsorships:
        model_name = s.openrouter_model_id or s.custom_model_name or "Unknown"
        items.append(SponsorshipItem(
            id=s.id,
            request_type=s.request_type,
            model_name=model_name,
            status=s.status,
            payment_status=s.payment_status,
            created_at=s.created_at,
            reviewed_at=s.reviewed_at,
            reviewer_notes=s.reviewer_notes
        ))
    
    return SponsorshipListResponse(items=items, total=total)


# Moderator endpoints

@moderator_router.get("", response_model=SponsorshipQueueResponse)
async def get_sponsorship_queue(
    status: Optional[str] = Query(None, description="Filter by status"),
    request_type: Optional[str] = Query(None, description="Filter by type (sponsorship or request)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get sponsorship requests queue for moderation"""
    query = db.query(SponsorshipRequest)
    
    if status:
        query = query.filter(SponsorshipRequest.status == status)
    else:
        # Default: show pending requests (paid sponsorships and free requests)
        query = query.filter(SponsorshipRequest.status == "pending")
    
    if request_type:
        query = query.filter(SponsorshipRequest.request_type == request_type)
    
    query = query.order_by(SponsorshipRequest.created_at.asc())
    
    total = query.count()
    sponsorships = query.offset(offset).limit(limit).all()
    
    items = []
    for s in sponsorships:
        model_name = s.openrouter_model_id or s.custom_model_name or "Unknown"
        items.append(SponsorshipQueueItem(
            id=s.id,
            request_type=s.request_type,
            model_name=model_name,
            user_name=s.user.name or s.user.email,
            user_email=s.user.email,
            message=s.message,
            status=s.status,
            payment_status=s.payment_status,
            created_at=s.created_at
        ))
    
    return SponsorshipQueueResponse(items=items, total=total)


@moderator_router.get("/{sponsorship_id}", response_model=SponsorshipDetailResponse)
async def get_sponsorship_detail(
    sponsorship_id: UUID,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get sponsorship details for review"""
    sponsorship = db.query(SponsorshipRequest).filter(
        SponsorshipRequest.id == sponsorship_id
    ).first()
    
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship request not found")
    
    model_name = sponsorship.openrouter_model_id or sponsorship.custom_model_name or "Unknown"
    
    return SponsorshipDetailResponse(
        id=sponsorship.id,
        request_type=sponsorship.request_type,
        openrouter_model_id=sponsorship.openrouter_model_id,
        custom_model_name=sponsorship.custom_model_name,
        model_name=model_name,
        user_id=sponsorship.user_id,
        user_name=sponsorship.user.name or sponsorship.user.email,
        user_email=sponsorship.user.email,
        message=sponsorship.message,
        status=sponsorship.status,
        payment_id=sponsorship.payment_id,
        payment_status=sponsorship.payment_status,
        created_at=sponsorship.created_at,
        reviewed_at=sponsorship.reviewed_at,
        reviewer_notes=sponsorship.reviewer_notes
    )


@moderator_router.post("/{sponsorship_id}/review", response_model=ReviewSponsorshipResponse)
async def review_sponsorship(
    sponsorship_id: UUID,
    request: ReviewSponsorshipRequest,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Review (approve or reject) a sponsorship request"""
    sponsorship = db.query(SponsorshipRequest).filter(
        SponsorshipRequest.id == sponsorship_id
    ).first()
    
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship request not found")
    
    if sponsorship.status not in ["pending"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot review sponsorship with status: {sponsorship.status}"
        )
    
    # For sponsorships, verify payment was successful
    if sponsorship.request_type == "sponsorship" and sponsorship.payment_status != "succeeded":
        raise HTTPException(
            status_code=400,
            detail="Cannot approve sponsorship - payment not completed"
        )
    
    if request.action == "approve":
        sponsorship.status = "approved"
        message = "Sponsorship request approved"
    else:
        sponsorship.status = "rejected"
        message = "Sponsorship request rejected"
    
    sponsorship.reviewer_id = current_user.id
    sponsorship.reviewer_notes = request.notes
    sponsorship.reviewed_at = datetime.utcnow()
    
    db.commit()
    
    # TODO: Send email notification to user about approval/rejection
    # TODO: For approved sponsorships, trigger model test setup
    
    return ReviewSponsorshipResponse(
        id=sponsorship.id,
        status=sponsorship.status,
        message=message
    )
