"""Stripe payment service with encrypted credential management"""
import stripe
import base64
import hashlib
from typing import Dict, Optional, List
from decimal import Decimal
from datetime import datetime
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.stripe_config import StripeConfig


class EncryptionService:
    """Service for encrypting and decrypting sensitive data using Fernet (AES-128)"""
    
    _fernet: Optional[Fernet] = None
    
    @classmethod
    def _get_fernet(cls) -> Fernet:
        """Get or create Fernet instance using NEXTAUTH_SECRET as the key base"""
        if cls._fernet is None:
            # Derive a 32-byte key from NEXTAUTH_SECRET using SHA-256
            secret = settings.NEXTAUTH_SECRET
            if not secret:
                raise ValueError("NEXTAUTH_SECRET is required for encryption")
            
            # Create a consistent 32-byte key
            key_bytes = hashlib.sha256(secret.encode()).digest()
            # Fernet requires base64-encoded 32-byte key
            fernet_key = base64.urlsafe_b64encode(key_bytes)
            cls._fernet = Fernet(fernet_key)
        
        return cls._fernet
    
    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext"""
        fernet = cls._get_fernet()
        encrypted = fernet.encrypt(plaintext.encode())
        return encrypted.decode()
    
    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext and return plaintext"""
        fernet = cls._get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode())
        return decrypted.decode()


