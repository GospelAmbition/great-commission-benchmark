"""Add pre-computed score columns to test_runs

Revision ID: 024
Revises: 023
Create Date: 2025-02-19 00:00:00.000000

Scores are computed once when a test completes and stored for fast reads.
Visitor-facing endpoints exclude test runs with null overall_score.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "024"
down_revision = "023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "test_runs",
        sa.Column("overall_score", sa.Numeric(6, 2), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("tier1_score", sa.Numeric(6, 2), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("tier2_score", sa.Numeric(6, 2), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("tier3_score", sa.Numeric(6, 2), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("category_scores", JSONB(), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("verdict_distribution", JSONB(), nullable=True),
    )
    op.add_column(
        "test_runs",
        sa.Column("total_questions", sa.Integer, nullable=True),
    )
    op.create_index(
        "ix_test_runs_overall_score",
        "test_runs",
        ["overall_score"],
    )


def downgrade() -> None:
    op.drop_index("ix_test_runs_overall_score", table_name="test_runs")
    op.drop_column("test_runs", "total_questions")
    op.drop_column("test_runs", "verdict_distribution")
    op.drop_column("test_runs", "category_scores")
    op.drop_column("test_runs", "tier3_score")
    op.drop_column("test_runs", "tier2_score")
    op.drop_column("test_runs", "tier1_score")
    op.drop_column("test_runs", "overall_score")
