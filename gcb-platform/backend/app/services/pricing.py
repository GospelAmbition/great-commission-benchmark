"""Pricing calculation service"""
from decimal import Decimal


class PricingService:
    """Service for pricing constants"""
    
    # CLI submission fee in USD
    SUBMISSION_FEE = Decimal("20.00")
