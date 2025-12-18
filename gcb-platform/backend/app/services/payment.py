"""Stripe payment service"""
import stripe
from typing import Dict, Optional
from decimal import Decimal
from app.core.config import settings

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Service for handling Stripe payments"""
    
    @staticmethod
    def create_payment_intent(
        amount: Decimal,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None,
        customer_email: Optional[str] = None
    ) -> Dict:
        """
        Create a Stripe PaymentIntent
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            metadata: Additional metadata to attach
            customer_email: Customer email for receipt
        
        Returns:
            PaymentIntent object dict
        """
        amount_cents = int(float(amount) * 100)  # Convert to cents
        
        intent_params = {
            "amount": amount_cents,
            "currency": currency,
            "automatic_payment_methods": {
                "enabled": True
            },
            "metadata": metadata or {}
        }
        
        if customer_email:
            intent_params["receipt_email"] = customer_email
        
        try:
            intent = stripe.PaymentIntent.create(**intent_params)
            return {
                "id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status,
                "amount": intent.amount / 100,  # Convert back to dollars
                "currency": intent.currency
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> Dict:
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            signature: Stripe signature header
        
        Returns:
            Event object dict
        
        Raises:
            Exception: If signature is invalid
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            raise Exception(f"Invalid payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise Exception(f"Invalid signature: {str(e)}")
    
    @staticmethod
    def create_refund(
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer"
    ) -> Dict:
        """
        Create a refund for a payment
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            amount: Amount to refund (None = full refund)
            reason: Refund reason
        
        Returns:
            Refund object dict
        """
        refund_params = {
            "payment_intent": payment_intent_id,
            "reason": reason
        }
        
        if amount:
            refund_params["amount"] = int(float(amount) * 100)  # Convert to cents
        
        try:
            refund = stripe.Refund.create(**refund_params)
            return {
                "id": refund.id,
                "amount": refund.amount / 100,  # Convert back to dollars
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe refund error: {str(e)}")
    
    @staticmethod
    def get_payment_intent(payment_intent_id: str) -> Dict:
        """
        Retrieve a PaymentIntent
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
        
        Returns:
            PaymentIntent object dict
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,
                "currency": intent.currency,
                "metadata": intent.metadata
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
