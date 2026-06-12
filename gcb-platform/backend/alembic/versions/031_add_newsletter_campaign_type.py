"""Add campaign type to newsletter send logs

Revision ID: 031
Revises: 030
Create Date: 2026-06-12
"""
from alembic import op
import sqlalchemy as sa

revision = "031"
down_revision = "030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "newsletter_campaign_sends",
        sa.Column(
            "campaign_type",
            sa.String(length=20),
            nullable=False,
            server_default="newsletter",
        ),
    )
    op.create_index(
        "ix_newsletter_campaign_sends_campaign_type",
        "newsletter_campaign_sends",
        ["campaign_type"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_newsletter_campaign_sends_campaign_type",
        table_name="newsletter_campaign_sends",
    )
    op.drop_column("newsletter_campaign_sends", "campaign_type")
