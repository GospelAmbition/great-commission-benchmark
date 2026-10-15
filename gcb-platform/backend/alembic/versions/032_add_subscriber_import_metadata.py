"""Record subscriber import provenance.

Revision ID: 032
Revises: 031
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "032"
down_revision = "031"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("newsletter_subscribers", sa.Column("name", sa.String(255), nullable=True))
    # Existing records predate source tracking; do not invent consent evidence.
    op.add_column("newsletter_subscribers", sa.Column("source", sa.String(120), nullable=False, server_default="legacy_platform"))
    op.alter_column("newsletter_subscribers", "source", server_default="website")
    op.add_column("newsletter_subscribers", sa.Column("consent_note", sa.String(1000), nullable=True))
    op.add_column("newsletter_subscribers", sa.Column("imported_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("newsletter_subscribers", sa.Column("import_batch_id", postgresql.UUID(as_uuid=True), nullable=True))


def downgrade():
    for column in ("import_batch_id", "imported_at", "consent_note", "source", "name"):
        op.drop_column("newsletter_subscribers", column)
