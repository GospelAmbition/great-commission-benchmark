"""Make judge_prompt nullable

Judge prompts are now served from code (app/services/judge.py) as the single
source of truth. The database column is kept for backward compatibility but
is no longer required.

Revision ID: 010
Revises: 009
Create Date: 2025-01-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade():
    # Make judge_prompt nullable since prompts are now served from code
    op.alter_column(
        'methodology_versions',
        'judge_prompt',
        existing_type=sa.Text(),
        nullable=True
    )


def downgrade():
    # Revert to non-nullable (would fail if any NULL values exist)
    op.alter_column(
        'methodology_versions',
        'judge_prompt',
        existing_type=sa.Text(),
        nullable=False
    )

