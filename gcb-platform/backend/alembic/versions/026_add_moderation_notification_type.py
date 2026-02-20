"""Add moderation notification type

Revision ID: 026
Revises: 025
Create Date: 2025-02-20

Adds 'moderation' to NotificationType enum. The INSERT is in migration 027
because PostgreSQL requires new enum values to be committed before use.
"""
from alembic import op

revision = "026"
down_revision = "025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'moderation' to the notificationtype enum (commits implicitly in PostgreSQL)
    op.execute("ALTER TYPE notificationtype ADD VALUE IF NOT EXISTS 'moderation'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing values from an enum.
    # The enum value remains but is unused.
    pass
