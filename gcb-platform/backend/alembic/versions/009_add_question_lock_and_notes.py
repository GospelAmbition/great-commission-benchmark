"""Add is_locked and notes columns to questions table for individual question management

Revision ID: 009
Revises: 008
Create Date: 2025-01-26 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_locked column to mark individual questions as accepted/finalized
    op.add_column('questions', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add notes column for tracking question framing history
    op.add_column('questions', sa.Column('notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('questions', 'notes')
    op.drop_column('questions', 'is_locked')

