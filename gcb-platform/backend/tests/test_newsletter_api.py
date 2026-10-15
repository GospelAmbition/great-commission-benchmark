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

@pytest.mark.parametrize("source", ["article_end", None])
def test_signup_provenance_survives_repeat_signup_and_unsubscribe(db, client, source):
    from app.db.models.newsletter_subscriber import NewsletterSubscriber

    payload = {"email": "reader@example.com"}
    if source:
        payload["source"] = source
    assert client.post("/api/newsletter/subscribe", json=payload).status_code == 200
    sub = db.query(NewsletterSubscriber).filter_by(email="reader@example.com").one()
    original_id, original_time = sub.id, sub.subscribed_at
    assert sub.source == f"website:{source or 'newsletter_page'}"
    assert sub.consent_note == "Subscribed through the GCB newsletter signup form."
    assert sub.is_active and sub.sync_status == "pending" and original_time

    # A repeat signup must not replace the original opt-in provenance.
    assert client.post("/api/newsletter/subscribe", json={**payload, "source": "footer"}).status_code == 200
    assert client.post("/api/newsletter/unsubscribe", json={"email": payload["email"]}).status_code == 200
    db.expire_all()
    retained = db.query(NewsletterSubscriber).filter_by(email=payload["email"]).one()
    assert retained.id == original_id and retained.subscribed_at == original_time
    assert retained.source == f"website:{source or 'newsletter_page'}"
    assert retained.consent_note == "Subscribed through the GCB newsletter signup form."
    assert retained.is_active is False and retained.unsubscribed_at is not None


def test_signup_rejects_unrecognized_source_without_storing_it(db, client):
    from app.db.models.newsletter_subscriber import NewsletterSubscriber

    response = client.post("/api/newsletter/subscribe", json={"email": "reader@example.com", "source": "someone@example.com"})
    assert response.status_code == 422
    assert db.query(NewsletterSubscriber).count() == 0
