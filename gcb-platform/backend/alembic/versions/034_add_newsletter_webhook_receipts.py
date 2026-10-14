"""Track authenticated webhook receipts and event ordering.

Revision ID: 034
Revises: 033
"""
from alembic import op
import sqlalchemy as sa

revision = "034"
down_revision = "033"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("newsletter_subscribers", sa.Column("mailerlite_event_at", sa.DateTime(timezone=True)))
    op.create_table("newsletter_webhook_events",
                    sa.Column("fingerprint", sa.String(64), primary_key=True),
                    sa.Column("event_type", sa.String(80), nullable=False),
                    sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.create_index("ix_newsletter_webhook_events_received_at", "newsletter_webhook_events", ["received_at"])


def downgrade():
    op.drop_table("newsletter_webhook_events")
    op.drop_column("newsletter_subscribers", "mailerlite_event_at")
