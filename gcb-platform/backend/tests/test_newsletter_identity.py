"""Canonical uniqueness and surviving legacy unsubscribe identities."""
from uuid import uuid4
import pytest
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.db.models.newsletter_subscriber_merge import NewsletterSubscriberMerge
from app.services.newsletter_links import unsubscribe_token, resubscribe_token


def test_database_rejects_case_and_whitespace_duplicates(db_session):
    db_session.add(Subscriber(email="Person@Example.com"))
    db_session.commit()
    db_session.add(Subscriber(email=" person@example.com "))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
    assert db_session.query(Subscriber).count() == 1


def test_legacy_unsubscribe_link_resolves_after_merge(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "NEWSLETTER_TOKEN_SECRET", "test-key-" * 8)
    survivor = Subscriber(email="person@example.com", is_active=True)
    db_session.add(survivor)
    db_session.flush()
    original_id = uuid4()
    db_session.add(NewsletterSubscriberMerge(original_id=original_id, subscriber_id=survivor.id,
                                             original_record={"email": "PERSON@example.com"}))
    db_session.commit()
    response = client.post("/api/newsletter/unsubscribe", json={"token": unsubscribe_token(original_id)})
    assert response.status_code == 200
    db_session.refresh(survivor)
    assert survivor.is_active is False
    assert survivor.sync_status == "pending"


def test_confirmation_for_removed_identity_is_not_reactivated(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "NEWSLETTER_TOKEN_SECRET", "test-key-" * 8)
    survivor = Subscriber(email="person@example.com", is_active=False)
    db_session.add(survivor)
    db_session.flush()
    original_id, nonce = uuid4(), uuid4()
    db_session.add(NewsletterSubscriberMerge(original_id=original_id, subscriber_id=survivor.id,
                                             original_record={"resubscribe_nonce": str(nonce)}))
    db_session.commit()
    response = client.post("/api/newsletter/confirm-resubscribe", json={"token": resubscribe_token(original_id, nonce)})
    assert response.status_code == 400
    db_session.refresh(survivor)
    assert survivor.is_active is False
    assert survivor.resubscribe_pending is False
