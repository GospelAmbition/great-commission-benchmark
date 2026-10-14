"""Tests for admin newsletter send modes and test-recipient management."""
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock
import pytest
from app.services.newsletter_sync import MailerLiteClient, MailerLiteError

from app.db.models.blog_post import BlogPost
from app.db.models.newsletter_campaign_send import NewsletterCampaignSend
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.db.models.newsletter_test_recipient import NewsletterTestRecipient
from app.core.config import settings
from app.services.email import EmailService
from app.services.newsletter import NewsletterService


def _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible):
    async def override_auth():
        return admin_user

    app.dependency_overrides[get_current_user] = override_auth
    app.dependency_overrides[require_admin] = override_auth
    app.dependency_overrides[require_admin_flexible] = override_auth


def _create_post(db_session, admin_user, status: str = "draft") -> BlogPost:
    post = BlogPost(
        title=f"Newsletter {status}",
        slug=f"newsletter-{status}-{uuid4()}",
        content="hello world",
        status=status,
        author_id=admin_user.id,
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)
    return post


class TestAdminNewsletterSend:
    def test_test_recipient_crud(self, client, db_session, admin_user, monkeypatch):
        from main import app
        from app.core.auth import get_current_user, require_admin
        from app.api.v1.endpoints.admin import require_admin_flexible

        _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible)
        monkeypatch.setattr(NewsletterService, "is_configured", staticmethod(lambda: False))

        created = client.post(
            "/api/admin/newsletter/test-recipients",
            json={"email": "qa@example.com", "name": "QA User", "notes": "internal"},
        )
        assert created.status_code == 200
        created_data = created.json()
        assert created_data["email"] == "qa@example.com"
        recipient_id = created_data["id"]

        listed = client.get("/api/admin/newsletter/test-recipients?status=active")
        assert listed.status_code == 200
        assert listed.json()["total"] == 1

        updated = client.patch(
            f"/api/admin/newsletter/test-recipients/{recipient_id}",
            json={"notes": "updated", "is_active": False},
        )
        assert updated.status_code == 200
        assert updated.json()["is_active"] is False

        deleted = client.delete(f"/api/admin/newsletter/test-recipients/{recipient_id}")
        assert deleted.status_code == 200

        app.dependency_overrides.clear()


class FakeMailerLite:
    def __init__(self):
        self.emails = {"member@example.com"}
        self.calls = []
        self.campaigns = 0
        self.fail_step = None
        self.status_code = None
        self.provider_status = "sent"
        self.on_create = None
        self.on_schedule = None
        self.webhook_ok = True

    async def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if path.startswith("/webhooks/"):
            return {"enabled": self.webhook_ok, "batchable": True, "url": settings.BACKEND_PUBLIC_URL.rstrip("/") + "/api/newsletter/webhooks/mailerlite",
                    "secret": settings.MAILERLITE_WEBHOOK_SECRET,
                    "events": ["subscriber.unsubscribed", "subscriber.bounced", "subscriber.spam_reported", "subscriber.deleted", "campaign.sent"]}
        if path.startswith("/groups/"):
            return {"data": [{"email": email, "status": "active"} for email in self.emails], "meta": {"next_cursor": None}}
        if path == "/campaigns":
            if self.fail_step == "create":
                raise MailerLiteError("Simulated create failure", status_code=self.status_code)
            self.campaigns += 1
            if self.on_create:
                self.on_create()
            return {"id": str(self.campaigns)}
        if path.endswith("/schedule"):
            if self.on_schedule:
                await self.on_schedule()
            if self.fail_step == "schedule":
                raise MailerLiteError("Simulated schedule failure", status_code=self.status_code)
            return {"id": path.split("/")[2]}
        if path.startswith("/campaigns/") and method == "GET":
            return {"id": path.split("/")[2], "status": self.provider_status}
        raise AssertionError(f"Unexpected provider call: {method} {path}")


