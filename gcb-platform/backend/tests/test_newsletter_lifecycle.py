"""Authenticated provider callbacks and recipient unsubscribe links."""
import hashlib
import hmac
import json
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest

from app.core.config import settings
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.db.models.newsletter_webhook_event import NewsletterWebhookEvent
from app.services.newsletter_links import unsubscribe_token, read_unsubscribe_token
from app.services.newsletter_sync import MailerLiteClient, _claim, sync_one


@pytest.fixture(autouse=True)
def configure(monkeypatch):
    monkeypatch.setattr(settings, "MAILERLITE_WEBHOOK_SECRET", "webhook-test-secret")
    monkeypatch.setattr(settings, "NEWSLETTER_TOKEN_SECRET", "test-signing-key-with-at-least-32-characters")
    monkeypatch.setattr(settings, "MAILERLITE_API_KEY", "test-key")
    monkeypatch.setattr(settings, "MAILERLITE_PROD_GROUP_ID", "123")


def event(kind="subscriber.unsubscribed", **kwargs):
    return {"event": kind, "id": "456", "email": "PERSON@example.com", "status": "active",
            "updated_at": "2026-10-14T10:00:00Z", **kwargs}


def send(client, payload, valid=True):
    body = json.dumps(payload).encode()
    signature = hmac.new(settings.MAILERLITE_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/api/newsletter/webhooks/mailerlite", content=body,
                       headers={"Content-Type": "application/json", "Signature": signature if valid else "invalid"})


def add_subscriber(db, **kwargs):
    sub = Subscriber(email="person@example.com", **kwargs)
    db.add(sub)
    db.commit()
    return sub


def test_unsigned_or_tampered_webhook_never_changes_state(client, db_session):
    sub = add_subscriber(db_session)
    assert send(client, event(), valid=False).status_code == 401
    db_session.refresh(sub)
    assert sub.is_active is True
    assert db_session.query(NewsletterWebhookEvent).count() == 0


def test_missing_webhook_secret_is_not_silently_accepted(client, monkeypatch):
    monkeypatch.setattr(settings, "MAILERLITE_WEBHOOK_SECRET", "")
    assert send(client, event()).status_code == 503


@pytest.mark.parametrize("kind,status", [("subscriber.unsubscribed", "unsubscribed"), ("subscriber.bounced", "bounced"), ("subscriber.spam_reported", "junk")])
def test_provider_optout_overrides_stale_active_payload_and_is_idempotent(client, db_session, kind, status):
    sub = add_subscriber(db_session)
    claimed = _claim(db_session, sub.id)
    response = send(client, event(kind))
    assert response.status_code == 200
    assert response.json()["applied"] == 1
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.mailerlite_status == status
    assert sub.sync_revision > claimed.revision
    assert sub.sync_lease_id == claimed.lease
    assert sub.sync_status == "pending"
    assert send(client, event(kind)).json()["duplicates"] == 1
    assert db_session.query(NewsletterWebhookEvent).count() == 1


def test_unknown_subscriber_optout_is_retained(client, db_session):
    assert send(client, event()).status_code == 200
    sub = db_session.query(Subscriber).one()
    assert sub.email == "person@example.com"
    assert sub.is_active is False
    assert sub.source == "mailerlite_webhook"


def test_batch_handles_nested_and_flat_events(client, db_session):
    payload = {"events": [event(), {"type": "subscriber.spam_reported", "subscriber": {
        "id": "789", "email": "other@example.com", "updated_at": "2026-10-14T10:00:00Z"}}]}
    result = send(client, payload)
    assert result.status_code == 200
    assert result.json()["applied"] == 2
    assert db_session.query(Subscriber).filter(Subscriber.is_active == False).count() == 2


def test_bad_batch_is_atomic(client, db_session):
    result = send(client, {"events": [event(), event(email="not-an-email")]})
    assert result.status_code == 400
    assert db_session.query(Subscriber).count() == 0
    assert db_session.query(NewsletterWebhookEvent).count() == 0


def test_late_event_cannot_override_newer_suppression_reason(client, db_session):
    send(client, event("subscriber.spam_reported"))
    response = send(client, event(updated_at="2026-10-13T10:00:00Z"))
    assert response.json()["ignored"] == 1
    assert db_session.query(Subscriber).one().mailerlite_status == "junk"


def test_active_event_does_not_reactivate_local_optout(client, db_session):
    sub = add_subscriber(db_session, is_active=False)
    assert send(client, event("subscriber.active")).json()["ignored"] == 1
    db_session.refresh(sub)
    assert sub.is_active is False


async def test_rechecking_deleted_record_does_not_recreate_it(client, db_session):
    send(client, {"type": "subscriber.deleted", "subscriber": event()})
    sub = db_session.query(Subscriber).one()
    assert sub.mailerlite_status == "deleted"
    calls = []
    def handler(request):
        calls.append(request.method)
        return httpx.Response(404)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        result = await MailerLiteClient(http).synchronize(SimpleNamespace(
            email=sub.email, active=False, remote_status="deleted", remote_id="456"))
    assert result["status"] == "deleted"
    assert calls == ["GET"]


async def test_webhook_during_outbound_sync_wins(client, db_session):
    sub = add_subscriber(db_session)
    async def concurrent(claim):
        send(client, event())
        return {"id": "456", "status": "active", "groups": [{"id": "123"}]}
    assert (await sync_one(db_session, sub.id, SimpleNamespace(synchronize=concurrent)))["status"] == "superseded"
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.sync_status == "pending"  # Correct any late provider-side mutation.


def test_signed_unsubscribe_is_post_only_and_repeatable(client, db_session):
    sub = add_subscriber(db_session)
    token = unsubscribe_token(sub.id)
    assert "person@example.com" not in token
    assert read_unsubscribe_token(token) == sub.id
    assert client.get("/api/newsletter/unsubscribe", params={"token": token}).status_code == 405
    db_session.refresh(sub)
    assert sub.is_active is True
    for _ in range(2):
        result = client.post("/api/newsletter/unsubscribe", json={"token": token})
        assert result.status_code == 200
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.sync_status == "pending"


def test_modified_token_cannot_unsubscribe_another_person(client, db_session):
    sub = add_subscriber(db_session)
    token = unsubscribe_token(uuid4())
    # Swap the subject without recomputing its signature.
    parts = token.split(".")
    parts[2] = str(sub.id)
    assert client.post("/api/newsletter/unsubscribe", json={"token": ".".join(parts)}).status_code == 400
    db_session.refresh(sub)
    assert sub.is_active is True


def test_email_unsubscribe_response_does_not_reveal_membership(client, db_session):
    add_subscriber(db_session)
    known = client.post("/api/newsletter/unsubscribe", json={"email": "PERSON@example.com"})
    unknown = client.post("/api/newsletter/unsubscribe", json={"email": "unknown@example.com"})
    assert known.json() == unknown.json()
    assert client.post("/api/newsletter/unsubscribe", json={}).status_code == 422


def test_non_ascii_token_is_rejected(client):
    token = f"unsubscribe.v1.{uuid4()}.é"
    assert client.post("/api/newsletter/unsubscribe", json={"token": token}).status_code == 400


def test_platform_signed_link_unsubscribes_its_recipient(client, db_session):
    from urllib.parse import urlparse, parse_qs
    from app.services.newsletter_links import unsubscribe_url
    sub = add_subscriber(db_session)
    token = parse_qs(urlparse(unsubscribe_url(sub.id)).query)["token"][0]
    assert read_unsubscribe_token(token) == sub.id
    assert client.post("/api/newsletter/unsubscribe", json={"token": token}).status_code == 200
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.sync_status == "pending"
