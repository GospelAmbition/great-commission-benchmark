"""Add metadata column to questions table

Revision ID: 006
Revises: 005
Create Date: 2025-12-19 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add question_metadata JSONB column to questions table
    op.add_column('questions', sa.Column('question_metadata', JSONB(), nullable=True))


def downgrade() -> None:
    op.drop_column('questions', 'question_metadata')
