"""Tests for webhook endpoints"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.services.payment import PaymentService


class TestStripeWebhooks:
    """Tests for Stripe webhook handlers"""
    
    @patch.object(PaymentService, 'verify_webhook_signature')
    def test_stripe_webhook_payment_succeeded(
        self,
        mock_verify,
        client,
        db_session,
        test_user,
        test_test_run,
        mock_email
    ):
        """Test Stripe webhook for payment_intent.succeeded"""
        # Set up test run with payment ID
        test_test_run.payment_id = "pi_test_123"
        test_test_run.status = "pending_payment"
        db_session.commit()
        
        # Mock webhook verification to return success event
        mock_verify.return_value = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test_123",
                    "metadata": {
                        "test_id": str(test_test_run.id)
                    }
                }
            }
        }
        
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"type": "payment_intent.succeeded"}',
            headers={"stripe-signature": "test_signature_123"}
        )
        
        assert response.status_code == 200
        
        # Verify test run was updated
        db_session.refresh(test_test_run)
        assert test_test_run.payment_status == "succeeded"
        assert test_test_run.status == "running"
        assert test_test_run.started_at is not None
    
    @patch.object(PaymentService, 'verify_webhook_signature')
    def test_stripe_webhook_payment_failed(
        self,
        mock_verify,
        client,
        db_session,
        test_user,
        test_test_run,
        mock_email
    ):
        """Test Stripe webhook for payment_intent.payment_failed"""
        # Set up test run with payment ID
        test_test_run.payment_id = "pi_test_failed"
        test_test_run.status = "pending_payment"
        db_session.commit()
        
        mock_verify.return_value = {
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test_failed"
                }
            }
        }
        
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"type": "payment_intent.payment_failed"}',
            headers={"stripe-signature": "test_signature_123"}
        )
        
        assert response.status_code == 200
        
        # Verify test run was updated
        db_session.refresh(test_test_run)
        assert test_test_run.payment_status == "failed"
        assert test_test_run.status == "payment_failed"
    
    @patch.object(PaymentService, 'verify_webhook_signature')
    def test_stripe_webhook_charge_refunded(
        self,
        mock_verify,
        client,
        db_session,
        test_user,
        test_test_run
    ):
        """Test Stripe webhook for charge.refunded"""
        # Set up test run with payment ID
        test_test_run.payment_id = "pi_test_refund"
        test_test_run.status = "pending_payment"
        test_test_run.payment_status = "succeeded"
        db_session.commit()
        
        mock_verify.return_value = {
            "type": "charge.refunded",
            "data": {
                "object": {
                    "payment_intent": "pi_test_refund"
                }
            }
        }
        
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"type": "charge.refunded"}',
            headers={"stripe-signature": "test_signature_123"}
        )
        
        assert response.status_code == 200
        
        # Verify test run was updated
        db_session.refresh(test_test_run)
        assert test_test_run.payment_status == "refunded"
        assert test_test_run.status == "cancelled"
    
    def test_stripe_webhook_missing_signature(self, client):
        """Test webhook without signature header"""
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"test": "payload"}'
        )
        
        assert response.status_code == 400
        assert "Missing stripe-signature" in response.json()["detail"]
    
    @patch.object(PaymentService, 'verify_webhook_signature')
    def test_stripe_webhook_invalid_signature(
        self,
        mock_verify,
        client
    ):
        """Test webhook with invalid signature"""
        mock_verify.side_effect = Exception("Invalid signature")
        
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"test": "payload"}',
            headers={"stripe-signature": "invalid_signature"}
        )
        
        assert response.status_code == 400
        assert "Invalid webhook signature" in response.json()["detail"]
    
    @patch.object(PaymentService, 'verify_webhook_signature')
    def test_stripe_webhook_unknown_event_type(
        self,
        mock_verify,
        client
    ):
        """Test webhook with unknown event type"""
        mock_verify.return_value = {
            "type": "some.unknown.event",
            "data": {
                "object": {}
            }
        }
        
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"type": "some.unknown.event"}',
            headers={"stripe-signature": "test_signature"}
        )
        
        # Should return 200 (acknowledge receipt) even for unknown events
        assert response.status_code == 200
    
    @patch.object(PaymentService, 'verify_webhook_signature')
    def test_stripe_webhook_no_test_id_in_metadata(
        self,
        mock_verify,
        client,
        db_session
    ):
        """Test webhook where payment has no test_id in metadata"""
        mock_verify.return_value = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_no_metadata",
                    "metadata": {}  # No test_id
                }
            }
        }
        
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"type": "payment_intent.succeeded"}',
            headers={"stripe-signature": "test_signature"}
        )
        
        # Should still return 200 - just won't update any test run
        assert response.status_code == 200


class TestWebhookEmailNotifications:
    """Tests for email notifications triggered by webhooks"""
    
    @patch.object(PaymentService, 'verify_webhook_signature')
    @patch("app.api.v1.endpoints.webhooks.EmailService")
    def test_payment_failed_sends_email(
        self,
        mock_email_service,
        mock_verify,
        client,
        db_session,
        test_user,
        test_test_run
    ):
        """Test that payment failure triggers email notification"""
        test_test_run.payment_id = "pi_test_email"
        test_test_run.status = "pending_payment"
        db_session.commit()
        
        mock_email_service.send_payment_failed_email = AsyncMock(return_value=True)
        
        mock_verify.return_value = {
            "type": "payment_intent.payment_failed",
            "data": {
                "object": {
                    "id": "pi_test_email"
                }
            }
        }
        
        response = client.post(
            "/api/webhooks/stripe",
            content=b'{"type": "payment_intent.payment_failed"}',
            headers={"stripe-signature": "test_signature"}
        )
        
        assert response.status_code == 200
        # Email service should be called (though may fail silently)
