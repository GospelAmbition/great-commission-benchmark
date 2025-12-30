"""Add target_question_count to question_sets table

Revision ID: 012
Revises: 011
Create Date: 2025-01-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '012'
down_revision = '011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add optional target question count field to question_sets table
    # When set, this value is used for calculating tier/category targets
    # When NULL, targets are calculated dynamically from actual question count
    op.add_column('question_sets', sa.Column('target_question_count', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('question_sets', 'target_question_count')

