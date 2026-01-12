"""Add is_active and mailerlite_subscriber_id to newsletter_subscribers

Revision ID: 020
Revises: 019
Create Date: 2025-01-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None


def upgrade():
    # Add is_active column with default True
    op.add_column(
        'newsletter_subscribers',
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('true'))
    )
    # Add mailerlite_subscriber_id column
    op.add_column(
        'newsletter_subscribers',
        sa.Column('mailerlite_subscriber_id', sa.String(255), nullable=True)
    )


def downgrade():
    op.drop_column('newsletter_subscribers', 'mailerlite_subscriber_id')
    op.drop_column('newsletter_subscribers', 'is_active')
