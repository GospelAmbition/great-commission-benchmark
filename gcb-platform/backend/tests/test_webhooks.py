"""Tests for webhook endpoints"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.db.models.user import User
from app.db.models.test_run import TestRun

client = TestClient(app)


@pytest.fixture
def test_test_run_with_payment(db_session):
    """Create test run with payment"""
    from app.db.models.model import Model
    from app.db.models.question_set import QuestionSet
    from app.db.models.methodology_version import MethodologyVersion
    
    user = User(
        auth0_id="test_user",
        email="test@example.com",
        role="user"
    )
    db_session.add(user)
    db_session.flush()
    
    model = Model(model_id="test-model", name="Test Model", provider="test")
    db_session.add(model)
    db_session.flush()
    
    question_set = QuestionSet(semantic_version="1.0.0", status="active")
    db_session.add(question_set)
    db_session.flush()
    
    methodology_version = MethodologyVersion(question_set_id=question_set.id)
    db_session.add(methodology_version)
    db_session.flush()
    
    test_run = TestRun(
        user_id=user.id,
        model_id=model.id,
        question_set_id=question_set.id,
        methodology_version_id=methodology_version.id,
        status="pending_payment",
        payment_id="pi_test123",
        payment_status="requires_payment_method"
    )
    db_session.add(test_run)
    db_session.commit()
    db_session.refresh(test_run)
    return test_run


@patch("app.services.payment.PaymentService.verify_webhook_signature")
def test_stripe_webhook_payment_succeeded(mock_verify, test_test_run_with_payment, db_session):
    """Test Stripe webhook for payment succeeded"""
    # Mock webhook verification
    mock_verify.return_value = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": "pi_test123",
                "metadata": {
                    "test_id": str(test_test_run_with_payment.id)
                }
            }
        }
    }
    
    response = client.post(
        "/api/v1/webhooks/stripe",
        content=b'{"test": "payload"}',
        headers={"stripe-signature": "test_signature"}
    )
    
    assert response.status_code == 200
    
    # Verify test run was updated
    db_session.refresh(test_test_run_with_payment)
    assert test_test_run_with_payment.payment_status == "succeeded"
    assert test_test_run_with_payment.status == "running"


@patch("app.services.payment.PaymentService.verify_webhook_signature")
def test_stripe_webhook_payment_failed(mock_verify, test_test_run_with_payment, db_session):
    """Test Stripe webhook for payment failed"""
    mock_verify.return_value = {
        "type": "payment_intent.payment_failed",
        "data": {
            "object": {
                "id": "pi_test123"
            }
        }
    }
    
    response = client.post(
        "/api/v1/webhooks/stripe",
        content=b'{"test": "payload"}',
        headers={"stripe-signature": "test_signature"}
    )
    
    assert response.status_code == 200
    
    # Verify test run was updated
    db_session.refresh(test_test_run_with_payment)
    assert test_test_run_with_payment.payment_status == "failed"
    assert test_test_run_with_payment.status == "payment_failed"


def test_stripe_webhook_missing_signature():
    """Test webhook without signature"""
    response = client.post(
        "/api/v1/webhooks/stripe",
        content=b'{"test": "payload"}'
    )
    
    assert response.status_code == 400
