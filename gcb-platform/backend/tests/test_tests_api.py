"""Tests for tests API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, AsyncMock

from app.main import app
from app.db.base import Base, engine, SessionLocal
from app.db.models.user import User
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.methodology_version import MethodologyVersion
from app.core.auth import get_current_user

client = TestClient(app)


@pytest.fixture
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_data(db: Session):
    """Create test data"""
    user = User(
        auth0_id="test|123",
        email="test@example.com",
        name="Test User"
    )
    db.add(user)
    
    question_set = QuestionSet(
        semantic_version="1.0",
        marketing_version="Version 1",
        status="active"
    )
    db.add(question_set)
    db.commit()
    db.refresh(question_set)
    
    methodology_version = MethodologyVersion(
        question_set_id=question_set.id,
        judge_prompt="Test prompt",
        scoring_config={},
        active_from=question_set.created_at
    )
    db.add(methodology_version)
    
    model = Model(
        model_id="test/model",
        name="Test Model",
        provider="Test Provider",
        is_active=True,
        estimated_cost_per_test=20.0
    )
    db.add(model)
    db.commit()
    db.refresh(user)
    db.refresh(model)
    db.refresh(question_set)
    db.refresh(methodology_version)
    
    return {
        "user": user,
        "model": model,
        "question_set": question_set,
        "methodology_version": methodology_version
    }


@pytest.fixture
def mock_auth(test_data):
    """Mock authentication"""
    async def mock_get_current_user():
        return test_data["user"]
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


def test_create_test(db, test_data, mock_auth):
    """Test creating a test"""
    response = client.post(
        "/api/tests",
        headers={"Authorization": "Bearer test_token"},
        json={
            "model_id": str(test_data["model"].id),
            "question_set_id": str(test_data["question_set"].id)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "test_id" in data
    assert "cost_estimate" in data
    assert data["status"] == "pending_payment"


def test_start_test(db, test_data, mock_auth):
    """Test starting a test"""
    from app.db.models.test_run import TestRun
    
    # Create a pending test
    test_run = TestRun(
        user_id=test_data["user"].id,
        model_id=test_data["model"].id,
        question_set_id=test_data["question_set"].id,
        methodology_version_id=test_data["methodology_version"].id,
        status="pending_payment"
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    response = client.post(
        f"/api/tests/{test_run.id}/start",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"


def test_get_test_progress(db, test_data, mock_auth):
    """Test getting test progress"""
    from app.db.models.test_run import TestRun
    
    test_run = TestRun(
        user_id=test_data["user"].id,
        model_id=test_data["model"].id,
        question_set_id=test_data["question_set"].id,
        methodology_version_id=test_data["methodology_version"].id,
        status="running"
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    response = client.get(
        f"/api/tests/{test_run.id}/progress",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "progress" in data
    assert "status" in data


def test_cancel_test(db, test_data, mock_auth):
    """Test cancelling a test"""
    from app.db.models.test_run import TestRun
    
    test_run = TestRun(
        user_id=test_data["user"].id,
        model_id=test_data["model"].id,
        question_set_id=test_data["question_set"].id,
        methodology_version_id=test_data["methodology_version"].id,
        status="pending_payment"
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    response = client.post(
        f"/api/tests/{test_run.id}/cancel",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"