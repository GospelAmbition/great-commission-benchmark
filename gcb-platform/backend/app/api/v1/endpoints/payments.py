"""Payments API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.auth import get_db
from app.core.auth import require_auth
from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.question import Question
from app.services.payment import PaymentService
from app.services.pricing import PricingService
from app.schemas.payments import (
    CreatePaymentIntentRequest,
    CreatePaymentIntentResponse,
    RefundRequest,
    RefundResponse
)

router = APIRouter()


@router.post("/create-intent", response_model=CreatePaymentIntentResponse)
async def create_payment_intent(
    request: CreatePaymentIntentRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a Stripe payment intent for a test"""
    # Get test run
    test_run = db.query(TestRun).filter(
        TestRun.id == request.test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if test_run.status != "pending_payment":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create payment intent. Test status: {test_run.status}"
        )
    
    # Get model and question count
    model = db.query(Model).filter(Model.id == test_run.model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    question_count = db.query(Question).filter(
        Question.question_set_id == test_run.question_set_id
    ).count()
    
    # Calculate pricing
    from decimal import Decimal
    pricing_breakdown = await PricingService.calculate_test_cost(
        model.model_id,
        question_count
    )
    
    # Add tip if specified
    if request.tip_percentage:
        pricing_breakdown = PricingService.calculate_with_tip(
            pricing_breakdown["total"],
            request.tip_percentage
        )
    
    total_amount = pricing_breakdown["total"]
    
    # Update test run with calculated cost
    test_run.total_cost = float(total_amount)
    db.commit()
    
    # Create payment intent
    metadata = {
        "test_id": str(test_run.id),
        "user_id": str(current_user.id),
        "model_id": str(model.id)
    }
    
    payment_intent = PaymentService.create_payment_intent(
        amount=total_amount,
        metadata=metadata,
        customer_email=current_user.email
    )
    
    # Update test run with payment intent ID
    test_run.payment_id = payment_intent["id"]
    test_run.payment_status = payment_intent["status"]
    db.commit()
    
    return CreatePaymentIntentResponse(
        payment_intent_id=payment_intent["id"],
        client_secret=payment_intent["client_secret"],
        amount=total_amount,
        breakdown={
            "api_cost": float(pricing_breakdown.get("api_cost", 0)),
            "processing_fee": float(pricing_breakdown.get("processing_fee", 0)),
            "tip_amount": float(pricing_breakdown.get("tip_amount", 0)),
            "total": float(total_amount)
        }
    )


@router.post("/refund", response_model=RefundResponse)
async def create_refund(
    request: RefundRequest,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Create a refund for a test"""
    # Get test run
    test_run = db.query(TestRun).filter(
        TestRun.id == request.test_id,
        TestRun.user_id == current_user.id
    ).first()
    
    if not test_run:
        raise HTTPException(status_code=404, detail="Test not found")
    
    if not test_run.payment_id:
        raise HTTPException(status_code=400, detail="No payment found for this test")
    
    # Create refund
    refund = PaymentService.create_refund(
        payment_intent_id=test_run.payment_id,
        amount=request.amount,
        reason=request.reason
    )
    
    # Update test run status
    test_run.payment_status = "refunded"
    if test_run.status == "pending_payment":
        test_run.status = "cancelled"
    
    db.commit()
    
    return RefundResponse(
        refund_id=refund["id"],
        amount=refund["amount"],
        status=refund["status"]
    )
