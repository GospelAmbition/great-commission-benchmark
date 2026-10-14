"""Only confirmed ownership may request provider resubscription."""
import re
import time
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlparse
from unittest.mock import AsyncMock
from uuid import uuid4

import httpx
import pytest

from app.core.config import settings
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.services.email import EmailService
from app.services.newsletter_links import resubscribe_token
from app.services.newsletter_sync import MailerLiteClient, sync_one, MailerLiteError


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setattr(settings, "RECAPTCHA_ENABLED", False)
    monkeypatch.setattr(settings, "RESEND_API_KEY", "test-key")
    monkeypatch.setattr(settings, "MAILERLITE_API_KEY", "test-key")
    monkeypatch.setattr(settings, "MAILERLITE_PROD_GROUP_ID", "123")
    monkeypatch.setattr(settings, "NEWSLETTER_TOKEN_SECRET", "a-test-signing-secret-at-least-32-characters")
    mock = AsyncMock(return_value=True)
    monkeypatch.setattr(EmailService, "send_email", mock)
    return mock


def subscriber(db):
    sub = Subscriber(email="person@example.com", is_active=False, unsubscribed_at=datetime.now(timezone.utc))
    db.add(sub)
    db.commit()
    return sub


def request_link(client, sent):
    response = client.post("/api/newsletter/subscribe", json={"email": "PERSON@example.com"})
    assert response.status_code == 200
    assert response.json()["status"] == "confirmation_required"
    link = re.search(r'href="([^\"]+)"', sent.await_args.kwargs["html_content"]).group(1)
    return parse_qs(urlparse(link).query)["token"][0]


async def test_confirmed_request_remains_suppressed_until_verified(client, db_session, configured):
    sub = subscriber(db_session)
    token = request_link(client, configured)
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.resubscribe_pending is False
    assert client.get("/api/newsletter/confirm-resubscribe", params={"token": token}).status_code == 405
    response = client.post("/api/newsletter/confirm-resubscribe", json={"token": token})
    assert response.status_code == 200
    assert response.json()["status"] == "sync_pending"
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.resubscribe_pending is True
    assert sub.resubscribe_confirmed_at is not None
    api = SimpleNamespace(synchronize=AsyncMock(return_value={"id": "456", "status": "active"}))
    assert (await sync_one(db_session, sub.id, api))["status"] == "synced"
    assert api.synchronize.await_args.args[0].resubscribe is True
    db_session.refresh(sub)
    assert sub.is_active is True
    assert sub.resubscribe_pending is False
    assert sub.unsubscribed_at is None
    assert client.post("/api/newsletter/confirm-resubscribe", json={"token": token}).status_code == 400


def test_request_is_throttled_and_failure_can_retry(client, db_session, configured):
    subscriber(db_session)
    request_link(client, configured)
    assert client.post("/api/newsletter/subscribe", json={"email": "person@example.com"}).json()["status"] == "confirmation_required"
    assert configured.await_count == 1


def test_email_failure_keeps_suppression_and_clears_pending_link(client, db_session, configured):
    sub = subscriber(db_session)
    configured.return_value = False
    assert client.post("/api/newsletter/subscribe", json={"email": sub.email}).status_code == 503
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.resubscribe_nonce is None
    configured.return_value = True
    request_link(client, configured)
    assert configured.await_count == 2


def test_unsubscribe_cancels_unused_confirmation(client, db_session, configured):
    sub = subscriber(db_session)
    token = request_link(client, configured)
    assert client.post("/api/newsletter/unsubscribe", json={"email": sub.email}).status_code == 200
    assert client.post("/api/newsletter/confirm-resubscribe", json={"token": token}).status_code == 400
    db_session.refresh(sub)
    assert sub.is_active is False


def test_unsubscribe_cancels_confirmed_pending_sync(client, db_session, configured):
    sub = subscriber(db_session)
    token = request_link(client, configured)
    client.post("/api/newsletter/confirm-resubscribe", json={"token": token})
    client.post("/api/newsletter/unsubscribe", json={"email": sub.email})
    db_session.refresh(sub)
    assert sub.resubscribe_pending is False
    assert sub.is_active is False


def test_expired_or_replaced_confirmation_fails(client, db_session):
    sub = subscriber(db_session)
    sub.resubscribe_nonce = uuid4()
    db_session.commit()
    expired = resubscribe_token(sub.id, sub.resubscribe_nonce, expires=int(time.time()) - 1)
    replaced = resubscribe_token(sub.id, uuid4())
    for token in (expired, replaced):
        assert client.post("/api/newsletter/confirm-resubscribe", json={"token": token}).status_code == 400


async def test_only_confirmed_resubscription_sets_provider_flag():
    bodies = []
    def handler(request):
        import json
        if request.method == "POST":
            bodies.append(json.loads(request.content))
        status = "active" if bodies else "unsubscribed"
        return httpx.Response(200, json={"data": {"id": "456", "status": status, "groups": [{"id": "123"}]}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        api = MailerLiteClient(http)
        claim = SimpleNamespace(email="person@example.com", active=True, name=None, group_id="123", resubscribe=False)
        assert (await api.synchronize(claim))["status"] == "unsubscribed"
        assert bodies == []
        claim.resubscribe = True
        assert (await api.synchronize(claim))["status"] == "active"
    assert bodies[0]["resubscribe"] is True
    assert bodies[0]["status"] == "active"


@pytest.mark.parametrize("status", ["bounced", "junk", "unconfirmed"])
async def test_confirmation_does_not_override_delivery_restrictions(status):
    def handler(request):
        assert request.method == "GET"
        return httpx.Response(200, json={"data": {"id": "456", "status": status}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        claim = SimpleNamespace(email="person@example.com", active=True, resubscribe=True)
        assert (await MailerLiteClient(http).synchronize(claim))["status"] == status


async def test_confirmation_survives_retryable_sync_failure(client, db_session, configured):
    sub = subscriber(db_session)
    token = request_link(client, configured)
    client.post("/api/newsletter/confirm-resubscribe", json={"token": token})
    api = SimpleNamespace(synchronize=AsyncMock(side_effect=MailerLiteError("HTTP 503")))
    assert (await sync_one(db_session, sub.id, api))["status"] == "error"
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.resubscribe_pending is True


def test_old_optout_does_not_cancel_newer_confirmation(client, db_session, configured):
    from app.services.newsletter_webhook import apply_webhook
    sub = subscriber(db_session)
    token = request_link(client, configured)
    client.post("/api/newsletter/confirm-resubscribe", json={"token": token})
    result = apply_webhook(db_session, {"event": "subscriber.unsubscribed", "id": "456", "email": sub.email,
                                       "updated_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()})
    assert result["ignored"] == 1
    db_session.refresh(sub)
    assert sub.resubscribe_pending is True


async def test_new_optout_waits_for_older_provider_call_then_runs(client, db_session, configured):
    from app.services.newsletter_sync import _claim
    sub = subscriber(db_session)
    token = request_link(client, configured)
    client.post("/api/newsletter/confirm-resubscribe", json={"token": token})
    async def race(claim):
        assert claim.resubscribe is True
        client.post("/api/newsletter/unsubscribe", json={"email": sub.email})
        # A second worker must not overtake the old resubscribe request.
        assert _claim(db_session, sub.id) is None
        return {"id": "456", "status": "active"}
    assert (await sync_one(db_session, sub.id, SimpleNamespace(synchronize=race)))["status"] == "superseded"
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.resubscribe_pending is False
    assert sub.sync_lease_id is None
    next_claim = _claim(db_session, sub.id)
    assert next_claim is not None
    assert next_claim.active is False
