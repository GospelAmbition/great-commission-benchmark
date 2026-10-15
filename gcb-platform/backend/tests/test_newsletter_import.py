"""Imports preserve suppression, validate consent, and never send email."""
from unittest.mock import AsyncMock

import pytest

from app.db.models.action_log import ActionLog
from app.db.models.newsletter_subscriber import NewsletterSubscriber
from app.services.newsletter import NewsletterService


@pytest.fixture
def admin_client(client, admin_user, monkeypatch):
    from main import app
    from app.core.auth import require_admin

    app.dependency_overrides[require_admin] = lambda: admin_user
    # Fail the test if imports attempt to contact MailerLite.
    sync = AsyncMock(side_effect=AssertionError("Imports must not call MailerLite"))
    monkeypatch.setattr(NewsletterService, "sync_subscriber_to_mailerlite", sync)
    monkeypatch.setattr(NewsletterService, "remove_subscriber_from_mailerlite", sync)
    yield client
    assert sync.await_count == 0


def submit(client, csv, **kwargs):
    return client.post("/api/admin/newsletter/subscribers/import", json={
        "csv_content": csv, "source": "Google Form September", **kwargs,
    })


def test_preview_does_not_write(admin_client, db_session):
    result = submit(admin_client, '\ufeffTimestamp,Email Address,Name\n2026-09-01, Person@Example.com ,"Doe, Jane"\n')
    assert result.status_code == 200
    assert result.json()["counts"] == {"create_active": 1}
    assert result.json()["rows"][0]["email"] == "person@example.com"
    assert result.json()["requires_consent"] is True
    assert db_session.query(NewsletterSubscriber).count() == 0
    assert db_session.query(ActionLog).count() == 0


def test_apply_records_provenance_and_is_repeatable(admin_client, db_session, admin_user):
    csv = 'Email Address,Name\nPERSON@example.com,"Doe, Jane"\n'
    options = dict(dry_run=False, confirm_subscribed=True, consent_note="Selected newsletter opt-in")
    result = submit(admin_client, csv, **options)
    assert result.status_code == 200
    subscriber = db_session.query(NewsletterSubscriber).one()
    assert subscriber.email == "person@example.com"
    assert subscriber.name == "Doe, Jane"
    assert subscriber.source == "Google Form September"
    assert subscriber.consent_note == "Selected newsletter opt-in"
    assert subscriber.imported_at is not None
    assert str(subscriber.import_batch_id) == result.json()["batch_id"]
    log = db_session.query(ActionLog).one()
    assert log.action == "newsletter.import"
    assert log.actor_user_id == admin_user.id
    again = submit(admin_client, csv, **options)
    assert again.json()["counts"] == {"unchanged": 1}
    assert db_session.query(NewsletterSubscriber).count() == 1


@pytest.mark.parametrize("options", [{}, {"confirm_subscribed": True}, {"consent_note": "opted in"}])
def test_consent_required_for_new_active_rows(admin_client, db_session, options):
    response = submit(admin_client, "email\na@example.com\n", dry_run=False, **options)
    assert response.status_code == 400
    assert db_session.query(NewsletterSubscriber).count() == 0
    assert db_session.query(ActionLog).count() == 0


def test_existing_unsubscribe_is_preserved_case_insensitively(admin_client, db_session):
    db_session.add(NewsletterSubscriber(email="PERSON@Example.com", is_active=False))
    db_session.commit()
    response = submit(admin_client, "email\nperson@example.com\n", dry_run=False)
    assert response.json()["counts"] == {"protected": 1}
    assert db_session.query(NewsletterSubscriber).one().is_active is False


@pytest.mark.parametrize("statuses", ["active,unsubscribed", "unsubscribed,active"])
def test_file_suppression_wins_regardless_of_row_order(admin_client, db_session, statuses):
    first, second = statuses.split(",")
    response = submit(admin_client, f"email,status\na@example.com,{first}\nA@EXAMPLE.COM,{second}\n", dry_run=False)
    assert response.status_code == 200
    assert response.json()["counts"] == {"duplicate": 1, "create_unsubscribed": 1}
    subscriber = db_session.query(NewsletterSubscriber).one()
    assert subscriber.is_active is False
    assert subscriber.unsubscribed_at is not None


