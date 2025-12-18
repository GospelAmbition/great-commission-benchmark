"""Tests for admin endpoints"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.models.user import User

client = TestClient(app)


@pytest.fixture
def admin_user(db_session):
    """Create admin user"""
    user = User(
        auth0_id="admin_auth0_id",
        email="admin@example.com",
        name="Admin",
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_list_users(admin_user, auth_headers):
    """Test listing users"""
    response = client.get(
        "/api/v1/admin/users",
        headers=auth_headers(admin_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data


def test_update_user_role(admin_user, db_session, auth_headers):
    """Test updating user role"""
    test_user = User(
        auth0_id="test_user",
        email="testuser@example.com",
        role="user"
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    
    response = client.put(
        f"/api/v1/admin/users/{test_user.id}/role",
        json={"role": "moderator"},
        headers=auth_headers(admin_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "moderator"


def test_get_admin_stats(admin_user, auth_headers):
    """Test getting admin stats"""
    response = client.get(
        "/api/v1/admin/stats",
        headers=auth_headers(admin_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "tests" in data
    assert "revenue" in data
    assert "moderation" in data


def test_admin_requires_role(db_session):
    """Test that admin endpoints require admin role"""
    regular_user = User(
        auth0_id="regular_user",
        email="user@example.com",
        role="user"
    )
    db_session.add(regular_user)
    db_session.commit()
    
    response = client.get(
        "/api/v1/admin/users",
        headers=auth_headers(regular_user)
    )
    
    assert response.status_code == 403
