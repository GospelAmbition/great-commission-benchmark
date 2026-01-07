"""Donations API endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

from app.services.payment import PaymentService
from app.core.config import settings

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
async def create_donation_intent(request: CreateDonationIntentRequest):
    """
    Create a Stripe payment intent for a donation.
    
    No authentication required - anyone can donate.
    """
    # Check if Stripe is configured
    if not settings.STRIPE_SECRET_KEY:
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
            customer_email=request.email
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

