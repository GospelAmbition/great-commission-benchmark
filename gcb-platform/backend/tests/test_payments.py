"""Tests for payment endpoints"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from decimal import Decimal

from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.services.payment import PaymentService
from app.services.pricing import PricingService


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


class TestPricingService:
    """Tests for PricingService"""
    
    @pytest.mark.asyncio
    async def test_calculate_test_cost(self, mock_openrouter):
        """Test calculating test cost"""
        result = await PricingService.calculate_test_cost(
            model_id="test-model",
            question_count=100
        )
        
        assert "api_cost" in result
        assert "processing_fee" in result
        assert "total" in result
        assert result["processing_fee"] == Decimal("2.00")
    
    def test_calculate_with_tip_zero(self):
        """Test calculating with no tip"""
        result = PricingService.calculate_with_tip(
            base_cost=Decimal("20.00"),
            tip_percentage=0
        )
        
        assert result["tip_amount"] == Decimal("0.00")
        assert result["total"] == Decimal("20.00")
    
    def test_calculate_with_tip_10_percent(self):
        """Test calculating with 10% tip"""
        result = PricingService.calculate_with_tip(
            base_cost=Decimal("20.00"),
            tip_percentage=10
        )
        
        assert result["tip_amount"] == Decimal("2.00")
        assert result["total"] == Decimal("22.00")
    
    def test_calculate_with_tip_20_percent(self):
        """Test calculating with 20% tip"""
        result = PricingService.calculate_with_tip(
            base_cost=Decimal("20.00"),
            tip_percentage=20
        )
        
        assert result["tip_amount"] == Decimal("4.00")
        assert result["total"] == Decimal("24.00")
    
    def test_calculate_with_tip_none(self):
        """Test calculating with None tip"""
        result = PricingService.calculate_with_tip(
            base_cost=Decimal("20.00"),
            tip_percentage=None
        )
        
        assert result["tip_amount"] == Decimal("0.00")
        assert result["total"] == Decimal("20.00")


class TestPaymentEndpoints:
    """Tests for payment API endpoints"""
    
    def test_create_payment_intent_endpoint(
        self,
        client,
        db_session,
        test_user,
        test_test_run,
        mock_stripe,
        mock_openrouter
    ):
        """Test POST /api/payments/create-intent"""
        from main import app
        from app.core.auth import get_current_user
        
        # Override auth to return test user
        async def override_auth():
            return test_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        with patch.object(PricingService, 'calculate_test_cost', new_callable=AsyncMock) as mock_pricing:
            mock_pricing.return_value = {
                "api_cost": Decimal("18.00"),
                "processing_fee": Decimal("2.00"),
                "total": Decimal("20.00")
            }
            
            response = client.post(
                "/api/payments/create-intent",
                json={
                    "test_id": str(test_test_run.id),
                    "tip_percentage": 10
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "payment_intent_id" in data
        assert "client_secret" in data
        assert "amount" in data
        assert "breakdown" in data
        
        app.dependency_overrides.clear()
    
    def test_create_payment_intent_test_not_found(
        self,
        client,
        db_session,
        test_user
    ):
        """Test payment intent for non-existent test"""
        from main import app
        from app.core.auth import get_current_user
        from uuid import uuid4
        
        async def override_auth():
            return test_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.post(
            "/api/payments/create-intent",
            json={
                "test_id": str(uuid4()),
                "tip_percentage": 0
            }
        )
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_create_payment_intent_wrong_status(
        self,
        client,
        db_session,
        test_user,
        completed_test_run
    ):
        """Test payment intent for test with wrong status"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return test_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.post(
            "/api/payments/create-intent",
            json={
                "test_id": str(completed_test_run.id),
                "tip_percentage": 0
            }
        )
        
        assert response.status_code == 400
        assert "Cannot create payment intent" in response.json()["detail"]
        
        app.dependency_overrides.clear()
    
    def test_create_payment_intent_requires_auth(self, client):
        """Test that payment intent creation requires authentication"""
        from uuid import uuid4
        
        response = client.post(
            "/api/payments/create-intent",
            json={
                "test_id": str(uuid4()),
                "tip_percentage": 0
            }
        )
        
        assert response.status_code == 403
    
    def test_refund_requires_auth(self, client):
        """Test that refund requires authentication"""
        from uuid import uuid4
        
        response = client.post(
            "/api/payments/refund",
            json={
                "test_id": str(uuid4())
            }
        )
        
        assert response.status_code == 403
    
    def test_create_refund_no_payment(
        self,
        client,
        db_session,
        test_user,
        test_test_run
    ):
        """Test refund when no payment exists"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return test_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.post(
            "/api/payments/refund",
            json={
                "test_id": str(test_test_run.id)
            }
        )
        
        assert response.status_code == 400
        assert "No payment found" in response.json()["detail"]
        
        app.dependency_overrides.clear()
