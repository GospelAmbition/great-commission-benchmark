"""Webhook endpoints"""
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import get_db
from app.services.payment import PaymentService
from app.db.models.community_submission import CommunitySubmission
from app.db.models.sponsorship_request import SponsorshipRequest
from app.services.email import EmailService

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
        
        # Handle CLI submission payments
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
        
        # Handle sponsorship payments
        elif payment_type == "sponsorship":
            # Query by payment_id for reliability (consistent with payment_failed handler)
            sponsorship = db.query(SponsorshipRequest).filter(
                SponsorshipRequest.payment_id == payment_intent_id
            ).first()
            
            if sponsorship and sponsorship.status == "pending_payment":
                # Update sponsorship status to pending for moderation
                sponsorship.payment_status = "succeeded"
                sponsorship.status = "pending"
                db.commit()
                
                # DEFERRED: Payment confirmation emails
                # Sponsorship payment confirmation email not yet implemented in EmailService
                # When ready, uncomment:
                # await EmailService.send_sponsorship_payment_confirmed_email(
                #     sponsorship.user.email,
                #     str(sponsorship.id),
                #     sponsorship.openrouter_model_id or sponsorship.custom_model_name
                # )
    
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
