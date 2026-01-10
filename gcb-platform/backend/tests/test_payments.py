"""Tests for payment endpoints"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from decimal import Decimal

from app.services.payment import PaymentService


class TestPaymentService:
    """Tests for PaymentService"""
    
    def test_create_payment_intent(self, mock_stripe):
        """Test creating a Stripe payment intent"""
        result = PaymentService.create_payment_intent(
            amount=Decimal("20.00"),
            metadata={"test_id": "test-123"},
            customer_email="test@example.com"
        )
        
        assert result["id"] == "pi_test_123"
        assert result["client_secret"] == "pi_test_123_secret_456"
        assert result["status"] == "requires_payment_method"
        mock_stripe["intent"].create.assert_called_once()
    
    def test_create_refund(self, mock_stripe):
        """Test creating a Stripe refund"""
        result = PaymentService.create_refund(
            payment_intent_id="pi_test_123",
            amount=Decimal("20.00"),
            reason="requested_by_customer"
        )
        
        assert result["id"] == "re_test_123"
        assert result["status"] == "succeeded"
        mock_stripe["refund"].create.assert_called_once()
    
    def test_get_payment_intent(self, mock_stripe):
        """Test retrieving a payment intent"""
        result = PaymentService.get_payment_intent("pi_test_123")
        
        assert result["id"] == "pi_test_123"
        assert result["status"] == "succeeded"
        mock_stripe["intent"].retrieve.assert_called_once_with("pi_test_123")
