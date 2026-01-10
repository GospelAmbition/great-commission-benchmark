"""Add thought_process column to results table

Revision ID: 016
Revises: 015
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade():
    # Add thought_process column to results table
    op.add_column('results', sa.Column('thought_process', sa.Text(), nullable=True))


def downgrade():
    # Remove thought_process column from results table
    op.drop_column('results', 'thought_process')
