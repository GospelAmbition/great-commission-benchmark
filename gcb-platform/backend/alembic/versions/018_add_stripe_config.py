"""Add stripe_config table for storing encrypted Stripe credentials

Revision ID: 018
Revises: 017
Create Date: 2025-01-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None


def upgrade():
    # Create stripe_config table for storing encrypted Stripe API credentials
    op.create_table(
        'stripe_config',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        
        # Encrypted sensitive fields
        sa.Column('secret_key_encrypted', sa.Text, nullable=False),
        sa.Column('webhook_secret_encrypted', sa.Text, nullable=True),
        
        # Public key (safe unencrypted)
        sa.Column('publishable_key', sa.String(255), nullable=False),
        
        # Configuration metadata
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('is_live_mode', sa.Boolean, default=False, nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        
        # Audit fields
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
    )
    
    # Index on is_active for quick lookup of active config
    op.create_index('ix_stripe_config_is_active', 'stripe_config', ['is_active'])


def downgrade():
    op.drop_index('ix_stripe_config_is_active', table_name='stripe_config')
    op.drop_table('stripe_config')