class PaymentService:
    """Service for handling Stripe payments with support for DB-stored credentials"""
    
    @staticmethod
    def get_active_config(db: Session) -> Optional[StripeConfig]:
        """
        Get the active Stripe configuration from the database.
        
        Returns:
            The active StripeConfig or None if not found
        """
        return db.query(StripeConfig).filter(
            StripeConfig.is_active == True
        ).first()
    
    @staticmethod
    def get_stripe_keys(db: Optional[Session] = None) -> Dict[str, Optional[str]]:
        """
        Get Stripe API keys, preferring database config over environment variables.
        
        Args:
            db: Database session (optional - if not provided, uses env vars only)
        
        Returns:
            Dict with 'secret_key', 'publishable_key', 'webhook_secret', 'source', 'is_live_mode'
        """
        # Try database first if session provided
        if db is not None:
            config = PaymentService.get_active_config(db)
            if config:
                try:
                    secret_key = EncryptionService.decrypt(config.secret_key_encrypted)
                    webhook_secret = None
                    if config.webhook_secret_encrypted:
                        webhook_secret = EncryptionService.decrypt(config.webhook_secret_encrypted)
                    
                    return {
                        "secret_key": secret_key,
                        "publishable_key": config.publishable_key,
                        "webhook_secret": webhook_secret,
                        "source": "database",
                        "is_live_mode": config.is_live_mode,
                        "config_name": config.name,
                        "config_id": str(config.id),
                    }
                except Exception:
                    # If decryption fails, fall back to env vars
                    pass
        
        # Fall back to environment variables
        return {
            "secret_key": settings.STRIPE_SECRET_KEY or None,
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY or None,
            "webhook_secret": settings.STRIPE_WEBHOOK_SECRET or None,
            "source": "environment",
            "is_live_mode": settings.STRIPE_SECRET_KEY.startswith("sk_live_") if settings.STRIPE_SECRET_KEY else False,
            "config_name": None,
            "config_id": None,
        }
    
    @staticmethod
    def _configure_stripe(db: Optional[Session] = None) -> str:
        """
        Configure the stripe module with the appropriate API key.
        
        Returns:
            The secret key being used
        """
        keys = PaymentService.get_stripe_keys(db)
        secret_key = keys.get("secret_key")
        
        if not secret_key:
            raise Exception("Stripe is not configured. No API key available.")
        
        stripe.api_key = secret_key
        return secret_key
    
    @staticmethod
    def create_payment_intent(
        amount: Decimal,
        currency: str = "usd",
        metadata: Optional[Dict[str, str]] = None,
        customer_email: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Create a Stripe PaymentIntent
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: usd)
            metadata: Additional metadata to attach
            customer_email: Customer email for receipt
            db: Database session for loading DB config
        
        Returns:
            PaymentIntent object dict
        """
        PaymentService._configure_stripe(db)
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
    def verify_webhook_signature(
        payload: bytes,
        signature: str,
        db: Optional[Session] = None
    ) -> Dict:
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Raw request body
            signature: Stripe signature header
            db: Database session for loading DB config
        
        Returns:
            Event object dict
        
        Raises:
            Exception: If signature is invalid
        """
        keys = PaymentService.get_stripe_keys(db)
        webhook_secret = keys.get("webhook_secret")
        
        if not webhook_secret:
            # Fall back to settings if not in DB
            webhook_secret = settings.STRIPE_WEBHOOK_SECRET
        
        if not webhook_secret:
            raise Exception("Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                webhook_secret
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
        reason: str = "requested_by_customer",
        db: Optional[Session] = None
    ) -> Dict:
        """
        Create a refund for a payment
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            amount: Amount to refund (None = full refund)
            reason: Refund reason
            db: Database session for loading DB config
        
        Returns:
            Refund object dict
        """
        PaymentService._configure_stripe(db)
        
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
    def get_payment_intent(payment_intent_id: str, db: Optional[Session] = None) -> Dict:
        """
        Retrieve a PaymentIntent
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            db: Database session for loading DB config
        
        Returns:
            PaymentIntent object dict
        """
        PaymentService._configure_stripe(db)
        
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
    
    # =========================================================================
    # Admin methods for viewing Stripe data
    # =========================================================================
    
    @staticmethod
    def test_connection(secret_key: str) -> Dict:
        """
        Test a Stripe connection with given credentials.
        
        Supports both full API keys and restricted keys. For restricted keys,
        uses a simpler endpoint that doesn't require account-level permissions.
        
        Args:
            secret_key: Stripe secret key to test
        
        Returns:
            Dict with connection status and account info
        """
        # Save current key to restore later
        original_key = stripe.api_key
        
        try:
            # Set the test API key
            stripe.api_key = secret_key
            
            # Check if this is a restricted key by prefix
            is_restricted = secret_key.startswith(("rk_live_", "rk_test_"))
            
            if is_restricted:
                # For restricted keys, use a simpler endpoint that most keys have access to
                # PaymentIntent.list is commonly available for restricted keys
                try:
                    stripe.PaymentIntent.list(limit=1)
                    return {
                        "success": True,
                        "account_id": None,
                        "business_name": None,
                        "country": None,
                        "default_currency": None,
                        "charges_enabled": None,
                        "payouts_enabled": None,
                        "is_restricted_key": True,
                        "message": "Restricted key validated successfully. Account details unavailable with restricted keys.",
                    }
                except stripe.error.AuthenticationError:
                    return {
                        "success": False,
                        "error": "Invalid API key"
                    }
                except stripe.error.StripeError as e:
                    # Key might have very limited permissions, but if it's not an auth error,
                    # it's probably valid - just with limited access
                    error_msg = str(e).lower()
                    if "permission" in error_msg:
                        return {
                            "success": True,
                            "account_id": None,
                            "business_name": None,
                            "country": None,
                            "default_currency": None,
                            "charges_enabled": None,
                            "payouts_enabled": None,
                            "is_restricted_key": True,
                            "message": "Restricted key accepted. Note: key has limited permissions.",
                        }
                    return {
                        "success": False,
                        "error": f"Stripe error: {str(e)}"
                    }
            else:
                # For full keys (sk_live_, sk_test_), try to get account info
                try:
                    account = stripe.Account.retrieve()
                    return {
                        "success": True,
                        "account_id": account.id,
                        "business_name": account.get("business_profile", {}).get("name") if hasattr(account, 'get') else getattr(getattr(account, 'business_profile', None), 'name', None),
                        "country": account.country,
                        "default_currency": account.default_currency,
                        "charges_enabled": account.charges_enabled,
                        "payouts_enabled": account.payouts_enabled,
                        "is_restricted_key": False,
                    }
                except stripe.error.AuthenticationError:
                    return {
                        "success": False,
                        "error": "Invalid API key"
                    }
                except stripe.error.StripeError as e:
                    return {
                        "success": False,
                        "error": str(e)
                    }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }
        finally:
            # Restore original key (avoid setting to None which corrupts Stripe SDK)
            if original_key:
                stripe.api_key = original_key
    
    @staticmethod
    def list_balance_transactions(
        limit: int = 25,
        starting_after: Optional[str] = None,
        created_gte: Optional[datetime] = None,
        created_lte: Optional[datetime] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        List balance transactions from Stripe.
        
        Args:
            limit: Number of transactions to return (max 100)
            starting_after: Cursor for pagination
            created_gte: Filter transactions created on or after this date
            created_lte: Filter transactions created on or before this date
            db: Database session for loading DB config
        
        Returns:
            Dict with transactions list and pagination info
        """
        PaymentService._configure_stripe(db)
        
        params = {
            "limit": min(limit, 100),
        }
        
        if starting_after:
            params["starting_after"] = starting_after
        
        # Build created filter
        if created_gte or created_lte:
            params["created"] = {}
            if created_gte:
                params["created"]["gte"] = int(created_gte.timestamp())
            if created_lte:
                params["created"]["lte"] = int(created_lte.timestamp())
        
        try:
            transactions = stripe.BalanceTransaction.list(**params)
            
            return {
                "data": [
                    {
                        "id": t.id,
                        "amount": t.amount / 100,
                        "currency": t.currency,
                        "net": t.net / 100,
                        "fee": t.fee / 100,
                        "type": t.type,
                        "status": t.status,
                        "description": t.description,
                        "created": datetime.fromtimestamp(t.created).isoformat(),
                        "available_on": datetime.fromtimestamp(t.available_on).isoformat() if t.available_on else None,
                        "source": t.source,
                    }
                    for t in transactions.data
                ],
                "has_more": transactions.has_more,
                "total_count": None,  # Stripe doesn't provide total count
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def list_payment_intents(
        limit: int = 25,
        starting_after: Optional[str] = None,
        created_gte: Optional[datetime] = None,
        created_lte: Optional[datetime] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        List payment intents from Stripe.
        
        Args:
            limit: Number of payment intents to return (max 100)
            starting_after: Cursor for pagination
            created_gte: Filter created on or after this date
            created_lte: Filter created on or before this date
            db: Database session for loading DB config
        
        Returns:
            Dict with payment intents list and pagination info
        """
        PaymentService._configure_stripe(db)
        
        params = {
            "limit": min(limit, 100),
        }
        
        if starting_after:
            params["starting_after"] = starting_after
        
        if created_gte or created_lte:
            params["created"] = {}
            if created_gte:
                params["created"]["gte"] = int(created_gte.timestamp())
            if created_lte:
                params["created"]["lte"] = int(created_lte.timestamp())
        
        try:
            intents = stripe.PaymentIntent.list(**params)
            
            return {
                "data": [
                    {
                        "id": pi.id,
                        "amount": pi.amount / 100,
                        "currency": pi.currency,
                        "status": pi.status,
                        "description": pi.description,
                        "receipt_email": pi.receipt_email,
                        "metadata": dict(pi.metadata) if pi.metadata else {},
                        "created": datetime.fromtimestamp(pi.created).isoformat(),
                        "payment_method_types": pi.payment_method_types,
                    }
                    for pi in intents.data
                ],
                "has_more": intents.has_more,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def list_charges(
        limit: int = 25,
        starting_after: Optional[str] = None,
        created_gte: Optional[datetime] = None,
        created_lte: Optional[datetime] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        List charges from Stripe.
        
        Args:
            limit: Number of charges to return (max 100)
            starting_after: Cursor for pagination
            created_gte: Filter created on or after this date
            created_lte: Filter created on or before this date
            db: Database session for loading DB config
        
        Returns:
            Dict with charges list and pagination info
        """
        PaymentService._configure_stripe(db)
        
        params = {
            "limit": min(limit, 100),
        }
        
        if starting_after:
            params["starting_after"] = starting_after
        
        if created_gte or created_lte:
            params["created"] = {}
            if created_gte:
                params["created"]["gte"] = int(created_gte.timestamp())
            if created_lte:
                params["created"]["lte"] = int(created_lte.timestamp())
        
        try:
            charges = stripe.Charge.list(**params)
            
            return {
                "data": [
                    {
                        "id": c.id,
                        "amount": c.amount / 100,
                        "amount_refunded": c.amount_refunded / 100,
                        "currency": c.currency,
                        "status": c.status,
                        "paid": c.paid,
                        "refunded": c.refunded,
                        "disputed": c.disputed,
                        "description": c.description,
                        "receipt_email": c.receipt_email,
                        "receipt_url": c.receipt_url,
                        "payment_intent": c.payment_intent,
                        "metadata": dict(c.metadata) if c.metadata else {},
                        "created": datetime.fromtimestamp(c.created).isoformat(),
                        "failure_code": c.failure_code,
                        "failure_message": c.failure_message,
                    }
                    for c in charges.data
                ],
                "has_more": charges.has_more,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def list_refunds(
        limit: int = 25,
        starting_after: Optional[str] = None,
        created_gte: Optional[datetime] = None,
        created_lte: Optional[datetime] = None,
        db: Optional[Session] = None
    ) -> Dict:
        """
        List refunds from Stripe.
        
        Args:
            limit: Number of refunds to return (max 100)
            starting_after: Cursor for pagination
            created_gte: Filter created on or after this date
            created_lte: Filter created on or before this date
            db: Database session for loading DB config
        
        Returns:
            Dict with refunds list and pagination info
        """
        PaymentService._configure_stripe(db)
        
        params = {
            "limit": min(limit, 100),
        }
        
        if starting_after:
            params["starting_after"] = starting_after
        
        if created_gte or created_lte:
            params["created"] = {}
            if created_gte:
                params["created"]["gte"] = int(created_gte.timestamp())
            if created_lte:
                params["created"]["lte"] = int(created_lte.timestamp())
        
        try:
            refunds = stripe.Refund.list(**params)
            
            return {
                "data": [
                    {
                        "id": r.id,
                        "amount": r.amount / 100,
                        "currency": r.currency,
                        "status": r.status,
                        "reason": r.reason,
                        "payment_intent": r.payment_intent,
                        "charge": r.charge,
                        "created": datetime.fromtimestamp(r.created).isoformat(),
                        "metadata": dict(r.metadata) if r.metadata else {},
                    }
                    for r in refunds.data
                ],
                "has_more": refunds.has_more,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def get_balance(db: Optional[Session] = None) -> Dict:
        """
        Get the current Stripe balance.
        
        Args:
            db: Database session for loading DB config
        
        Returns:
            Dict with available and pending balances
        """
        PaymentService._configure_stripe(db)
        
        try:
            balance = stripe.Balance.retrieve()
            
            return {
                "available": [
                    {
                        "amount": b.amount / 100,
                        "currency": b.currency,
                    }
                    for b in balance.available
                ],
                "pending": [
                    {
                        "amount": b.amount / 100,
                        "currency": b.currency,
                    }
                    for b in balance.pending
                ],
                "livemode": balance.livemode,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def mask_key(key: str) -> str:
        """
        Mask a Stripe API key for display.
        
        Args:
            key: The full API key
        
        Returns:
            Masked key showing only prefix and last 4 characters
        """
        if not key or len(key) < 12:
            return "****"
        
        # Keep prefix (sk_test_ or sk_live_ or pk_test_ or pk_live_)
        if key.startswith(("sk_test_", "sk_live_", "pk_test_", "pk_live_")):
            prefix = key[:8]  # e.g., "sk_test_"
            return f"{prefix}****{key[-4:]}"
        
        # For webhook secrets (whsec_)
        if key.startswith("whsec_"):
            return f"whsec_****{key[-4:]}"
        
        return f"****{key[-4:]}"
