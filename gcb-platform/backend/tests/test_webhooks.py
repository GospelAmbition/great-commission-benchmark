"""Stripe webhook coverage for the current sponsorship and submission workflows."""
import hashlib
import hmac
import time
from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import settings
from app.db.models.community_submission import CommunitySubmission
from app.db.models.notification_setting import NotificationSetting, NotificationType
from app.db.models.sponsorship_request import SponsorshipRequest
from app.db.models.stripe_config import StripeConfig
from app.services.payment import EncryptionService, PaymentService


@pytest.fixture
def sponsorship(db_session, test_user):
    record = SponsorshipRequest(
        user_id=test_user.id, openrouter_model_id="provider/test-model",
        request_type="sponsorship", status="pending_payment",
        payment_id="pi_sponsorship", payment_status="pending",
    )
    db_session.add(record)
    db_session.commit()
    return record


@pytest.fixture
def submission(db_session, test_user):
    record = CommunitySubmission(
        user_id=test_user.id, model_name="Test Model", cli_version="1.0.0",
        question_set_version="1.0", results_package={},
        status="pending_payment", payment_id="pi_submission",
    )
    db_session.add(record)
    db_session.commit()
    return record


def post_event(client, event_type, event_data):
    with patch.object(PaymentService, "verify_webhook_signature", return_value={
        "type": event_type, "data": {"object": event_data},
    }):
        return client.post(
            "/api/webhooks/stripe", content=b'{"test":"payload"}',
            headers={"stripe-signature": "test_signature"},
        )


class TestStripeWebhooks:
    def test_sponsorship_payment_succeeded(self, client, db_session, sponsorship):
        response = post_event(client, "payment_intent.succeeded", {"id": sponsorship.payment_id})
        assert response.status_code == 200
        db_session.refresh(sponsorship)
        assert sponsorship.payment_status == "succeeded"
        assert sponsorship.status == "pending"

    def test_submission_payment_succeeded(self, client, db_session, submission):
        with patch("app.api.v1.endpoints.webhooks.EmailService.send_submission_payment_confirmed_email", new_callable=AsyncMock) as email:
            response = post_event(client, "payment_intent.succeeded", {
                "id": submission.payment_id, "metadata": {"type": "cli_submission"},
            })
        assert response.status_code == 200
        db_session.refresh(submission)
        assert submission.status == "pending"
        email.assert_awaited_once_with(submission.user.email, str(submission.id), submission.model_name)

    @pytest.mark.parametrize("record_name", ["sponsorship", "submission"])
    def test_payment_failed(self, client, db_session, request, record_name):
        record = request.getfixturevalue(record_name)
        response = post_event(client, "payment_intent.payment_failed", {"id": record.payment_id})
        assert response.status_code == 200
        db_session.refresh(record)
        assert record.status == "payment_failed"
        if record_name == "sponsorship":
            assert record.payment_status == "failed"

    @pytest.mark.parametrize("event_type,event_data", [
        ("payment_intent.succeeded", {"id": "pi_legacy", "metadata": {"test_id": "legacy"}}),
        ("payment_intent.payment_failed", {"id": "pi_legacy"}),
        ("charge.refunded", {"payment_intent": "pi_legacy"}),
    ])
    def test_retired_test_run_payments_do_not_mutate_runs(
        self, client, db_session, test_test_run, event_type, event_data,
    ):
        """Retired payment events must neither start nor cancel automated runs."""
        test_test_run.payment_id = "pi_legacy"
        test_test_run.payment_status = "succeeded"
        test_test_run.status = "completed"
        db_session.commit()
        response = post_event(client, event_type, event_data)
        assert response.status_code == 200
        db_session.refresh(test_test_run)
        assert test_test_run.payment_status == "succeeded"
        assert test_test_run.status == "completed"

    def test_missing_signature(self, client):
        response = client.post("/api/webhooks/stripe", content=b'{}')
        assert response.status_code == 400
        assert "Missing stripe-signature" in response.json()["detail"]

    def test_invalid_signature(self, client):
        with patch.object(PaymentService, "verify_webhook_signature", side_effect=Exception("Invalid signature")):
            response = client.post("/api/webhooks/stripe", content=b'{}', headers={"stripe-signature": "invalid"})
        assert response.status_code == 400
        assert "Invalid webhook signature" in response.json()["detail"]

    def test_unknown_event_type(self, client):
        assert post_event(client, "some.unknown.event", {}).status_code == 200

    def test_unknown_payment_does_not_update_submission(self, client, db_session, submission):
        response = post_event(client, "payment_intent.succeeded", {"id": "pi_unknown", "metadata": {}})
        assert response.status_code == 200
        db_session.refresh(submission)
        assert submission.status == "pending_payment"

    def test_uses_database_webhook_secret(self, client, db_session, test_user, monkeypatch):
        """Verify a real Stripe signature using only the admin-stored signing secret."""
        monkeypatch.setattr(settings, "NEXTAUTH_SECRET", "unit-test-encryption-secret")
        monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_wrong_environment_secret")
        monkeypatch.setattr(EncryptionService, "_fernet", None)
        secret = "whsec_database_test_secret"
        db_session.add(StripeConfig(
            secret_key_encrypted=EncryptionService.encrypt("sk_test_unit_tests"),
            webhook_secret_encrypted=EncryptionService.encrypt(secret),
            publishable_key="pk_test_unit_tests", updated_by_id=test_user.id,
        ))
        db_session.commit()
        payload = b'{"type":"some.unknown.event","data":{"object":{}}}'
        timestamp = str(int(time.time()))
        signature = hmac.new(secret.encode(), timestamp.encode() + b'.' + payload, hashlib.sha256).hexdigest()
        response = client.post("/api/webhooks/stripe", content=payload, headers={"stripe-signature": f"t={timestamp},v1={signature}"})
        assert response.status_code == 200
        invalid = client.post("/api/webhooks/stripe", content=payload + b' ', headers={"stripe-signature": f"t={timestamp},v1={signature}"})
        assert invalid.status_code == 400


class TestWebhookEmailNotifications:
    @pytest.mark.parametrize("record_name,notification_type,email_method", [
        ("sponsorship", NotificationType.SPONSORSHIP, "send_sponsorship_request_notification_email"),
        ("submission", NotificationType.MODERATION, "send_moderation_notification_email"),
    ])
    def test_success_notifies_once_and_preserves_moderation(
        self, client, db_session, request, record_name, notification_type, email_method,
    ):
        record = request.getfixturevalue(record_name)
        db_session.add(NotificationSetting(notification_type=notification_type, recipient_email="moderator@example.com", is_enabled=True))
        db_session.commit()
        event_data = {"id": record.payment_id, "metadata": {"type": "cli_submission"}}
        with patch("app.api.v1.endpoints.webhooks.EmailService") as emails:
            notify = AsyncMock()
            setattr(emails, email_method, notify)
            emails.send_submission_payment_confirmed_email = AsyncMock()
            assert post_event(client, "payment_intent.succeeded", event_data).status_code == 200
            notify.assert_awaited_once()
            assert notify.await_args.kwargs["admin_email"] == "moderator@example.com"
            # Stripe retries must not move an approved record back into the queue.
            record.status = "approved"
            db_session.commit()
            assert post_event(client, "payment_intent.succeeded", event_data).status_code == 200
            notify.assert_awaited_once()
            db_session.refresh(record)
            assert record.status == "approved"
            if record_name == "submission":
                emails.send_submission_payment_confirmed_email.assert_awaited_once()
