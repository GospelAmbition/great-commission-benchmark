"""Webhook endpoints"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import get_db
from app.services.payment import PaymentService
from app.db.models.test_run import TestRun
from app.db.models.community_submission import CommunitySubmission
from app.db.models.sponsorship_request import SponsorshipRequest
from app.services.executor import BenchmarkExecutor
from app.services.openrouter import OpenRouterClient
from app.services.email import EmailService

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
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
            sponsorship_id = metadata.get("sponsorship_id")
            
            if sponsorship_id:
                sponsorship = db.query(SponsorshipRequest).filter(
                    SponsorshipRequest.id == sponsorship_id
                ).first()
                
                if sponsorship and sponsorship.status == "pending_payment":
                    # Update sponsorship status to pending for moderation
                    sponsorship.payment_status = "succeeded"
                    sponsorship.status = "pending"
                    db.commit()
                    
                    # TODO: Send confirmation email to user
                    # try:
                    #     await EmailService.send_sponsorship_payment_confirmed_email(
                    #         sponsorship.user.email,
                    #         str(sponsorship.id),
                    #         sponsorship.openrouter_model_id or sponsorship.custom_model_name
                    #     )
                    # except:
                    #     pass
        
        # Handle platform test payments
        elif payment_type not in ["cli_submission", "sponsorship"]:
            test_id = metadata.get("test_id")
            
            if test_id:
                test_run = db.query(TestRun).filter(TestRun.id == test_id).first()
                if test_run:
                    # Update payment status
                    test_run.payment_status = "succeeded"
                    test_run.status = "running"
                    from datetime import datetime
                    test_run.started_at = datetime.utcnow()
                    db.commit()
                    
                    # Start test execution in background
                    async def run_test():
                        try:
                            openrouter_client = OpenRouterClient()
                            executor = BenchmarkExecutor(db, openrouter_client)
                            await executor.execute(test_id)
                            await openrouter_client.close()
                        except Exception as e:
                            # Update test run with error
                            test_run = db.query(TestRun).filter(TestRun.id == test_id).first()
                            if test_run:
                                test_run.status = "failed"
                                test_run.last_error = str(e)
                                db.commit()
                                # Send failure email
                                try:
                                    await EmailService.send_test_failed_email(
                                        test_run.user.email,
                                        test_run.id,
                                        str(e)
                                    )
                                except:
                                    pass
                    
                    background_tasks.add_task(run_test)
    
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
            # TODO: Send failure email notification
        
        # Handle platform test payment failures
        test_runs = db.query(TestRun).filter(TestRun.payment_id == payment_intent_id).all()
        
        for test_run in test_runs:
            test_run.payment_status = "failed"
            test_run.status = "payment_failed"
            db.commit()
            
            # Send failure email
            try:
                await EmailService.send_payment_failed_email(
                    test_run.user.email,
                    test_run.id
                )
            except:
                pass
    
    elif event_type == "charge.refunded":
        # Refund processed - update test status
        payment_intent_id = event_data.get("payment_intent")
        if payment_intent_id:
            test_runs = db.query(TestRun).filter(TestRun.payment_id == payment_intent_id).all()
            
            for test_run in test_runs:
                test_run.payment_status = "refunded"
                if test_run.status == "pending_payment":
                    test_run.status = "cancelled"
                db.commit()
    
    # Return 200 to acknowledge receipt
    return Response(status_code=200)
