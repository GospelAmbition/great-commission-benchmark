"""Add fee waiver fields to users table

Revision ID: 004
Revises: 003
Create Date: 2025-01-20 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add fee waiver fields to users table
    op.add_column('users', sa.Column('fee_waived', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('fee_waived_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('fee_waived_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True))
    op.add_column('users', sa.Column('fee_waived_reason', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'fee_waived_reason')
    op.drop_column('users', 'fee_waived_by')
    op.drop_column('users', 'fee_waived_at')
    op.drop_column('users', 'fee_waived')

