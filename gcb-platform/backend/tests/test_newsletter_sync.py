"""Provider contract and durable sync queue regression tests."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from app.core.config import settings
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.services.newsletter_sync import MailerLiteClient, MailerLiteError, queue_sync, sync_one, _claim


@pytest.fixture(autouse=True)
def configured(monkeypatch):
    monkeypatch.setattr(settings, "MAILERLITE_API_KEY", "test-key")
    monkeypatch.setattr(settings, "MAILERLITE_PROD_GROUP_ID", "123")


def add_subscriber(db, **kwargs):
    sub = Subscriber(email="person@example.com", **kwargs)
    db.add(sub)
    db.commit()
    return sub


def remote(status="active", groups=None):
    return {"id": "456", "email": "person@example.com", "status": status,
            "groups": groups if groups is not None else [{"id": "123"}]}


def claim(active=True):
    return SimpleNamespace(email="person@example.com", active=active, name="Person", group_id="123")


async def test_active_upsert_omits_reactivation_and_verifies_membership():
    requests = []
    def handler(request):
        import json
        requests.append(request)
        if request.method == "POST":
            body = json.loads(request.content)
            assert body == {"email": "person@example.com", "groups": ["123"], "fields": {"name": "Person"}}
        return httpx.Response(200, json={"data": remote()})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        assert (await MailerLiteClient(http).synchronize(claim()))["status"] == "active"
    assert [r.method for r in requests] == ["GET", "POST", "GET"]


@pytest.mark.parametrize("status", ["unsubscribed", "bounced", "junk", "unconfirmed"])
async def test_remote_suppression_never_upserts_active(status):
    def handler(request):
        assert request.method == "GET"
        return httpx.Response(200, json={"data": remote(status)})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        assert (await MailerLiteClient(http).synchronize(claim()))["status"] == status


async def test_missing_group_is_not_success():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200, json={"data": remote(groups=[])}))) as http:
        with pytest.raises(MailerLiteError, match="membership"):
            await MailerLiteClient(http).synchronize(claim())


async def test_unsubscribe_missing_address_creates_suppression():
    calls = []
    def handler(request):
        import json
        calls.append(request.method)
        if len(calls) == 1:
            return httpx.Response(404)
        if request.method == "POST":
            assert json.loads(request.content) == {"email": "person@example.com", "status": "unsubscribed"}
        return httpx.Response(200, json={"data": remote("unsubscribed")})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        await MailerLiteClient(http).synchronize(claim(False))
    assert calls == ["GET", "POST", "GET"]


async def test_failed_lookup_is_not_treated_as_missing():
    calls = []
    def handler(request):
        calls.append(request.method)
        return httpx.Response(401, json={"secret": "must-not-leak"})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        with pytest.raises(MailerLiteError, match="HTTP 401") as exc:
            await MailerLiteClient(http).synchronize(claim(False))
    assert "must-not-leak" not in str(exc.value)
    assert calls == ["GET"]


async def test_queue_success_and_remote_optout(db_session):
    sub = add_subscriber(db_session)
    api = SimpleNamespace(synchronize=AsyncMock(return_value=remote("unsubscribed")))
    result = await sync_one(db_session, sub.id, api)
    db_session.refresh(sub)
    assert result["status"] == "synced"
    assert sub.is_active is False
    assert sub.mailerlite_status == "unsubscribed"
    assert sub.mailerlite_synced_at is not None
    assert sub.unsubscribed_at is not None
    assert sub.sync_attempts == 1


async def test_retry_is_persistent_and_honors_backoff(db_session):
    sub = add_subscriber(db_session, is_active=False)
    api = SimpleNamespace(synchronize=AsyncMock(side_effect=MailerLiteError("HTTP 429", retry_after=600)))
    result = await sync_one(db_session, sub.id, api)
    db_session.refresh(sub)
    assert result["status"] == "error"
    assert sub.sync_error == "HTTP 429"
    assert sub.sync_next_attempt_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc) + timedelta(seconds=590)
    assert sub.is_active is False
    assert (await sync_one(db_session, sub.id, api))["status"] == "idle"
    assert api.synchronize.await_count == 1
    queue_sync(sub)
    db_session.commit()
    assert (await sync_one(db_session, sub.id, SimpleNamespace(synchronize=AsyncMock(return_value=remote("unsubscribed")))))["status"] == "synced"


async def test_stale_response_cannot_overwrite_new_unsubscribe(db_session):
    sub = add_subscriber(db_session)
    async def race(claim):
        sub.is_active = False
        queue_sync(sub)
        db_session.commit()
        return remote()
    result = await sync_one(db_session, sub.id, SimpleNamespace(synchronize=race))
    db_session.refresh(sub)
    assert result["status"] == "superseded"
    assert sub.is_active is False
    assert sub.sync_status == "pending"
    assert sub.mailerlite_synced_at is None


async def test_expired_lease_is_recovered(db_session):
    sub = add_subscriber(db_session)
    first = _claim(db_session, sub.id)
    assert first is not None
    assert _claim(db_session, sub.id) is None
    db_session.refresh(sub)
    sub.sync_lease_until = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    second = _claim(db_session, sub.id)
    assert second.lease != first.lease
    assert second.attempts == 2


async def test_missing_configuration_leaves_work_pending(db_session, monkeypatch):
    monkeypatch.setattr(settings, "MAILERLITE_API_KEY", "")
    sub = add_subscriber(db_session)
    assert (await sync_one(db_session, sub.id))["status"] == "not_configured"
    db_session.refresh(sub)
    assert sub.sync_status == "pending"
    assert sub.sync_attempts == 0


@pytest.fixture
def admin_client(client, admin_user):
    from main import app
    from app.core.auth import require_admin
    app.dependency_overrides[require_admin] = lambda: admin_user
    return client


def test_admin_unsubscribe_retains_suppression(admin_client, db_session):
    sub = add_subscriber(db_session)
    response = admin_client.delete(f"/api/admin/newsletter/subscribers/{sub.id}")
    assert response.status_code == 200
    db_session.refresh(sub)
    assert sub.is_active is False
    assert sub.sync_status == "pending"
    assert db_session.query(Subscriber).count() == 1


def test_admin_sync_failure_is_not_reported_as_success(admin_client, db_session, monkeypatch):
    sub = add_subscriber(db_session)
    monkeypatch.setattr(MailerLiteClient, "synchronize", AsyncMock(side_effect=MailerLiteError("HTTP 500")))
    assert admin_client.post(f"/api/admin/newsletter/subscribers/{sub.id}/sync").status_code == 502
    db_session.refresh(sub)
    assert sub.sync_status == "error"


def test_stats_do_not_count_stored_provider_id_as_verification(admin_client, db_session):
    add_subscriber(db_session, mailerlite_subscriber_id="456")
    data = admin_client.get("/api/admin/newsletter/stats").json()
    assert data["synced_to_mailerlite"] == 0
    assert data["sync_pending"] == 1


def test_queue_reconciliation_does_not_send(admin_client, db_session):
    sub = add_subscriber(db_session, sync_status="synced")
    response = admin_client.post("/api/admin/newsletter/sync/retry?reconcile=true")
    assert response.json()["queued"] == 1
    db_session.refresh(sub)
    assert sub.sync_status == "pending"
    assert sub.sync_revision == 2


def test_connection_verifies_groups_and_checks_separation(admin_client, monkeypatch):
    monkeypatch.setattr(settings, "MAILERLITE_TEST_GROUP_ID", "789")
    request = AsyncMock(return_value=[{"id": "123", "name": "Production"}, {"id": "789", "name": "QA"}])
    monkeypatch.setattr(MailerLiteClient, "request", request)
    response = admin_client.get("/api/admin/newsletter/connection")
    assert response.status_code == 200
    assert response.json()["groups"]["production"]["id"] == "123"
    request.assert_awaited_once_with("GET", "/groups", params={"limit": 1000})
    monkeypatch.setattr(settings, "MAILERLITE_TEST_GROUP_ID", "123")
    assert admin_client.get("/api/admin/newsletter/connection").status_code == 400


def test_connection_missing_group_fails(admin_client, monkeypatch):
    monkeypatch.setattr(MailerLiteClient, "request", AsyncMock(return_value=[]))
    assert admin_client.get("/api/admin/newsletter/connection").status_code == 502
