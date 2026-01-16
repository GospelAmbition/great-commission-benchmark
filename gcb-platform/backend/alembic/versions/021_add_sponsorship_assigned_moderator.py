"""Add assigned_moderator_id and assigned_at to sponsorship_requests table

Revision ID: 021
Revises: 020
Create Date: 2025-01-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '021'
down_revision = '020'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add assigned_moderator_id column
    op.add_column(
        'sponsorship_requests',
        sa.Column('assigned_moderator_id', UUID(as_uuid=True), nullable=True)
    )
    # Add assigned_at column
    op.add_column(
        'sponsorship_requests',
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True)
    )
    
    # Add foreign key for assigned_moderator_id
    op.create_foreign_key(
        'fk_sponsorship_requests_assigned_moderator_id',
        'sponsorship_requests',
        'users',
        ['assigned_moderator_id'],
        ['id']
    )


def downgrade() -> None:
    # Drop foreign key first
    op.drop_constraint(
        'fk_sponsorship_requests_assigned_moderator_id',
        'sponsorship_requests',
        type_='foreignkey'
    )
    
    # Drop columns
    op.drop_column('sponsorship_requests', 'assigned_at')
    op.drop_column('sponsorship_requests', 'assigned_moderator_id')