def test_suppression_import_deactivates_existing_records(admin_client, db_session):
    # Exercise legacy pre-037 data; current-schema writes cannot create variants.
    from sqlalchemy import text
    db_session.execute(text("DROP INDEX uq_newsletter_subscribers_canonical_email"))
    db_session.add_all([
        NewsletterSubscriber(email="A@example.com", is_active=True),
        NewsletterSubscriber(email="a@example.com", is_active=False),
    ])
    db_session.commit()
    response = submit(admin_client, "email,status\na@example.com,unsubscribed\n", dry_run=False)
    assert response.json()["counts"] == {"unsubscribe": 1}
    assert not any(s.is_active for s in db_session.query(NewsletterSubscriber).all())


def test_invalid_rows_are_reported_without_guessing_status(admin_client, db_session):
    response = submit(admin_client, "email,status\nbad,active\na@example.com,maybe\nb@example.com,\nc@example.com,unsubscribed\n", dry_run=False)
    assert response.status_code == 200
    assert response.json()["counts"] == {"invalid": 3, "create_unsubscribed": 1}
    assert db_session.query(NewsletterSubscriber).one().email == "c@example.com"


def test_custom_columns_semicolon_and_inactive_statuses(admin_client, db_session):
    response = submit(admin_client, "Contact;Preference\na@example.com;bounced\nb@example.com;unconfirmed\n",
                      email_column="Contact", status_column="Preference", dry_run=False)
    assert response.status_code == 200
    assert response.json()["counts"] == {"create_unsubscribed": 2}
    assert not any(s.is_active for s in db_session.query(NewsletterSubscriber).all())


@pytest.mark.parametrize("csv", [
    "email,email\na@example.com,a@example.com\n",
    "email,status\n",
    "email,status\n\"unclosed",
    "contact\na@example.com\n",
])
def test_malformed_file_is_rejected(admin_client, db_session, csv):
    assert submit(admin_client, csv, dry_run=False).status_code == 400
    assert db_session.query(NewsletterSubscriber).count() == 0


def test_preview_rechecks_database_on_apply(admin_client, db_session):
    csv = "email\na@example.com\n"
    assert submit(admin_client, csv).json()["counts"] == {"create_active": 1}
    db_session.add(NewsletterSubscriber(email="a@example.com", is_active=False))
    db_session.commit()
    response = submit(admin_client, csv, dry_run=False, confirm_subscribed=True, consent_note="opted in")
    assert response.json()["counts"] == {"protected": 1}


def test_admin_authentication_required(client):
    assert submit(client, "email\na@example.com\n").status_code in (401, 403)


def test_row_limit_and_truncated_preview(admin_client):
    csv = "email\n" + "\n".join(f"person{i}@example.com" for i in range(201))
    result = submit(admin_client, csv).json()
    assert result["total_rows"] == 201
    assert len(result["rows"]) == 200
    assert result["rows_truncated"] is True
    assert submit(admin_client, "email\n" + "a@example.com\n" * 10001).status_code == 400


def test_export_and_details_include_provenance(admin_client, db_session):
    submit(admin_client, "email,name\na@example.com,=FORMULA()\n", dry_run=False,
           confirm_subscribed=True, consent_note="Form opt-in")
    subscriber = db_session.query(NewsletterSubscriber).one()
    detail = admin_client.get(f"/api/admin/newsletter/subscribers/{subscriber.id}")
    assert detail.json()["source"] == "Google Form September"
    csv = admin_client.get("/api/admin/newsletter/subscribers/export").text
    assert "consent_note" in csv
    assert "'=FORMULA()" in csv


def test_public_signup_and_unsubscribe_find_imported_case_variants(client, db_session, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "RECAPTCHA_ENABLED", False)
    monkeypatch.setattr(NewsletterService, "remove_subscriber_from_mailerlite", AsyncMock(return_value=False))
    db_session.add(NewsletterSubscriber(email="person@example.com", is_active=True, source="import"))
    db_session.commit()
    response = client.post("/api/newsletter/subscribe", json={"email": "PERSON@EXAMPLE.COM"})
    assert response.status_code == 200
    assert response.json()["message"] == "Email already subscribed"
    assert db_session.query(NewsletterSubscriber).count() == 1
    response = client.post("/api/newsletter/unsubscribe", json={"email": "PERSON@EXAMPLE.COM"})
    assert response.status_code == 200
    assert db_session.query(NewsletterSubscriber).one().is_active is False
