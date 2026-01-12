"""Add description column to models table

Revision ID: 019
Revises: 018
Create Date: 2025-01-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade():
    # Add description column to models table
    op.add_column('models', sa.Column('description', sa.Text, nullable=True))


def downgrade():
    op.drop_column('models', 'description')
