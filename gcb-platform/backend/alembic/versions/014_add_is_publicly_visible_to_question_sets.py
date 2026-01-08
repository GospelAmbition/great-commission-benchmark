"""Add is_publicly_visible to question_sets

Revision ID: 014
Revises: 013
Create Date: 2025-01-08

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '014'
down_revision = '013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_publicly_visible column with default False
    op.add_column(
        'question_sets',
        sa.Column('is_publicly_visible', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Set is_publicly_visible=True for active versions (they should always be visible)
    op.execute("""
        UPDATE question_sets 
        SET is_publicly_visible = true 
        WHERE status = 'active'
    """)
    
    # Archived versions remain False (hidden by default per new behavior)
    # Draft versions remain False (not publicly visible anyway)


def downgrade() -> None:
    op.drop_column('question_sets', 'is_publicly_visible')
