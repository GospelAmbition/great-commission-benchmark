"""Add newsletter test recipients and campaign send logs

Revision ID: 030
Revises: 029
Create Date: 2026-04-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "030"
down_revision = "029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "newsletter_test_recipients",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("mailerlite_subscriber_id", sa.String(length=255), nullable=True),
        sa.Column("created_by_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_newsletter_test_recipients_email", "newsletter_test_recipients", ["email"])
    op.create_index("ix_newsletter_test_recipients_is_active", "newsletter_test_recipients", ["is_active"])

    op.create_table(
        "newsletter_campaign_sends",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("post_id", UUID(as_uuid=True), sa.ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("audience", sa.String(length=20), nullable=False),
        sa.Column("campaign_id", sa.String(length=255), nullable=True),
        sa.Column("recipient_count", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="sent"),
        sa.Column("provider", sa.String(length=50), nullable=False, server_default="mailerlite"),
        sa.Column("sent_by_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_newsletter_campaign_sends_post_id", "newsletter_campaign_sends", ["post_id"])
    op.create_index("ix_newsletter_campaign_sends_audience", "newsletter_campaign_sends", ["audience"])
    op.create_index("ix_newsletter_campaign_sends_status", "newsletter_campaign_sends", ["status"])
    op.create_index("ix_newsletter_campaign_sends_created_at", "newsletter_campaign_sends", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_newsletter_campaign_sends_created_at", table_name="newsletter_campaign_sends")
    op.drop_index("ix_newsletter_campaign_sends_status", table_name="newsletter_campaign_sends")
    op.drop_index("ix_newsletter_campaign_sends_audience", table_name="newsletter_campaign_sends")
    op.drop_index("ix_newsletter_campaign_sends_post_id", table_name="newsletter_campaign_sends")
    op.drop_table("newsletter_campaign_sends")

    op.drop_index("ix_newsletter_test_recipients_is_active", table_name="newsletter_test_recipients")
    op.drop_index("ix_newsletter_test_recipients_email", table_name="newsletter_test_recipients")
    op.drop_table("newsletter_test_recipients")
