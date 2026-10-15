"""Record MailerLite campaign routing and safe failure diagnostics.

Revision ID: 036
Revises: 035
"""
from alembic import op
import sqlalchemy as sa

revision = "036"
down_revision = "035"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("newsletter_campaign_sends", sa.Column("error_message", sa.String(255)))
    op.add_column("newsletter_campaign_sends", sa.Column("target_group_id", sa.String(255)))
    op.add_column("newsletter_campaign_sends", sa.Column("last_checked_at", sa.DateTime(timezone=True)))


def downgrade():
    for column in ("last_checked_at", "target_group_id", "error_message"):
        op.drop_column("newsletter_campaign_sends", column)
