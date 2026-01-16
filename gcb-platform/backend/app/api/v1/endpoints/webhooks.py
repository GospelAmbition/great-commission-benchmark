"""Webhook endpoints"""
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.core.auth import get_db
from app.services.payment import PaymentService
from app.db.models.community_submission import CommunitySubmission
from app.db.models.sponsorship_request import SponsorshipRequest
from app.db.models.notification_setting import NotificationSetting, NotificationType
from app.services.email import EmailService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    # Verify webhook signature
    try:
        event = PaymentService.verify_webhook_signature(payload, signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid webhook signature: {str(e)}")
    
    # Handle event
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    if event_type == "payment_intent.succeeded":
        # Payment succeeded
        payment_intent_id = event_data["id"]
        metadata = event_data.get("metadata", {})
        payment_type = metadata.get("type")
        
        # Try to find and update the relevant record by payment_id
        # Check sponsorships first (they have payment_id set)
        sponsorship = db.query(SponsorshipRequest).filter(
            SponsorshipRequest.payment_id == payment_intent_id
        ).first()
        
        if sponsorship:
            # Update sponsorship status to pending for moderation if payment is pending
            # This handles both initial webhook and cases where status might have been updated elsewhere
            was_pending_payment = sponsorship.status == "pending_payment"
            if was_pending_payment or sponsorship.payment_status != "succeeded":
                sponsorship.payment_status = "succeeded"
                sponsorship.status = "pending"
                db.commit()
            
            # Send notification email to designated recipient when sponsorship is ready for review
            if was_pending_payment:
                try:
                    # Get fresh sponsorship with user loaded
                    sponsorship = db.query(SponsorshipRequest).options(
                        joinedload(SponsorshipRequest.user)
                    ).filter(SponsorshipRequest.id == sponsorship.id).first()
                    
                    notification_setting = db.query(NotificationSetting).filter(
                        NotificationSetting.notification_type == NotificationType.SPONSORSHIP
                    ).first()
                    
                    if notification_setting and notification_setting.is_enabled and notification_setting.recipient_email:
                        model_name = sponsorship.openrouter_model_id or sponsorship.custom_model_name or "Unknown"
                        await EmailService.send_sponsorship_request_notification_email(
                            admin_email=notification_setting.recipient_email,
                            requester_name=sponsorship.user.name or sponsorship.user.email,
                            requester_email=sponsorship.user.email,
                            model_name=model_name,
                            request_type=sponsorship.request_type,
                            message=sponsorship.message,
                            sponsorship_id=str(sponsorship.id)
                        )
                except Exception as e:
                    logger.warning(f"Failed to send sponsorship notification email: {e}")
        else:
            # Handle CLI submission payments (only if not a sponsorship)
            if payment_type == "cli_submission":
                submission = db.query(CommunitySubmission).filter(
                    CommunitySubmission.payment_id == payment_intent_id
                ).first()
                
                if submission and submission.status == "pending_payment":
                    # Update submission status to pending for moderation
                    submission.status = "pending"
                    db.commit()
                    
                    # Send confirmation email
                    try:
                        await EmailService.send_submission_payment_confirmed_email(
                            submission.user.email,
                            str(submission.id),
                            submission.model_name
                        )
                    except:
                        pass
    
    elif event_type == "payment_intent.payment_failed":
        # Payment failed - update status
        payment_intent_id = event_data["id"]
        
        # Handle CLI submission payment failures
        submission = db.query(CommunitySubmission).filter(
            CommunitySubmission.payment_id == payment_intent_id
        ).first()
        
        if submission:
            submission.status = "payment_failed"
            db.commit()
            # Note: send_payment_failed_email is designed for test runs
            # For submissions, we could add a specific method or use a generic notification
            # For now, skip email to avoid errors
        
        # Handle sponsorship payment failures
        sponsorship = db.query(SponsorshipRequest).filter(
            SponsorshipRequest.payment_id == payment_intent_id
        ).first()
        
        if sponsorship:
            sponsorship.payment_status = "failed"
            sponsorship.status = "payment_failed"
            db.commit()
            # DEFERRED: Sponsorship payment failure email not yet implemented in EmailService
    
    # Return 200 to acknowledge receipt
    return Response(status_code=200)
