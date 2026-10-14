"""Durable, retryable synchronization of the platform subscriber list.

Rows are claimed with a lease and revision, then committed before network I/O.
Completion uses a compare-and-set so an old response cannot undo a newer local
unsubscribe. Expired leases recover automatically after a worker restart.
"""
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from uuid import UUID, uuid4

import httpx
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.services.newsletter import NewsletterService

logger = logging.getLogger(__name__)
SUPPRESSED = {"unsubscribed", "bounced", "junk", "unconfirmed", "deleted"}
KNOWN_STATUSES = SUPPRESSED | {"active"}


class MailerLiteError(Exception):
    """Only safe, operator-readable codes belong in this exception."""
    def __init__(self, message: str, retry_after: int = 0, status_code: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.status_code = status_code


class MailerLiteClient:
    """Strict API client: missing subscribers are distinct from API failures."""
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def request(self, method, path, *, allow_missing=False, envelope=False, allow_empty=False, **kwargs):
        try:
            response = await self.client.request(
                method, f"{NewsletterService.MAILERLITE_API_BASE}{path}",
                headers=NewsletterService._get_headers(), timeout=10, **kwargs,
            )
        except httpx.HTTPError as exc:
            raise MailerLiteError("MailerLite connection failed; will retry") from exc
        if response.status_code == 404 and allow_missing:
            return None
        if not 200 <= response.status_code < 300:
            try:
                retry_after = max(0, min(86400, int(response.headers.get("Retry-After", "0"))))
            except ValueError:
                retry_after = 0
            raise MailerLiteError(f"MailerLite returned HTTP {response.status_code}", retry_after, response.status_code)
        if allow_empty and not response.content:
            return None
        try:
            data = response.json()
            if not isinstance(data, dict) or "data" not in data:
                raise ValueError("Missing data")
            return data if envelope else data["data"]
        except (ValueError, TypeError) as exc:
            raise MailerLiteError("MailerLite returned an invalid response") from exc

    async def subscriber(self, email):
        data = await self.request("GET", f"/subscribers/{quote(email, safe='')}", allow_missing=True)
        if data is not None and (not isinstance(data, dict) or not data.get("id") or data.get("status") not in KNOWN_STATUSES):
            raise MailerLiteError("MailerLite returned invalid subscriber data")
        return data

    async def synchronize(self, claim):
        remote = await self.subscriber(claim.email)
        # Remote suppression always wins over a routine active upsert.
        explicit_resubscribe = getattr(claim, "resubscribe", False) and remote and remote["status"] == "unsubscribed"
        if claim.active and remote and remote["status"] in SUPPRESSED and not explicit_resubscribe:
            return remote
        if claim.active:
            payload = {"email": claim.email, "groups": [claim.group_id]}
            if claim.name:
                payload["fields"] = {"name": claim.name}
            if explicit_resubscribe:
                payload.update(status="active", resubscribe=True)
            # Routine sync omits these flags; only a confirmed request may resubscribe.
            await self.request("POST", "/subscribers", json=payload)
        elif remote is None:
            if getattr(claim, "remote_status", None) == "deleted":
                return {"id": claim.remote_id, "status": "deleted"}
            await self.request("POST", "/subscribers", json={"email": claim.email, "status": "unsubscribed"})
        elif remote["status"] == "active":
            await self.request("PUT", f"/subscribers/{quote(str(remote['id']), safe='')}", json={"status": "unsubscribed"})

        verified = await self.subscriber(claim.email)
        if verified is None:
            raise MailerLiteError("Subscriber was not found after sync")
        if not claim.active and verified["status"] not in SUPPRESSED:
            raise MailerLiteError("MailerLite unsubscribe has not been verified")
        if claim.active and verified["status"] == "active":
            groups = verified.get("groups", [])
            if not isinstance(groups, list) or not any(isinstance(g, dict) and str(g.get("id")) == claim.group_id for g in groups):
                raise MailerLiteError("Production group membership has not been verified")
        return verified


@dataclass
class SyncClaim:
    id: UUID
    revision: int
    lease: UUID
    email: str
    name: str | None
    active: bool
    group_id: str
    attempts: int
    remote_status: str | None = None
    remote_id: str | None = None
    resubscribe: bool = False


def queue_sync(subscriber: Subscriber, *, resubscribe=False, cancel_confirmation=True):
    """Queue the latest desired state within the caller's transaction."""
    subscriber.sync_status = "pending"
    subscriber.sync_revision = Subscriber.sync_revision + 1 if subscriber.id else 1
    subscriber.sync_attempts = 0
    subscriber.sync_error = None
    subscriber.sync_next_attempt_at = None
    # Preserve a live lease: a newer opt-out must run after any older provider
    # mutation, especially an explicitly confirmed resubscription.
    subscriber.resubscribe_pending = resubscribe
    if cancel_confirmation:
        subscriber.resubscribe_nonce = None


def _claim(db: Session, subscriber_id=None):
    now = datetime.now(timezone.utc)
    query = db.query(Subscriber).filter(
        or_(
            and_(Subscriber.sync_status.in_(["pending", "error"]),
                 or_(Subscriber.sync_lease_id.is_(None), Subscriber.sync_lease_until <= now),
                 or_(Subscriber.sync_next_attempt_at.is_(None), Subscriber.sync_next_attempt_at <= now)),
            and_(Subscriber.sync_status == "processing", Subscriber.sync_lease_until <= now),
            and_(Subscriber.sync_status == "synced",
                 or_(Subscriber.mailerlite_synced_at.is_(None),
                     Subscriber.mailerlite_synced_at <= now - timedelta(hours=1))),
        )
    )
    if subscriber_id:
        query = query.filter(Subscriber.id == subscriber_id)
    # Prioritize opt-outs. Multiple backend replicas may claim different rows.
    sub = query.order_by(Subscriber.is_active, Subscriber.sync_next_attempt_at, Subscriber.id).with_for_update(skip_locked=True).first()
    if sub is None:
        db.rollback()
        return None
    lease = uuid4()
    sub.sync_status = "processing"
    sub.sync_lease_id = lease
    sub.sync_lease_until = now + timedelta(minutes=5)
    sub.sync_attempts += 1
    claim = SyncClaim(sub.id, sub.sync_revision, lease, sub.email, sub.name, sub.is_active or sub.resubscribe_pending,
                      NewsletterService.production_group_id(), sub.sync_attempts,
                      sub.mailerlite_status, sub.mailerlite_subscriber_id, sub.resubscribe_pending)
    db.commit()
    return claim


async def sync_one(db: Session, subscriber_id=None, api=None):
    if not NewsletterService.is_configured() or not NewsletterService.production_group_id():
        return {"status": "not_configured"}
    claim = _claim(db, subscriber_id)
    if claim is None:
        return {"status": "idle"}
    now = datetime.now(timezone.utc)
    try:
        if api is None:
            async with httpx.AsyncClient() as client:
                remote = await MailerLiteClient(client).synchronize(claim)
        else:
            remote = await api.synchronize(claim)
        values = dict(sync_status="synced", sync_error=None, sync_next_attempt_at=None,
                      sync_lease_id=None, sync_lease_until=None, mailerlite_synced_at=now,
                      mailerlite_subscriber_id=str(remote["id"]), mailerlite_status=remote["status"],
                      mailerlite_group_id=claim.group_id if remote["status"] == "active" else None)
        if claim.resubscribe:
            values["resubscribe_pending"] = False
            if remote["status"] == "active":
                values.update(is_active=True, unsubscribed_at=None)
        if remote["status"] in SUPPRESSED:
            values.update(is_active=False)
            from sqlalchemy import func
            values["unsubscribed_at"] = func.coalesce(Subscriber.unsubscribed_at, now)
    except MailerLiteError as exc:
        delay = max(min(3600, 30 * 2 ** min(claim.attempts - 1, 7)), exc.retry_after)
        values = dict(sync_status="error", sync_error=str(exc), sync_next_attempt_at=now + timedelta(seconds=delay),
                      sync_lease_id=None, sync_lease_until=None)
    changed = db.query(Subscriber).filter(
        Subscriber.id == claim.id, Subscriber.sync_revision == claim.revision,
        Subscriber.sync_lease_id == claim.lease,
    ).update(values, synchronize_session=False)
    if not changed:
        db.query(Subscriber).filter(Subscriber.id == claim.id, Subscriber.sync_lease_id == claim.lease).update({
            Subscriber.sync_status: "pending", Subscriber.sync_lease_id: None,
            Subscriber.sync_lease_until: None, Subscriber.sync_next_attempt_at: None,
        }, synchronize_session=False)
        # The stale request may still have changed the provider after a webhook
        # marked the latest state verified. Recheck it instead of trusting that
        # earlier verification; leave any newer in-flight worker alone.
        db.query(Subscriber).filter(Subscriber.id == claim.id, Subscriber.sync_status == "synced").update({
            Subscriber.sync_status: "pending",
            Subscriber.sync_revision: Subscriber.sync_revision + 1,
            Subscriber.sync_next_attempt_at: None,
        }, synchronize_session=False)
    db.commit()
    db.expire_all()
    return {"status": values["sync_status"] if changed else "superseded", "subscriber_id": str(claim.id)}


async def sync_worker():
    """Automatic retries, backed by database state rather than in-memory jobs."""
    from app.db.base import SessionLocal
    while True:
        try:
            for _ in range(10):
                with SessionLocal() as db:
                    result = await sync_one(db)
                if result["status"] in ("idle", "not_configured"):
                    break
        except asyncio.CancelledError:
            raise
        except Exception:
            # Do not log provider payloads or credentials. Lease expiry recovers
            # any interrupted attempt; other queued rows remain durable.
            logger.error("Newsletter sync worker failed; queued work will retry")
        await asyncio.sleep(settings.NEWSLETTER_SYNC_INTERVAL_SECONDS)
