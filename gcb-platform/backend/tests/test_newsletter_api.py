"""Tests for newsletter API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.base import Base, engine, SessionLocal

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


def test_subscribe_newsletter(db):
    """Test subscribing to newsletter"""
    response = client.post(
        "/api/newsletter/subscribe",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "message" in data


def test_subscribe_newsletter_duplicate(db):
    """Test subscribing with duplicate email"""
    # First subscription
    client.post(
        "/api/newsletter/subscribe",
        json={"email": "test2@example.com"}
    )
    
    # Second subscription (should handle gracefully)
    response = client.post(
        "/api/newsletter/subscribe",
        json={"email": "test2@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True