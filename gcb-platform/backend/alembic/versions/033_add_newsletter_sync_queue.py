"""Durable subscriber synchronization queue.

Revision ID: 033
Revises: 032
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "033"
down_revision = "032"
branch_labels = None
depends_on = None


def upgrade():
    for column in (
        sa.Column("sync_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("sync_revision", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("sync_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sync_error", sa.String(255)),
        sa.Column("sync_next_attempt_at", sa.DateTime(timezone=True)),
        sa.Column("sync_lease_id", postgresql.UUID(as_uuid=True)),
        sa.Column("sync_lease_until", sa.DateTime(timezone=True)),
        sa.Column("mailerlite_synced_at", sa.DateTime(timezone=True)),
        sa.Column("mailerlite_status", sa.String(30)),
        sa.Column("mailerlite_group_id", sa.String(255)),
    ):
        op.add_column("newsletter_subscribers", column)
    op.create_index("ix_newsletter_subscribers_sync_status", "newsletter_subscribers", ["sync_status"])


def downgrade():
    op.drop_index("ix_newsletter_subscribers_sync_status", table_name="newsletter_subscribers")
    for column in ("mailerlite_group_id", "mailerlite_status", "mailerlite_synced_at", "sync_lease_until", "sync_lease_id", "sync_next_attempt_at", "sync_error", "sync_attempts", "sync_revision", "sync_status"):
        op.drop_column("newsletter_subscribers", column)
