"""Tests for admin newsletter send modes and test-recipient management."""
from uuid import uuid4

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

    def test_send_dry_run_test_audience(self, client, db_session, admin_user):
        from main import app
        from app.core.auth import get_current_user, require_admin
        from app.api.v1.endpoints.admin import require_admin_flexible

        _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible)

        post = _create_post(db_session, admin_user, status="draft")
        db_session.add(NewsletterTestRecipient(email="qa1@example.com", is_active=True))
        db_session.commit()

        response = client.post(
            "/api/admin/newsletter/send",
            json={"post_id": str(post.id), "dry_run": True, "audience": "test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["audience"] == "test"
        assert data["recipient_count"] == 1
        assert data["post_status"] == "draft"

        app.dependency_overrides.clear()

    def test_send_production_requires_published(self, client, db_session, admin_user):
        from main import app
        from app.core.auth import get_current_user, require_admin
        from app.api.v1.endpoints.admin import require_admin_flexible

        _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible)

        post = _create_post(db_session, admin_user, status="draft")
        response = client.post(
            "/api/admin/newsletter/send",
            json={
                "post_id": str(post.id),
                "dry_run": False,
                "audience": "production",
                "confirm_production_send": True,
            },
        )
        assert response.status_code == 400
        assert "published" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_send_production_requires_confirmation(self, client, db_session, admin_user):
        from main import app
        from app.core.auth import get_current_user, require_admin
        from app.api.v1.endpoints.admin import require_admin_flexible

        _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible)

        post = _create_post(db_session, admin_user, status="published")
        response = client.post(
            "/api/admin/newsletter/send",
            json={
                "post_id": str(post.id),
                "dry_run": False,
                "audience": "production",
                "confirm_production_send": False,
            },
        )
        assert response.status_code == 400
        assert "confirm_production_send" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_send_production_duplicate_guard(self, client, db_session, admin_user, monkeypatch):
        from main import app
        from app.core.auth import get_current_user, require_admin
        from app.api.v1.endpoints.admin import require_admin_flexible

        _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible)

        post = _create_post(db_session, admin_user, status="published")
        db_session.add(NewsletterSubscriber(email="member@example.com", is_active=True))
        db_session.commit()

        sent_to: list[str] = []

        async def fake_send_email(to: str, subject: str, html_content: str, from_email: str | None = None):
            sent_to.append(to)
            return True

        monkeypatch.setattr(settings, "RESEND_API_KEY", "re_test")
        monkeypatch.setattr(EmailService, "send_email", staticmethod(fake_send_email))

        payload = {
            "post_id": str(post.id),
            "dry_run": False,
            "audience": "production",
            "confirm_production_send": True,
        }
        first = client.post("/api/admin/newsletter/send", json=payload)
        assert first.status_code == 200
        first_data = first.json()
        assert first_data["campaign_id"].startswith("resend:")
        assert first_data["send_log_id"]
        assert sent_to == ["member@example.com"]

        second = client.post("/api/admin/newsletter/send", json=payload)
        assert second.status_code == 409

        forced = client.post(
            "/api/admin/newsletter/send",
            json={**payload, "force_resend": True},
        )
        assert forced.status_code == 200
        assert sent_to == ["member@example.com", "member@example.com"]

        send_count = db_session.query(NewsletterCampaignSend).filter(
            NewsletterCampaignSend.post_id == post.id,
            NewsletterCampaignSend.audience == "production",
            NewsletterCampaignSend.status == "sent",
        ).count()
        assert send_count == 2

        attempt_count = db_session.query(NewsletterCampaignSend).filter(
            NewsletterCampaignSend.post_id == post.id,
            NewsletterCampaignSend.audience == "production",
        ).count()
        assert attempt_count == 3

        app.dependency_overrides.clear()

    def test_send_duplicate_guard_is_separate_by_campaign_type(self, client, db_session, admin_user, monkeypatch):
        from main import app
        from app.core.auth import get_current_user, require_admin
        from app.api.v1.endpoints.admin import require_admin_flexible

        _set_admin_overrides(app, admin_user, get_current_user, require_admin, require_admin_flexible)

        post = _create_post(db_session, admin_user, status="published")
        db_session.add(NewsletterSubscriber(email="member@example.com", is_active=True))
        db_session.commit()

        sent_subjects: list[str] = []

        async def fake_send_email(to: str, subject: str, html_content: str, from_email: str | None = None):
            sent_subjects.append(subject)
            return True

        monkeypatch.setattr(settings, "RESEND_API_KEY", "re_test")
        monkeypatch.setattr(EmailService, "send_email", staticmethod(fake_send_email))

        base_payload = {
            "post_id": str(post.id),
            "dry_run": False,
            "audience": "production",
            "confirm_production_send": True,
        }
        newsletter = client.post("/api/admin/newsletter/send", json=base_payload)
        assert newsletter.status_code == 200
        assert newsletter.json()["campaign_type"] == "newsletter"

        highlight_payload = {**base_payload, "campaign_type": "highlight"}
        highlight = client.post("/api/admin/newsletter/send", json=highlight_payload)
        assert highlight.status_code == 200
        assert highlight.json()["campaign_type"] == "highlight"

        duplicate_highlight = client.post("/api/admin/newsletter/send", json=highlight_payload)
        assert duplicate_highlight.status_code == 409

        sent_logs = db_session.query(NewsletterCampaignSend).filter(
            NewsletterCampaignSend.post_id == post.id,
            NewsletterCampaignSend.audience == "production",
            NewsletterCampaignSend.status == "sent",
        ).all()
        assert sorted(log.campaign_type for log in sent_logs) == ["highlight", "newsletter"]

        app.dependency_overrides.clear()
