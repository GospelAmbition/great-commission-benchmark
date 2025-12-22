"""Add new fields to sponsorship_requests table for model sponsorship feature

Revision ID: 008
Revises: 007
Create Date: 2025-01-20 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to sponsorship_requests table
    op.add_column('sponsorship_requests', sa.Column('openrouter_model_id', sa.String(255), nullable=True))
    op.add_column('sponsorship_requests', sa.Column('custom_model_name', sa.String(255), nullable=True))
    op.add_column('sponsorship_requests', sa.Column('request_type', sa.String(50), nullable=False, server_default='sponsorship'))
    op.add_column('sponsorship_requests', sa.Column('message', sa.Text(), nullable=True))
    op.add_column('sponsorship_requests', sa.Column('payment_id', sa.String(255), nullable=True))
    op.add_column('sponsorship_requests', sa.Column('payment_status', sa.String(50), nullable=True))
    op.add_column('sponsorship_requests', sa.Column('reviewer_id', UUID(as_uuid=True), nullable=True))
    op.add_column('sponsorship_requests', sa.Column('reviewer_notes', sa.Text(), nullable=True))
    op.add_column('sponsorship_requests', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    
    # Add foreign key for reviewer_id
    op.create_foreign_key(
        'fk_sponsorship_requests_reviewer_id',
        'sponsorship_requests',
        'users',
        ['reviewer_id'],
        ['id']
    )
    
    # Make model_id nullable (it was required before)
    op.alter_column('sponsorship_requests', 'model_id', nullable=True)
    
    # Make justification nullable (it was required before)
    op.alter_column('sponsorship_requests', 'justification', nullable=True)


def downgrade() -> None:
    # Drop foreign key first
    op.drop_constraint('fk_sponsorship_requests_reviewer_id', 'sponsorship_requests', type_='foreignkey')
    
    # Drop new columns
    op.drop_column('sponsorship_requests', 'reviewed_at')
    op.drop_column('sponsorship_requests', 'reviewer_notes')
    op.drop_column('sponsorship_requests', 'reviewer_id')
    op.drop_column('sponsorship_requests', 'payment_status')
    op.drop_column('sponsorship_requests', 'payment_id')
    op.drop_column('sponsorship_requests', 'message')
    op.drop_column('sponsorship_requests', 'request_type')
    op.drop_column('sponsorship_requests', 'custom_model_name')
    op.drop_column('sponsorship_requests', 'openrouter_model_id')
    
    # Restore model_id and justification as required
    op.alter_column('sponsorship_requests', 'model_id', nullable=False)
    op.alter_column('sponsorship_requests', 'justification', nullable=False)
