"""Tests for submissions API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.base import Base, engine, SessionLocal
from app.db.models.user import User
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


def test_upload_submission_valid(db, test_user, mock_auth):
    """Test uploading a valid submission"""
    export_data = {
        "version": "1.0",
        "model": {
            "name": "Test Model",
            "provider": "Test Provider"
        },
        "questions": [
            {"id": "q1", "content": "Question 1"},
            {"id": "q2", "content": "Question 2"}
        ],
        "results": [
            {"question_id": "q1", "verdict": "ACCEPTED", "response": "Response 1"},
            {"question_id": "q2", "verdict": "COMPROMISED", "response": "Response 2"}
        ],
        "cli_version": "1.0"
    }
    
    response = client.post(
        "/api/submissions",
        headers={"Authorization": "Bearer test_token"},
        json={"export_data": export_data}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert "submission_id" in data


def test_upload_submission_invalid(db, test_user, mock_auth):
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