@pytest.fixture
def campaign_setup(client, db_session, admin_user, monkeypatch):
    from main import app
    from app.core.auth import get_current_user, require_admin
    from app.api.v1.endpoints.admin import require_admin_flexible
    _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible)
    for name, value in {"MAILERLITE_API_KEY": "test", "MAILERLITE_PROD_GROUP_ID": "prod", "MAILERLITE_TEST_GROUP_ID": "qa",
                        "MAILERLITE_WEBHOOK_SECRET": "webhook-test", "MAILERLITE_WEBHOOK_ID": "hook", "NEWSLETTER_SYNC_ENABLED": True}.items():
        monkeypatch.setattr(settings, name, value)
    api = FakeMailerLite()
    monkeypatch.setattr(MailerLiteClient, "request", api.request)
    resend = AsyncMock(side_effect=AssertionError("Campaigns must never fall back to Resend"))
    monkeypatch.setattr(EmailService, "send_email", resend)
    post = _create_post(db_session, admin_user, status="published")
    db_session.add(NewsletterSubscriber(email="member@example.com", is_active=True, sync_status="synced",
                                       mailerlite_status="active", mailerlite_group_id="prod", mailerlite_synced_at=datetime.now(timezone.utc)))
    db_session.commit()
    payload = {"post_id": str(post.id), "audience": "production", "dry_run": False, "confirm_production_send": True}
    yield client, api, post, payload
    assert resend.await_count == 0


def test_dry_run_checks_live_group_without_creating_campaign(campaign_setup, db_session):
    client, api, post, payload = campaign_setup
    response = client.post("/api/admin/newsletter/send", json={**payload, "dry_run": True})
    assert response.status_code == 200
    assert response.json()["recipient_count"] == 1
    assert response.json()["target_group_id"] == "prod"
    assert response.json()["recipient_count_source"] == "verified_mailerlite_group"
    assert all(method == "GET" for method, _, _ in api.calls)
    assert db_session.query(NewsletterCampaignSend).count() == 0


def test_test_audience_allows_draft_and_routes_only_to_test_group(campaign_setup, db_session):
    client, api, post, payload = campaign_setup
    post.status = "draft"
    db_session.add(NewsletterTestRecipient(email="qa@example.com", is_active=True))
    db_session.commit()
    api.emails = {"qa@example.com"}
    response = client.post("/api/admin/newsletter/send", json={**payload, "audience": "test"})
    assert response.status_code == 200
    created = next(kwargs["json"] for method, path, kwargs in api.calls if method == "POST" and path == "/campaigns")
    assert created["groups"] == ["qa"]
    assert '{$unsubscribe}' in created["emails"][0]["content"]
    assert '{$unsubscribe}' in created["emails"][0]["plain_text"]
    assert "Designed and created by Gospel Ambition" in created["emails"][0]["content"]


@pytest.mark.parametrize("change,expected", [("draft", "published"), ("unconfirmed", "confirm_production_send")])
def test_production_guards(campaign_setup, db_session, change, expected):
    client, api, post, payload = campaign_setup
    if change == "draft":
        post.status = "draft"
        db_session.commit()
    else:
        payload["confirm_production_send"] = False
    response = client.post("/api/admin/newsletter/send", json=payload)
    assert response.status_code == 400
    assert expected in response.json()["detail"]
    assert api.calls == []


@pytest.mark.parametrize("emails", [set(), {"member@example.com", "unexpected@example.com"}])
def test_audience_mismatch_blocks_sending(campaign_setup, emails):
    client, api, post, payload = campaign_setup
    api.emails = emails
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 409
    assert all(method == "GET" for method, _, _ in api.calls)


def test_pending_unsubscribe_blocks_production(campaign_setup, db_session):
    client, api, post, payload = campaign_setup
    db_session.add(NewsletterSubscriber(email="optout@example.com", is_active=False, sync_status="pending"))
    db_session.commit()
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 409
    assert api.campaigns == 0


def test_webhook_configuration_must_match(campaign_setup):
    client, api, post, payload = campaign_setup
    api.webhook_ok = False
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 409
    assert api.campaigns == 0


def test_scheduled_is_not_sent_and_force_cannot_override_unresolved(campaign_setup, db_session):
    client, api, post, payload = campaign_setup
    response = client.post("/api/admin/newsletter/send", json=payload)
    assert response.status_code == 200
    send_id = response.json()["send_log_id"]
    assert db_session.query(NewsletterCampaignSend).one().status == "scheduled"
    assert client.post("/api/admin/newsletter/send", json={**payload, "force_resend": True}).status_code == 409
    refreshed = client.post(f"/api/admin/newsletter/sends/{send_id}/refresh")
    assert refreshed.json()["status"] == "sent"
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 409
    assert client.post("/api/admin/newsletter/send", json={**payload, "force_resend": True}).status_code == 200
    assert api.campaigns == 2


