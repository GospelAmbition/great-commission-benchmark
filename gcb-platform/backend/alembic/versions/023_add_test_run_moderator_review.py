"""Add moderator review fields to test_runs for automated (bulk) runs

Revision ID: 023
Revises: 022
Create Date: 2025-02-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("moderator_reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("moderator_id", UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("moderator_decision", sa.String(20), nullable=True),
    )
    op.create_foreign_key(
        "fk_test_runs_moderator_id_users",
        "test_runs",
        "users",
        ["moderator_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_test_runs_moderator_id_users",
        "test_runs",
        type_="foreignkey",
    )
    op.drop_column("test_runs", "moderator_decision")
    op.drop_column("test_runs", "moderator_id")
    op.drop_column("test_runs", "moderator_reviewed_at")
