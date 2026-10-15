"""Apply authenticated opt-outs without calling the provider during delivery."""
import hashlib
import json
from datetime import datetime, timedelta, timezone

from email_validator import validate_email, EmailNotValidError
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.db.models.action_log import ActionLog
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.db.models.newsletter_webhook_event import NewsletterWebhookEvent
from app.db.models.newsletter_campaign_send import NewsletterCampaignSend
from app.services.newsletter_sync import queue_sync

SUPPRESSION_EVENTS = {
    "subscriber.unsubscribed": "unsubscribed",
    "subscriber.bounced": "bounced",
    "subscriber.spam_reported": "junk",
    "subscriber.deleted": "deleted",
}


def event_time(data):
    value = data.get("updated_at") or data.get("unsubscribed_at")
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
    except ValueError:
        return None


def apply_webhook(db, payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected a webhook object")
    events = payload.get("events", [payload])
    if not isinstance(events, list) or not events or len(events) > 100:
        raise ValueError("Expected 1 to 100 webhook events")
    # Validate the complete delivery before writing any receipts.
    validated = []
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Invalid webhook event")
        kind = event.get("event") or event.get("type")
        if not isinstance(kind, str) or not kind or len(kind) > 80:
            raise ValueError("Missing webhook event type")
        data = event.get("subscriber", event)
        email = None
        if kind in SUPPRESSION_EVENTS:
            if not isinstance(data, dict) or not isinstance(data.get("email"), str) or not data.get("id"):
                raise ValueError("Subscriber event is missing identity")
            try:
                email = validate_email(data["email"].strip(), check_deliverability=False).normalized.lower()
            except EmailNotValidError as exc:
                raise ValueError("Subscriber event has an invalid email") from exc
            if len(str(data["id"])) > 255:
                raise ValueError("Invalid subscriber ID")
        elif kind == "campaign.sent" and (not isinstance(data, dict) or not data.get("id")):
            raise ValueError("Campaign event is missing identity")
        fingerprint = hashlib.sha256(json.dumps(event, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        validated.append((kind, data, email, fingerprint))

    applied = duplicates = ignored = 0
    now = datetime.now(timezone.utc)
    for kind, data, email, fingerprint in validated:
        try:
            with db.begin_nested():
                db.add(NewsletterWebhookEvent(fingerprint=fingerprint, event_type=kind))
                db.flush()
        except IntegrityError:
            duplicates += 1
            continue
        if kind == "campaign.sent":
            if not isinstance(data, dict) or not data.get("id"):
                raise ValueError("Campaign event is missing identity")
            updated = db.query(NewsletterCampaignSend).filter(
                NewsletterCampaignSend.provider == "mailerlite",
                NewsletterCampaignSend.campaign_id == str(data["id"]),
            ).update({"status": "sent", "error_message": None, "last_checked_at": now}, synchronize_session=False)
            applied += updated
            ignored += int(not updated)
            continue
        if kind not in SUPPRESSION_EVENTS:
            # In particular, active events must not overwrite local consent.
            ignored += 1
            continue
        subscribers = db.query(Subscriber).filter(func.lower(func.trim(Subscriber.email)) == email).with_for_update().all()
        if not subscribers:
            sub = Subscriber(email=email, source="mailerlite_webhook", is_active=False)
            db.add(sub)
            subscribers = [sub]
        timestamp = event_time(data)
        for sub in subscribers:
            confirmed = sub.resubscribe_confirmed_at
            if confirmed and confirmed.tzinfo is None:
                confirmed = confirmed.replace(tzinfo=timezone.utc)
            # A clearly earlier opt-out must not cancel a later confirmed choice.
            # Ambiguous timestamps still favor suppression.
            if confirmed and timestamp and timestamp < confirmed - timedelta(seconds=2):
                ignored += 1
                continue
            previous = sub.mailerlite_event_at
            if previous and previous.tzinfo is None:
                previous = previous.replace(tzinfo=timezone.utc)
            if previous and timestamp and timestamp < previous:
                ignored += 1
                continue
            sub.is_active = False
            sub.unsubscribed_at = sub.unsubscribed_at or now
            sub.mailerlite_subscriber_id = str(data["id"])
            sub.mailerlite_status = SUPPRESSION_EVENTS[kind]
            sub.mailerlite_event_at = timestamp or previous or now
            # Invalidate any in-flight sync. The event itself proves suppression;
            # no outbound API call is needed (and deleted records stay deleted).
            queue_sync(sub)
            sub.sync_status = "pending" if sub.sync_lease_id else "synced"
            sub.mailerlite_synced_at = now
            sub.mailerlite_group_id = None
            db.flush()
            db.add(ActionLog(action="newsletter.mailerlite_event", actor_type="system",
                             entity_type="newsletter_subscriber", entity_id=str(sub.id),
                             extra_data={"event": kind, "fingerprint": fingerprint}))
            applied += 1
    db.commit()
    return {"received": len(events), "applied": applied, "duplicates": duplicates, "ignored": ignored}
