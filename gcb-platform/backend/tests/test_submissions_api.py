"""Tests for submissions API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.db.models.user import User
from app.core.auth import get_current_user



@pytest.fixture
def db(db_session):
    """Use the isolated shared test database."""
    return db_session

@pytest.fixture
def test_user(db: Session):
    """Create test user"""
    user = User(
        auth0_id="test|123",
        email="test@example.com",
        name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def mock_auth(test_user):
    """Mock authentication"""
    async def mock_get_current_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def valid_export():
    """A complete current runner export with the benchmark's 70/20/10 split."""
    return {
        "format_version": "1.1",
        "test_run": {
            "id": "local-1", "model": "test/model", "backend": "openrouter",
            "benchmark_version": "1.0", "judge_model": "test/judge",
            "completed_at": "2026-01-01T00:00:00Z",
            "validity": "COMPLETE_VALID",
        },
        "summary": {
            "total_questions": 10, "score": 100,
            "scoring_weights": {"tier1": 0.7, "tier2": 0.2, "tier3": 0.1},
            "tier_scores": {
                "tier1": {"raw": 100, "questions": 7},
                "tier2": {"raw": 100, "questions": 2},
                "tier3": {"raw": 100, "questions": 1},
            },
            "verdict_counts": {"ACCEPTED": 10, "COMPROMISED": 0, "REFUSED": 0},
            "validity": "COMPLETE_VALID", "publishable": True,
        },
        "responses": [
            {"question_id": f"q{i}", "tier": tier, "verdict": "ACCEPTED", "response": "Response"}
            for i, tier in enumerate([1] * 7 + [2] * 2 + [3])
        ],
        "metadata": {"cli_version": "1.0", "benchmark_version": "1.0"},
    }


def test_upload_submission_valid(db, test_user, mock_auth, client, valid_export):
    """A fee-waived valid export is persisted and queued for review."""
    from app.db.models.community_submission import CommunitySubmission
    test_user.fee_waived = True
    db.commit()
    response = client.post(
        "/api/submissions", headers={"Authorization": "Bearer test_token"},
        json={"export_data": valid_export},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["fee_waived"] is True
    assert data["payment_required"] is False
    submission = db.query(CommunitySubmission).one()
    assert str(submission.id) == data["submission_id"]
    assert submission.user_id == test_user.id
    assert submission.results_package == valid_export
    assert submission.overall_score == 100
    assert submission.model_name == "test/model"


def test_valid_submission_requires_payment(db, test_user, mock_auth, client, valid_export, monkeypatch):
    """Ordinary submitters remain pending payment until a verified webhook."""
    from unittest.mock import Mock
    from app.services.payment import PaymentService
    from app.services.pricing import PricingService
    from app.db.models.community_submission import CommunitySubmission
    create_intent = Mock(return_value={"id": "pi_submission", "client_secret": "test_secret"})
    monkeypatch.setattr(PaymentService, "create_payment_intent", create_intent)
    response = client.post(
        "/api/submissions", headers={"Authorization": "Bearer test_token"},
        json={"export_data": valid_export},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_payment"
    assert data["payment_required"] is True
    assert data["fee_waived"] is False
    assert data["payment_intent_id"] == "pi_submission"
    create_intent.assert_called_once_with(
        amount=PricingService.SUBMISSION_FEE, currency="usd",
        metadata={"type": "cli_submission", "user_id": str(test_user.id), "model_name": "test/model", "version": "1.0"},
        customer_email=test_user.email, db=db,
    )
    submission = db.query(CommunitySubmission).one()
    assert submission.status == "pending_payment"
    assert submission.payment_id == "pi_submission"
    assert submission.results_package == valid_export


def test_upload_submission_invalid(db, test_user, mock_auth, client):
    """Test uploading an invalid submission"""
    export_data = {
        "version": "1.0",
        # Missing required fields
    }
    
    response = client.post(
        "/api/submissions",
        headers={"Authorization": "Bearer test_token"},
        json={"export_data": export_data}
    )
    assert response.status_code == 200  # Returns validation errors
    data = response.json()
    assert data["status"] == "rejected"
    assert len(data["validation_errors"]) > 0