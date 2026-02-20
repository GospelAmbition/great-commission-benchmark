"""Sponsorship API endpoints"""
from typing import Optional
from decimal import Decimal
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, or_, and_
from uuid import UUID
from datetime import datetime

from app.core.auth import get_db, require_auth, require_moderator
from app.core.config import settings
from app.db.models.user import User
from app.db.models.sponsorship_request import SponsorshipRequest
from app.db.models.notification_setting import NotificationSetting, NotificationType
from app.services.payment import PaymentService
from app.services.pricing import PricingService
from app.services.email import EmailService
from app.services.action_log import ActionLogService
from app.schemas.sponsorship import (
    CreateSponsorshipRequest,
    CreateSponsorshipResponse,
    CostBreakdown,
    SponsorshipItem,
    SponsorshipListResponse,
    SponsorshipQueueItem,
    SponsorshipQueueResponse,
    SponsorshipDetailResponse,
    ReviewSponsorshipRequest,
    ReviewSponsorshipResponse,
)

logger = logging.getLogger(__name__)

# User-facing sponsorship endpoints
user_router = APIRouter()

# Moderator sponsorship endpoints
moderator_router = APIRouter()

# Fallback flat fee for sponsorship in cents (used if pricing calculation fails)
FALLBACK_FEE_CENTS = 2000  # $20.00


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
        # Calculate sponsorship cost based on model pricing and question tokens
        cost_breakdown = None
        payment_amount = Decimal(FALLBACK_FEE_CENTS) / 100  # Default fallback
        
        try:
            cost_data = await PricingService.calculate_sponsorship_cost(
                model_id=request.openrouter_model_id,
                db=db
            )
            payment_amount = cost_data["total"]
            
            # Convert to CostBreakdown schema
            cost_breakdown = CostBreakdown(
                input_tokens=cost_data["input_tokens"],
                estimated_output_tokens=cost_data["estimated_output_tokens"],
                input_cost=float(cost_data["input_cost"]),
                output_cost=float(cost_data["output_cost"]),
                base_fee=float(cost_data["base_fee"]),
                total=float(cost_data["total"]),
                prompt_cost_per_token=float(cost_data["prompt_cost_per_token"]),
                completion_cost_per_token=float(cost_data["completion_cost_per_token"]),
                question_count=cost_data["question_count"],
                version=cost_data["version"],
            )
            logger.info(f"Calculated sponsorship cost for {model_name}: ${payment_amount}")
        except Exception as e:
            logger.warning(f"Failed to calculate sponsorship cost for {model_name}: {e}")
            # Fall back to flat fee if pricing calculation fails
            payment_amount = Decimal(FALLBACK_FEE_CENTS) / 100
        
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
                amount=payment_amount,
                metadata=metadata,
                customer_email=current_user.email,
                db=db  # Pass db session to use database config
            )
            
            # Update sponsorship with payment info
            sponsorship.payment_id = payment_intent["id"]
            sponsorship.payment_status = payment_intent["status"]
            
            # For test mode: if payment is already succeeded, automatically mark as ready for moderation
            # This simulates the webhook behavior for testing purposes
            keys = PaymentService.get_stripe_keys(db)
            is_test_mode = keys.get("secret_key", "").startswith("sk_test_")
            
            if is_test_mode and payment_intent["status"] == "succeeded":
                # Simulate successful payment - update status to pending for moderation
                sponsorship.payment_status = "succeeded"
                sponsorship.status = "pending"
                logger.info(f"Test mode: Payment already succeeded, sponsorship {sponsorship.id} marked as pending for moderation")
                
                # Send notification email for test mode auto-success
                try:
                    notification_setting = db.query(NotificationSetting).filter(
                        NotificationSetting.notification_type == NotificationType.SPONSORSHIP
                    ).first()
                    
                    if notification_setting and notification_setting.is_enabled and notification_setting.recipient_email:
                        await EmailService.send_sponsorship_request_notification_email(
                            admin_email=notification_setting.recipient_email,
                            requester_name=current_user.name or current_user.email,
                            requester_email=current_user.email,
                            model_name=model_name,
                            request_type="sponsorship",
                            message=request.message,
                            sponsorship_id=str(sponsorship.id)
                        )
                except Exception as e:
                    logger.warning(f"Failed to send sponsorship notification email: {e}")
            
            db.commit()

            ActionLogService.log_action(
                db, "sponsorship.create", "user",
                actor_user_id=current_user.id,
                entity_type="sponsorship_request", entity_id=str(sponsorship.id),
                metadata={"request_type": "sponsorship", "model_name": model_name}
            )
            
            # Determine response status and message based on whether payment was auto-completed
            response_status = "pending" if (is_test_mode and payment_intent["status"] == "succeeded") else "pending_payment"
            response_message = (
                "Payment successful! Your sponsorship request is pending moderation."
                if (is_test_mode and payment_intent["status"] == "succeeded")
                else "Please complete payment to submit your sponsorship request"
            )
            
            return CreateSponsorshipResponse(
                id=sponsorship.id,
                request_type="sponsorship",
                model_name=model_name,
                status=response_status,
                payment_required=not (is_test_mode and payment_intent["status"] == "succeeded"),
                payment_intent_id=payment_intent["id"],
                client_secret=payment_intent["client_secret"],
                message=response_message,
                cost_breakdown=cost_breakdown
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
        
        # Send notification email to designated recipient for model requests
        try:
            notification_setting = db.query(NotificationSetting).filter(
                NotificationSetting.notification_type == NotificationType.SPONSORSHIP
            ).first()
            
            if notification_setting and notification_setting.is_enabled and notification_setting.recipient_email:
                await EmailService.send_sponsorship_request_notification_email(
                    admin_email=notification_setting.recipient_email,
                    requester_name=current_user.name or current_user.email,
                    requester_email=current_user.email,
                    model_name=model_name,
                    request_type="request",
                    message=request.message,
                    sponsorship_id=str(sponsorship.id)
                )
        except Exception as e:
            # Log error but don't fail the request submission
            logger.warning(f"Failed to send sponsorship request notification email: {e}")

        ActionLogService.log_action(
            db, "sponsorship.create", "user",
            actor_user_id=current_user.id,
            entity_type="sponsorship_request", entity_id=str(sponsorship.id),
            metadata={"request_type": "request", "model_name": model_name}
        )
        
        return CreateSponsorshipResponse(
            id=sponsorship.id,
            request_type="request",
            model_name=model_name,
            status="pending",
            payment_required=False,
            message="Your model request has been submitted for review"
        )


@user_router.get("/estimate-cost", response_model=CostBreakdown)
async def estimate_sponsorship_cost(
    model_id: str = Query(..., description="OpenRouter model ID"),
    db: Session = Depends(get_db)
):
    """
    Estimate the cost of sponsoring a model test.
    
    Returns a cost breakdown including:
    - Input token cost (based on current version's questions)
    - Estimated output token cost (with 10% margin)
    - Base fee ($20)
    - Total cost
    
    This endpoint does not require authentication and can be used
    to preview costs before initiating a sponsorship request.
    """
    try:
        cost_data = await PricingService.calculate_sponsorship_cost(
            model_id=model_id,
            db=db
        )
        
        return CostBreakdown(
            input_tokens=cost_data["input_tokens"],
            estimated_output_tokens=cost_data["estimated_output_tokens"],
            input_cost=float(cost_data["input_cost"]),
            output_cost=float(cost_data["output_cost"]),
            base_fee=float(cost_data["base_fee"]),
            total=float(cost_data["total"]),
            prompt_cost_per_token=float(cost_data["prompt_cost_per_token"]),
            completion_cost_per_token=float(cost_data["completion_cost_per_token"]),
            question_count=cost_data["question_count"],
            version=cost_data["version"],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to estimate sponsorship cost for {model_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate cost estimate. Please try again later."
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


@user_router.get("/{sponsorship_id}", response_model=SponsorshipDetailResponse)
async def get_user_sponsorship_detail(
    sponsorship_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user's own sponsorship request details"""
    sponsorship = db.query(SponsorshipRequest).filter(
        SponsorshipRequest.id == sponsorship_id
    ).first()
    
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship request not found")
    
    # Users can only view their own sponsorships
    if sponsorship.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only view your own sponsorship requests")
    
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


@user_router.post("/{sponsorship_id}/check-payment")
async def check_payment_status(
    sponsorship_id: UUID,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """
    Check payment intent status and update sponsorship if payment succeeded.
    This is useful in test mode to immediately update status without waiting for webhook.
    """
    sponsorship = db.query(SponsorshipRequest).filter(
        SponsorshipRequest.id == sponsorship_id
    ).first()
    
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship request not found")
    
    # Users can only check their own sponsorships
    if sponsorship.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only check your own sponsorship requests")
    
    if not sponsorship.payment_id:
        raise HTTPException(status_code=400, detail="No payment associated with this sponsorship")
    
    # Check if we're in test mode
    keys = PaymentService.get_stripe_keys(db)
    is_test_mode = keys.get("secret_key", "").startswith("sk_test_")
    
    if not is_test_mode:
        # In live mode, rely on webhooks
        return {
            "status": sponsorship.status,
            "payment_status": sponsorship.payment_status,
            "updated": False,
            "message": "In live mode, payment status is updated via webhooks"
        }
    
    # In test mode, check payment intent status
    try:
        payment_intent = PaymentService.get_payment_intent(sponsorship.payment_id, db=db)
        
        # If payment succeeded and sponsorship is still pending payment, update it
        if payment_intent["status"] == "succeeded" and sponsorship.status == "pending_payment":
            sponsorship.payment_status = "succeeded"
            sponsorship.status = "pending"
            db.commit()
            logger.info(f"Test mode: Payment {sponsorship.payment_id} succeeded, sponsorship {sponsorship.id} updated to pending")
            
            return {
                "status": sponsorship.status,
                "payment_status": sponsorship.payment_status,
                "updated": True,
                "message": "Payment confirmed! Sponsorship is now pending moderation."
            }
        else:
            return {
                "status": sponsorship.status,
                "payment_status": sponsorship.payment_status,
                "updated": False,
                "message": f"Payment status: {payment_intent['status']}"
            }
    except Exception as e:
        logger.error(f"Failed to check payment status for sponsorship {sponsorship_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check payment status: {str(e)}"
        )


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
    query = db.query(SponsorshipRequest).options(
        joinedload(SponsorshipRequest.user),
        joinedload(SponsorshipRequest.assigned_moderator)
    )
    
    if status:
        query = query.filter(SponsorshipRequest.status == status)
    else:
        # Default: show pending requests (paid sponsorships and free requests)
        # Include:
        # 1. Sponsorships with status="pending" (ready for review)
        # 2. Sponsorships with status="pending_payment" that have payment_status="succeeded" (webhook updated payment but not status)
        # 3. Sponsorships with status="pending_payment" that have a payment_id set but payment_status is None or "pending"
        #    (payment was initiated, webhook may not have fired yet - exclude failed payments)
        # This ensures all sponsorships that should be reviewed are visible, even if webhook processing failed
        query = query.filter(
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
        )
    
    if request_type:
        query = query.filter(SponsorshipRequest.request_type == request_type)
    
    query = query.order_by(SponsorshipRequest.created_at.asc())
    
    total = query.count()
    sponsorships = query.offset(offset).limit(limit).all()
    
    # In test mode, check Stripe for any sponsorships with payment_id but unclear status
    # This helps catch cases where payment succeeded but webhook didn't fire
    keys = PaymentService.get_stripe_keys(db)
    is_test_mode = keys.get("secret_key", "").startswith("sk_test_")
    
    items = []
    for s in sponsorships:
        # If in test mode and sponsorship has payment_id but status is still pending_payment,
        # check Stripe to see if payment actually succeeded
        if is_test_mode and s.payment_id and s.status == "pending_payment" and s.payment_status != "succeeded":
            try:
                payment_intent = PaymentService.get_payment_intent(s.payment_id, db=db)
                if payment_intent["status"] == "succeeded":
                    # Payment succeeded but status wasn't updated - update it now
                    s.payment_status = "succeeded"
                    s.status = "pending"
                    db.commit()
                    logger.info(f"Queue: Auto-synced payment status for sponsorship {s.id} - payment succeeded")
            except Exception as e:
                logger.warning(f"Queue: Failed to check payment status for sponsorship {s.id}: {e}")
                # Continue with current status if check fails
        
        model_name = s.openrouter_model_id or s.custom_model_name or "Unknown"
        assigned_moderator_name = None
        if s.assigned_moderator:
            assigned_moderator_name = s.assigned_moderator.name or s.assigned_moderator.email
        
        items.append(SponsorshipQueueItem(
            id=s.id,
            request_type=s.request_type,
            model_name=model_name,
            user_name=s.user.name or s.user.email,
            user_email=s.user.email,
            message=s.message,
            status=s.status,
            payment_status=s.payment_status,
            created_at=s.created_at,
            assigned_moderator_id=s.assigned_moderator_id,
            assigned_moderator_name=assigned_moderator_name,
            assigned_at=s.assigned_at
        ))
    
    return SponsorshipQueueResponse(items=items, total=total)


@moderator_router.get("/{sponsorship_id}", response_model=SponsorshipDetailResponse)
async def get_sponsorship_detail(
    sponsorship_id: UUID,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """Get sponsorship details for review"""
    sponsorship = db.query(SponsorshipRequest).options(
        joinedload(SponsorshipRequest.user),
        joinedload(SponsorshipRequest.assigned_moderator)
    ).filter(
        SponsorshipRequest.id == sponsorship_id
    ).first()
    
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship request not found")
    
    model_name = sponsorship.openrouter_model_id or sponsorship.custom_model_name or "Unknown"
    assigned_moderator_name = None
    if sponsorship.assigned_moderator:
        assigned_moderator_name = sponsorship.assigned_moderator.name or sponsorship.assigned_moderator.email
    
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
        reviewer_notes=sponsorship.reviewer_notes,
        assigned_moderator_id=sponsorship.assigned_moderator_id,
        assigned_moderator_name=assigned_moderator_name,
        assigned_at=sponsorship.assigned_at
    )


@moderator_router.post("/{sponsorship_id}/sync-payment")
async def sync_payment_status(
    sponsorship_id: UUID,
    current_user: User = Depends(require_moderator),
    db: Session = Depends(get_db)
):
    """
    Manually sync payment status from Stripe for a sponsorship.
    Useful for troubleshooting when webhook didn't fire or payment status is out of sync.
    """
    sponsorship = db.query(SponsorshipRequest).filter(
        SponsorshipRequest.id == sponsorship_id
    ).first()
    
    if not sponsorship:
        raise HTTPException(status_code=404, detail="Sponsorship request not found")
    
    if not sponsorship.payment_id:
        raise HTTPException(status_code=400, detail="No payment associated with this sponsorship")
    
    try:
        payment_intent = PaymentService.get_payment_intent(sponsorship.payment_id, db=db)
        
        # Update payment status from Stripe
        sponsorship.payment_status = payment_intent["status"]
        
        # If payment succeeded and sponsorship is still pending payment, update status
        if payment_intent["status"] == "succeeded" and sponsorship.status == "pending_payment":
            sponsorship.status = "pending"
            db.commit()
            logger.info(f"Moderator {current_user.id} synced payment for sponsorship {sponsorship.id}: payment succeeded, status updated to pending")
            
            return {
                "status": sponsorship.status,
                "payment_status": sponsorship.payment_status,
                "updated": True,
                "message": "Payment status synced. Sponsorship is now pending moderation."
            }
        else:
            db.commit()
            return {
                "status": sponsorship.status,
                "payment_status": sponsorship.payment_status,
                "updated": False,
                "message": f"Payment status synced. Current payment status: {payment_intent['status']}"
            }
    except Exception as e:
        logger.error(f"Failed to sync payment status for sponsorship {sponsorship_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync payment status: {str(e)}"
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

    ActionLogService.log_action(
        db, "sponsorship.review", "user",
        actor_user_id=current_user.id,
        entity_type="sponsorship_request", entity_id=str(sponsorship.id),
        metadata={"action": request.action, "request_type": sponsorship.request_type}
    )
    
    # DEFERRED: Sponsorship review email notifications
    # When EmailService has sponsorship methods, implement here:
    # if request.action == "approve":
    #     await EmailService.send_sponsorship_approved_email(...)
    # else:
    #     await EmailService.send_sponsorship_rejected_email(...)
    
    # DEFERRED: Auto-trigger model test setup for approved sponsorships
    # This would create a TestRun and queue it for execution
    
    return ReviewSponsorshipResponse(
        id=sponsorship.id,
        status=sponsorship.status,
        message=message
    )
