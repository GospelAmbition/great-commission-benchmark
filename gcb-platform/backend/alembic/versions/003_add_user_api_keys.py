"""Add user API keys table

Revision ID: 003
Revises: 002
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_api_keys table
    op.create_table(
        'user_api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_prefix', sa.String(8), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_user_api_keys_user_id', 'user_api_keys', ['user_id'])
    op.create_index('ix_user_api_keys_key_prefix', 'user_api_keys', ['key_prefix'])
    op.create_index('ix_user_api_keys_key_hash', 'user_api_keys', ['key_hash'])


def downgrade() -> None:
    op.drop_index('ix_user_api_keys_key_hash', 'user_api_keys')
    op.drop_index('ix_user_api_keys_key_prefix', 'user_api_keys')
    op.drop_index('ix_user_api_keys_user_id', 'user_api_keys')
    op.drop_table('user_api_keys')
