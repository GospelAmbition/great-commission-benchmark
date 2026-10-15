"""Migration scans must be complete and preserve suppressions on either side."""
from unittest.mock import AsyncMock
import pytest
from app.core.config import settings
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.services.newsletter_sync import MailerLiteClient, MailerLiteError
from app.services.newsletter_migration import STATUSES


@pytest.fixture
def migration(client, admin_user, monkeypatch):
    from main import app
    from app.core.auth import require_admin
    app.dependency_overrides[require_admin] = lambda: admin_user
    monkeypatch.setattr(settings, "MAILERLITE_API_KEY", "test")
    monkeypatch.setattr(settings, "MAILERLITE_PROD_GROUP_ID", "prod")
    monkeypatch.setattr(settings, "MAILERLITE_TEST_GROUP_ID", "qa")
    records = {status: [{"id": str(i), "email": f"{status}@example.com", "status": status, "fields": {"name": status}}] for i, status in enumerate(STATUSES, 1)}
    async def read(method, path, **kwargs):
        assert method == "GET"
        assert path == "/groups/prod/subscribers"
        return {"data": records[kwargs["params"]["filter[status]"]], "meta": {"next_cursor": None}}
    request = AsyncMock(side_effect=read)
    monkeypatch.setattr(MailerLiteClient, "request", request)
    return client, records, request


def post(client, **kwargs):
    return client.post("/api/admin/newsletter/mailerlite/import", json=kwargs)


def test_preview_covers_every_status_without_writes(migration, db_session):
    client, records, request = migration
    response = post(client)
    assert response.status_code == 200
    assert response.json()["counts"] == {"create_active": 1, "create_unsubscribed": 4}
    assert response.json()["remote_status_counts"] == {status: 1 for status in STATUSES}
    assert request.await_count == 5
    assert db_session.query(Subscriber).count() == 0


def test_apply_preserves_remote_suppression_and_provenance(migration, db_session):
    client, records, request = migration
    preview = post(client).json()
    assert post(client, dry_run=False, snapshot_sha256=preview["snapshot_sha256"]).status_code == 400
    response = post(client, dry_run=False, snapshot_sha256=preview["snapshot_sha256"], confirm_subscribed=True, consent_note="GCB legacy signup form")
    assert response.status_code == 200
    rows = db_session.query(Subscriber).all()
    assert len(rows) == 5
    assert sum(row.is_active for row in rows) == 1
    assert all(row.source == "MailerLite group prod" and row.sync_status == "pending" for row in rows)
    again = post(client, dry_run=False, snapshot_sha256=preview["snapshot_sha256"])
    assert again.json()["counts"] == {"unchanged": 5}


def test_local_optout_after_preview_remains_protected(migration, db_session):
    client, records, request = migration
    preview = post(client).json()
    db_session.add(Subscriber(email="ACTIVE@example.com", is_active=False))
    db_session.commit()
    response = post(client, dry_run=False, snapshot_sha256=preview["snapshot_sha256"])
    assert response.json()["counts"]["protected"] == 1
    assert not any(row.is_active for row in db_session.query(Subscriber).all())


def test_remote_changes_require_new_preview(migration, db_session):
    client, records, request = migration
    preview = post(client).json()
    records["active"][0]["email"] = "different@example.com"
    assert post(client, dry_run=False, snapshot_sha256=preview["snapshot_sha256"]).status_code == 409
    assert db_session.query(Subscriber).count() == 0


def test_failure_on_later_status_saves_nothing(migration, db_session):
    client, records, request = migration
    preview = post(client).json()
    request.side_effect = [{"data": records["active"], "meta": {"next_cursor": None}}, MailerLiteError("HTTP 429")]
    assert post(client, dry_run=False, snapshot_sha256=preview["snapshot_sha256"], confirm_subscribed=True, consent_note="Opted in").status_code == 502
    assert db_session.query(Subscriber).count() == 0


def test_apply_requires_preview_before_provider_calls(migration):
    client, records, request = migration
    assert post(client, dry_run=False).status_code == 400
    assert request.await_count == 0


@pytest.mark.parametrize("response", [{"data": []}, {"data": [], "meta": {"next_cursor": 3}}, {"data": [{"id": "1", "email": "a@example.com", "status": "junk"}], "meta": {"next_cursor": None}}])
def test_malformed_pages_are_not_partial_success(migration, response):
    client, records, request = migration
    request.side_effect = None
    request.return_value = response
    assert post(client).status_code == 502


def test_pagination_is_read_and_duplicate_suppression_wins(migration):
    client, records, request = migration
    request.side_effect = [
        {"data": records["active"], "meta": {"next_cursor": "next"}},
        {"data": [{**records["active"][0], "id": "more", "email": "second@example.com"}], "meta": {"next_cursor": None}},
        {"data": [{**records["unsubscribed"][0], "email": "active@example.com"}], "meta": {"next_cursor": None}},
        *[{"data": [], "meta": {"next_cursor": None}} for _ in range(3)],
    ]
    result = post(client).json()
    assert result["counts"] == {"duplicate": 1, "create_unsubscribed": 1, "create_active": 1}
    assert request.call_args_list[1].kwargs["params"]["cursor"] == "next"


def test_repeated_cursor_fails_without_saving_partial_list(migration, db_session):
    client, records, request = migration
    request.side_effect = None
    request.return_value = {"data": records["active"], "meta": {"next_cursor": "same"}}
    assert post(client).status_code == 502
    assert request.await_count == 2
    assert db_session.query(Subscriber).count() == 0


def test_invalid_contact_cannot_silently_shrink_import(migration, db_session):
    client, records, request = migration
    records["active"][0]["email"] = "not-an-email"
    assert post(client).status_code == 400
    assert db_session.query(Subscriber).count() == 0


def test_bounded_scan_does_not_import_partial_group(migration, db_session, monkeypatch):
    client, records, request = migration
    monkeypatch.setattr("app.services.newsletter_migration.MAX_ROWS", 2)
    response = post(client)
    assert response.status_code == 400
    assert "CSV batches" in response.json()["detail"]
    assert db_session.query(Subscriber).count() == 0
