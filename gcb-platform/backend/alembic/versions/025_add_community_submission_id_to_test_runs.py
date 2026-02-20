"""Add community_submission_id to test_runs for reverting approved submissions

Revision ID: 025
Revises: 024
Create Date: 2025-02-19

Links TestRun to CommunitySubmission when created from an approved CLI export.
Enables reliable lookup when reverting approved -> rejected.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "025"
down_revision = "024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("community_submission_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_test_runs_community_submission_id",
        "test_runs",
        "community_submissions",
        ["community_submission_id"],
        ["id"],
    )
    op.create_index(
        "ix_test_runs_community_submission_id",
        "test_runs",
        ["community_submission_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_test_runs_community_submission_id", table_name="test_runs")
    op.drop_constraint("fk_test_runs_community_submission_id", "test_runs", type_="foreignkey")
    op.drop_column("test_runs", "community_submission_id")
