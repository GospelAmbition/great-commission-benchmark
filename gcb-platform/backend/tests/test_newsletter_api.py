"""Tests for newsletter API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app



@pytest.fixture
def db(db_session):
    """Use the isolated shared test database."""
    return db_session

def test_subscribe_newsletter(db, client):
    """Test subscribing to newsletter"""
    response = client.post(
        "/api/newsletter/subscribe",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "message" in data


def test_subscribe_newsletter_duplicate(db, client):
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