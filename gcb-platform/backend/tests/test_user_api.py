"""Tests for user API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

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
        name="Test User",
        role="user"
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


def test_get_profile(db, test_user, mock_auth):
    """Test getting user profile"""
    response = client.get(
        "/api/user/profile",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "stats" in data
    assert data["user"]["email"] == test_user.email


def test_update_profile(db, test_user, mock_auth):
    """Test updating user profile"""
    response = client.put(
        "/api/user/profile",
        headers={"Authorization": "Bearer test_token"},
        json={"name": "Updated Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["name"] == "Updated Name"


def test_get_user_tests(db, test_user, mock_auth):
    """Test getting user tests"""
    response = client.get(
        "/api/user/tests",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "tests" in data
    assert "pagination" in data


def test_get_user_submissions(db, test_user, mock_auth):
    """Test getting user submissions"""
    response = client.get(
        "/api/user/submissions",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "submissions" in data
    assert "pagination" in data


def test_get_user_activity(db, test_user, mock_auth):
    """Test getting user activity"""
    response = client.get(
        "/api/user/activity",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "activities" in data


def test_get_notification_preferences(db, test_user, mock_auth):
    """Test getting notification preferences"""
    response = client.get(
        "/api/user/notifications",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "preferences" in data


def test_update_notification_preferences(db, test_user, mock_auth):
    """Test updating notification preferences"""
    response = client.put(
        "/api/user/notifications",
        headers={"Authorization": "Bearer test_token"},
        json={
            "test_completed": False,
            "test_failed": True,
            "submission_approved": True,
            "submission_rejected": False,
            "payment_confirmation": True,
            "newsletter": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["preferences"]["test_completed"] == False