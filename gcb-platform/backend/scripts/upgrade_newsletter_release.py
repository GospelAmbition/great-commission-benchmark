"""Apply 031→037 atomically when there are no subscriber identities to merge.

Run only after verifying a restorable database backup. Existing applications may
keep serving: the exclusive subscriber-table lock pauses their newsletter writes
for the transaction. No remote provider calls or subscriber deletions are allowed.
"""
import argparse
import os
from pathlib import Path
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.core.config import settings


def upgrade(backup_reference):
    if os.environ.get("NEWSLETTER_SYNC_ENABLED", "false").lower() in {"true", "1", "yes", "on"}:
        raise RuntimeError("Disable newsletter sync workers before this release migration")
    engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 10})
    try:
        with engine.begin() as connection:
            connection.execute(text("SET LOCAL lock_timeout = '5s'"))
            connection.execute(text("SET LOCAL statement_timeout = '60s'"))
            connection.execute(text("LOCK TABLE alembic_version, newsletter_subscribers IN ACCESS EXCLUSIVE MODE"))
            if connection.execute(text("SELECT version_num FROM alembic_version")).scalars().all() != ["031"]:
                raise RuntimeError("Expected schema 031; inspect current schema before proceeding")
            duplicates = connection.scalar(text("""SELECT count(*) FROM (
                SELECT lower(trim(email)) FROM newsletter_subscribers
                GROUP BY lower(trim(email)) HAVING count(*) > 1
            ) duplicates"""))
            if duplicates:
                raise RuntimeError("Duplicate subscriber identities exist; this guarded release will not merge or delete them")
            original = connection.execute(text("SELECT id,email,is_active,subscribed_at,unsubscribed_at FROM newsletter_subscribers ORDER BY id")).all()
            config = Config(str(ROOT / "alembic.ini"))
            config.set_main_option("script_location", str(ROOT / "alembic"))
            config.attributes["connection"] = connection
            command.upgrade(config, "037")
            after = connection.execute(text("SELECT id,email,is_active,subscribed_at,unsubscribed_at FROM newsletter_subscribers ORDER BY id")).all()
            if original != after or connection.scalar(text("SELECT count(*) FROM newsletter_subscriber_merges")):
                raise RuntimeError("Subscriber preservation check failed; rolling back all migrations")
            if connection.scalar(text("SELECT version_num FROM alembic_version")) != "037":
                raise RuntimeError("Migration revision verification failed")
        print(f"COMMITTED schema 037; preserved {len(original)} subscribers; zero merges; backup: {backup_reference}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backup-reference", required=True, help="Verified restorable backup name or ID")
    parser.add_argument("--apply", action="store_true", required=True)
    args = parser.parse_args()
    upgrade(args.backup_reference)
