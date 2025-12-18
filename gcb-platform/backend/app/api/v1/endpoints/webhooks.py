"""Webhook endpoints"""
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.services.payment import PaymentService
from app.db.models.test_run import TestRun
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
        # Payment succeeded - start the test
        payment_intent_id = event_data["id"]
        metadata = event_data.get("metadata", {})
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
        # Payment failed - update test status
        payment_intent_id = event_data["id"]
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