def test_duplicate_guard_separates_campaign_types(campaign_setup):
    client, api, post, payload = campaign_setup
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 200
    assert client.post("/api/admin/newsletter/send", json={**payload, "campaign_type": "highlight"}).status_code == 200
    assert api.campaigns == 2


@pytest.mark.parametrize("step", ["create", "schedule"])
def test_unknown_provider_outcome_blocks_automatic_retry(campaign_setup, db_session, step):
    client, api, post, payload = campaign_setup
    api.fail_step = step
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 502
    log = db_session.query(NewsletterCampaignSend).one()
    assert log.status == "uncertain"
    assert client.post("/api/admin/newsletter/send", json={**payload, "force_resend": True}).status_code == 409


def test_explicit_provider_rejection_is_recorded_without_fallback(campaign_setup, db_session):
    client, api, post, payload = campaign_setup
    api.fail_step, api.status_code = "create", 422
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 502
    assert db_session.query(NewsletterCampaignSend).one().status == "failed"


def test_audience_change_after_draft_creation_prevents_schedule(campaign_setup, db_session):
    client, api, post, payload = campaign_setup
    def change():
        sub = db_session.query(NewsletterSubscriber).one()
        sub.is_active = False
        sub.sync_status = "pending"
        db_session.commit()
    api.on_create = change
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 409
    assert not any(path.endswith("/schedule") for _, path, _ in api.calls)


def test_nested_concurrent_send_is_blocked_by_reservation(campaign_setup):
    client, api, post, payload = campaign_setup
    def second_request():
        assert client.post("/api/admin/newsletter/send", json=payload).status_code == 409
    api.on_create = second_request
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 200
    assert api.campaigns == 1


def test_campaign_sent_webhook_records_completion_without_regressing(campaign_setup, db_session):
    from app.services.newsletter_webhook import apply_webhook
    client, api, post, payload = campaign_setup
    async def sent_webhook():
        apply_webhook(db_session, {"event": "campaign.sent", "id": str(api.campaigns)})
    api.on_schedule = sent_webhook
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 200
    db_session.expire_all()
    assert db_session.query(NewsletterCampaignSend).one().status == "sent"


def test_failed_creation_can_be_resolved_without_scheduling(campaign_setup, db_session):
    client, api, post, payload = campaign_setup
    api.fail_step = "create"
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 502
    log = db_session.query(NewsletterCampaignSend).one()
    api.calls.clear()
    response = client.post(f"/api/admin/newsletter/sends/{log.id}/refresh")
    assert response.json()["status"] == "not_sent"
    assert api.calls == []
    api.fail_step = None
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 200


@pytest.mark.asyncio
async def test_status_refresh_cannot_regress_a_concurrent_webhook(campaign_setup, db_session):
    from app.services.newsletter_campaigns import refresh_send
    from app.services.newsletter_webhook import apply_webhook
    client, api, post, payload = campaign_setup
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 200
    log = db_session.query(NewsletterCampaignSend).one()
    class DelayedStatus:
        async def request(self, *args, **kwargs):
            apply_webhook(db_session, {"event": "campaign.sent", "id": log.campaign_id})
            return {"id": log.campaign_id, "status": "ready"}
    assert (await refresh_send(db_session, log, DelayedStatus()))["status"] == "sent"


def test_send_history_exposes_campaign_and_safe_diagnostics(campaign_setup):
    client, api, post, payload = campaign_setup
    api.fail_step, api.status_code = "create", 422
    assert client.post("/api/admin/newsletter/send", json=payload).status_code == 502
    history = client.get("/api/admin/newsletter/sends").json()["items"]
    assert history[0]["post_title"] == post.title
    assert history[0]["status"] == "failed"
    assert history[0]["target_group_id"] == "prod"
    assert history[0]["error_message"] == "Simulated create failure"


@pytest.mark.asyncio
async def test_group_verification_reads_all_pages_and_rejects_looping_cursor():
    from app.services.newsletter_campaigns import group_audience
    pages = [
        {"data": [{"email": "one@example.com", "status": "active"}], "meta": {"next_cursor": "next"}},
        {"data": [{"email": "two@example.com", "status": "active"}], "meta": {"next_cursor": None}},
    ]
    api = AsyncMock()
    api.request.side_effect = pages
    assert await group_audience(api, "prod") == {"one@example.com", "two@example.com"}
    assert api.request.call_args.kwargs["params"]["cursor"] == "next"
    api.request.side_effect = [pages[0], pages[0]]
    with pytest.raises(MailerLiteError, match="cursor"):
        await group_audience(api, "prod")
