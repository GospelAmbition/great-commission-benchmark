"""Add fee waiver and payment fields to community_submissions table

Revision ID: 005
Revises: 004
Create Date: 2025-01-20 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add fee waiver and payment tracking fields to community_submissions table
    op.add_column('community_submissions', sa.Column('fee_waived', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('community_submissions', sa.Column('payment_id', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('community_submissions', 'payment_id')
    op.drop_column('community_submissions', 'fee_waived')









