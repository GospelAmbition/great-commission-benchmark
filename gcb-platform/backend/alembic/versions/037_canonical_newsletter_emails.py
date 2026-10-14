"""Consolidate legacy case variants, archive originals, and enforce uniqueness.

Stop newsletter writers/workers before applying. Original IDs remain usable for
unsubscribe through the archive. Confirmation tokens for merged groups cancel.
Revision ID: 037
Revises: 036
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "037"
down_revision = "036"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("LOCK TABLE newsletter_subscribers IN ACCESS EXCLUSIVE MODE")
    op.execute("""DO $$ BEGIN
      IF EXISTS (SELECT 1 FROM newsletter_subscribers WHERE sync_lease_id IS NOT NULL) THEN
        RAISE EXCEPTION 'Newsletter sync leases exist. Drain worker leases and stop writers before migration 037.';
      END IF;
    END $$""")
    op.create_table("newsletter_subscriber_merges",
        sa.Column("original_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("subscriber_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("newsletter_subscribers.id"), nullable=False),
        sa.Column("original_record", postgresql.JSONB(), nullable=False),
        sa.Column("merged_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_newsletter_subscriber_merges_subscriber_id", "newsletter_subscriber_merges", ["subscriber_id"])
    op.execute("""CREATE TEMP TABLE newsletter_merge_map ON COMMIT DROP AS
      SELECT id, first_value(id) OVER (
        PARTITION BY lower(trim(email)) ORDER BY subscribed_at NULLS LAST, id
      ) AS survivor_id,
      count(*) OVER (PARTITION BY lower(trim(email))) AS copies
      FROM newsletter_subscribers""")
    op.execute("""INSERT INTO newsletter_subscriber_merges (original_id, subscriber_id, original_record)
      SELECT s.id, m.survivor_id, to_jsonb(s)
      FROM newsletter_subscribers s JOIN newsletter_merge_map m ON m.id = s.id
      WHERE m.copies > 1""")
    op.execute("""UPDATE newsletter_subscribers s SET
      is_active = merged.active,
      unsubscribed_at = CASE WHEN merged.active THEN NULL ELSE coalesce(merged.opted_out, now()) END,
      sync_status = 'pending', sync_revision = s.sync_revision + 1,
      sync_attempts = 0, sync_error = NULL, sync_next_attempt_at = NULL,
      mailerlite_subscriber_id = NULL, mailerlite_synced_at = NULL, mailerlite_group_id = NULL,
      mailerlite_status = CASE WHEN merged.deleted THEN 'deleted' ELSE NULL END,
      mailerlite_event_at = merged.event_at,
      resubscribe_nonce = NULL, resubscribe_requested_at = NULL,
      resubscribe_confirmed_at = NULL, resubscribe_pending = false
      FROM (
        SELECT m.survivor_id, bool_and(n.is_active AND coalesce(
          n.mailerlite_status NOT IN ('unsubscribed', 'unconfirmed', 'bounced', 'junk', 'deleted'), true)) AS active,
          max(n.unsubscribed_at) AS opted_out,
          bool_or(n.mailerlite_status = 'deleted') AS deleted,
          max(n.mailerlite_event_at) AS event_at
        FROM newsletter_subscribers n JOIN newsletter_merge_map m ON n.id = m.id
        WHERE m.copies > 1 GROUP BY m.survivor_id
      ) merged WHERE s.id = merged.survivor_id""")
    op.execute("""DELETE FROM newsletter_subscribers s USING newsletter_merge_map m
      WHERE s.id = m.id AND m.copies > 1 AND m.id <> m.survivor_id""")
    op.create_index("uq_newsletter_subscribers_canonical_email", "newsletter_subscribers",
                    [sa.text("lower(trim(email))")], unique=True)


def downgrade():
    raise RuntimeError("Migration 037 consolidates subscriber identities. Restore a reviewed backup for rollback; do not discard merge archives or unsubscribe aliases.")
