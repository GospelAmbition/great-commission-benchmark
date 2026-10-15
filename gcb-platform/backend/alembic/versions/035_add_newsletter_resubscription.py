"""Require email confirmation before resubscribing an opted-out address.

Revision ID: 035
Revises: 034
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "035"
down_revision = "034"
branch_labels = None
depends_on = None


def upgrade():
    for column in (
        sa.Column("resubscribe_nonce", postgresql.UUID(as_uuid=True)),
        sa.Column("resubscribe_requested_at", sa.DateTime(timezone=True)),
        sa.Column("resubscribe_confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("resubscribe_pending", sa.Boolean(), nullable=False, server_default=sa.false()),
    ):
        op.add_column("newsletter_subscribers", column)


def downgrade():
    for column in ("resubscribe_pending", "resubscribe_confirmed_at", "resubscribe_requested_at", "resubscribe_nonce"):
        op.drop_column("newsletter_subscribers", column)
