"""Add tester agreement acceptance

Revision ID: 002
Revises: 001
Create Date: 2025-12-18 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tester_agreement_accepted and tester_agreement_accepted_at to users table
    op.add_column('users', sa.Column('tester_agreement_accepted', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('tester_agreement_accepted_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'tester_agreement_accepted_at')
    op.drop_column('users', 'tester_agreement_accepted')
