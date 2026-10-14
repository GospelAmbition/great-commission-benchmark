"""Integration checks against an EMPTY disposable local PostgreSQL database.

GCB_NEWSLETTER_TEST_DATABASE_URL must point to localhost and a database named
gcb_newsletter_test*. This script applies migrations and creates synthetic data.
Never uses the application's configured DATABASE_URL or contacts MailerLite.
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
import sys
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
url = os.environ.get("GCB_NEWSLETTER_TEST_DATABASE_URL", "")
parsed = make_url(url)
if parsed.host not in {"localhost", "127.0.0.1", "::1"} or not (parsed.database or "").startswith("gcb_newsletter_test"):
    raise SystemExit("Use an empty disposable localhost database named gcb_newsletter_test*")
engine = create_engine(url)
with engine.connect() as conn:
    assert conn.scalar(text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")) == 0, "Database must be empty"


def migrate(revision, expect_failure=False):
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", revision], cwd=ROOT,
                            env={**os.environ, "DATABASE_URL": url}, capture_output=True, text=True)
    if expect_failure:
        assert result.returncode != 0 and "Drain worker leases" in result.stderr
    elif result.returncode:
        raise AssertionError(result.stderr)


migrate("036")
ids = [uuid4() for _ in range(5)]
with engine.begin() as conn:
    for i, (email, active, source) in enumerate([
        ("Person@example.com", True, "old signup"),
        (" person@EXAMPLE.com ", False, "legacy suppression"),
        ("second@example.com", True, "first import"),
        ("SECOND@example.com", True, "later import"),
        ("single@example.com", True, "single signup"),
    ]):
        conn.execute(text("""INSERT INTO newsletter_subscribers
          (id, email, is_active, source, subscribed_at, unsubscribed_at, resubscribe_nonce)
          VALUES (:id, :email, :active, :source, :time,
            CASE WHEN :active THEN NULL ELSE now() END, :nonce)"""),
          {"id": ids[i], "email": email, "active": active, "source": source,
           "time": f"2026-01-0{i + 1}T00:00:00Z", "nonce": uuid4()})
    conn.execute(text("UPDATE newsletter_subscribers SET sync_lease_id = :lease WHERE id = :id"), {"lease": uuid4(), "id": ids[4]})
migrate("037", expect_failure=True)
with engine.begin() as conn:
    assert conn.scalar(text("SELECT version_num FROM alembic_version")) == "036"
    assert conn.scalar(text("SELECT count(*) FROM newsletter_subscribers")) == 5
    conn.execute(text("UPDATE newsletter_subscribers SET sync_lease_id = NULL"))
migrate("head")
with engine.connect() as conn:
    assert conn.scalar(text("SELECT count(*) FROM newsletter_subscribers")) == 3
    assert conn.scalar(text("SELECT count(*) FROM newsletter_subscriber_merges")) == 4
    rows = {row.id: row for row in conn.execute(text("SELECT * FROM newsletter_subscribers"))}
    assert rows[ids[0]].is_active is False
    assert rows[ids[0]].unsubscribed_at is not None
    assert rows[ids[0]].sync_status == "pending"
    assert rows[ids[0]].resubscribe_nonce is None
    assert rows[ids[2]].is_active is True
    assert rows[ids[2]].resubscribe_nonce is None
    assert rows[ids[4]].resubscribe_nonce is not None  # unrelated row stays intact
    archive = conn.execute(text("SELECT * FROM newsletter_subscriber_merges WHERE original_id = :id"), {"id": ids[1]}).one()
    assert archive.subscriber_id == ids[0]
    assert archive.original_record["source"] == "legacy suppression"
    assert archive.original_record["is_active"] is False
    assert archive.original_record["resubscribe_nonce"] is not None
try:
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO newsletter_subscribers (id,email,is_active) VALUES (:id,' PERSON@example.COM ',true)"), {"id": uuid4()})
except IntegrityError:
    pass
else:
    raise AssertionError("Canonical uniqueness was not enforced")

# Exercise real PostgreSQL SKIP LOCKED and claim exclusivity with separate sessions.
from app.db.models.newsletter_subscriber import NewsletterSubscriber as Subscriber
from app.services.newsletter_sync import _claim, queue_sync, sync_one
from app.core.config import settings
settings.MAILERLITE_API_KEY = "synthetic-test-key"
settings.MAILERLITE_PROD_GROUP_ID = "test-group"
Session = sessionmaker(bind=engine)
with Session() as locked, Session() as other:
    locked.query(Subscriber).filter(Subscriber.id == ids[4]).with_for_update().one()
    assert _claim(other, ids[4]) is None
    locked.rollback()
barrier = Barrier(2)


def claim_once():
    with Session() as db:
        barrier.wait(timeout=5)
        return _claim(db, ids[4])


with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(claim_once) for _ in range(2)]
    assert sum(f.result() is not None for f in futures) == 1


async def stale_result():
    with Session() as db:
        async def provider(claim):
            with Session() as newer:
                row = newer.get(Subscriber, ids[2])
                row.is_active = False
                queue_sync(row)
                newer.commit()
            return {"id": "fake", "status": "active", "groups": [{"id": "test-group"}]}
        result = await sync_one(db, ids[2], SimpleNamespace(synchronize=provider))
        assert result["status"] == "superseded"
        db.expire_all()
        row = db.get(Subscriber, ids[2])
        assert row.is_active is False and row.sync_status == "pending"


asyncio.run(stale_result())
engine.dispose()
print("PASS: migrations 001–037, lease guard, archives, suppression merge, canonical uniqueness, SKIP LOCKED, concurrent claims and stale-result protection")
