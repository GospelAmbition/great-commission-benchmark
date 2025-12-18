"""Tests for payment endpoints"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from decimal import Decimal

from app.main import app
from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.model import Model

client = TestClient(app)


@pytest.fixture
def mock_stripe():
    """Mock Stripe service"""
    with patch("app.services.payment.PaymentService") as mock:
        yield mock


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        auth0_id="test_auth0_id",
        email="test@example.com",
        name="Test User",
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_model(db_session):
    """Create test model"""
    model = Model(
        model_id="test-model",
        name="Test Model",
        provider="test"
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    return model


@pytest.fixture
def test_test_run(db_session, test_user, test_model):
    """Create test run"""
    from app.db.models.question_set import QuestionSet
    from app.db.models.methodology_version import MethodologyVersion
    
    question_set = QuestionSet(
        semantic_version="1.0.0",
        status="active"
    )
    db_session.add(question_set)
    db_session.flush()
    
    methodology_version = MethodologyVersion(
        question_set_id=question_set.id
    )
    db_session.add(methodology_version)
    db_session.flush()
    
    test_run = TestRun(
        user_id=test_user.id,
        model_id=test_model.id,
        question_set_id=question_set.id,
        methodology_version_id=methodology_version.id,
        status="pending_payment",
        total_cost=20.0
    )
    db_session.add(test_run)
    db_session.commit()
    db_session.refresh(test_run)
    return test_run


def test_create_payment_intent(mock_stripe, test_user, test_test_run, auth_headers):
    """Test creating a payment intent"""
    mock_stripe.create_payment_intent.return_value = {
        "id": "pi_test123",
        "client_secret": "pi_test123_secret",
        "status": "requires_payment_method",
        "amount": 20.0,
        "currency": "usd"
    }
    
    response = client.post(
        "/api/v1/payments/create-intent",
        json={"test_id": str(test_test_run.id), "tip_percentage": 10},
        headers=auth_headers(test_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "payment_intent_id" in data
    assert "client_secret" in data
    assert data["amount"] == 20.0


def test_create_refund(mock_stripe, test_user, test_test_run, auth_headers):
    """Test creating a refund"""
    test_test_run.payment_id = "pi_test123"
    test_test_run.payment_status = "succeeded"
    
    mock_stripe.create_refund.return_value = {
        "id": "re_test123",
        "amount": 20.0,
        "status": "succeeded",
        "currency": "usd"
    }
    
    response = client.post(
        "/api/v1/payments/refund",
        json={"test_id": str(test_test_run.id)},
        headers=auth_headers(test_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "refund_id" in data
    assert data["amount"] == 20.0


def test_payment_intent_requires_auth(test_test_run):
    """Test that payment intent creation requires authentication"""
    response = client.post(
        "/api/v1/payments/create-intent",
        json={"test_id": str(test_test_run.id)}
    )
    
    assert response.status_code == 403


def test_refund_requires_auth(test_test_run):
    """Test that refund requires authentication"""
    response = client.post(
        "/api/v1/payments/refund",
        json={"test_id": str(test_test_run.id)}
    )
    
    assert response.status_code == 403
