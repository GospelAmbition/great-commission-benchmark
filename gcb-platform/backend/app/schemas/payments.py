"""Payment API schemas"""
from typing import Optional
from pydantic import BaseModel
from decimal import Decimal
from uuid import UUID


class CreatePaymentIntentRequest(BaseModel):
    """Create payment intent request"""
    test_id: UUID
    tip_percentage: Optional[int] = None  # 0-100


class CreatePaymentIntentResponse(BaseModel):
    """Create payment intent response"""
    payment_intent_id: str
    client_secret: str
    amount: Decimal
    breakdown: dict


class RefundRequest(BaseModel):
    """Refund request"""
    test_id: UUID
    amount: Optional[Decimal] = None  # None = full refund
    reason: str = "requested_by_customer"


class RefundResponse(BaseModel):
    """Refund response"""
    refund_id: str
    amount: Decimal
    status: str
