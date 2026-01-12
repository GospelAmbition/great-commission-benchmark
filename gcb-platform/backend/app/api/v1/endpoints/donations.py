"""Donations API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.payment import PaymentService
from app.core.auth import get_db

router = APIRouter()


class CreateDonationIntentRequest(BaseModel):
    """Request to create a donation payment intent"""
    amount: float = Field(..., ge=5, description="Donation amount in USD (minimum $5)")
    email: Optional[str] = Field(None, description="Email for donation receipt")


class CreateDonationIntentResponse(BaseModel):
    """Response with payment intent details"""
    payment_intent_id: str
    client_secret: str
    amount: float


@router.post("/create-intent", response_model=CreateDonationIntentResponse)
async def create_donation_intent(
    request: CreateDonationIntentRequest,
    db: Session = Depends(get_db)
):
    """
    Create a Stripe payment intent for a donation.
    
    No authentication required - anyone can donate.
    """
    # Check if Stripe is configured (from database or environment)
    keys = PaymentService.get_stripe_keys(db)
    if not keys.get("secret_key"):
        raise HTTPException(
            status_code=503,
            detail="Payment processing is not configured"
        )
    
    # Create metadata for Stripe dashboard filtering
    metadata = {
        "type": "donation",
        "source": "gcb_support_page"
    }
    
    try:
        payment_intent = PaymentService.create_payment_intent(
            amount=Decimal(str(request.amount)),
            metadata=metadata,
            customer_email=request.email,
            db=db  # Pass db session to use database config
        )
        
        return CreateDonationIntentResponse(
            payment_intent_id=payment_intent["id"],
            client_secret=payment_intent["client_secret"],
            amount=payment_intent["amount"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create payment intent: {str(e)}"
        )

