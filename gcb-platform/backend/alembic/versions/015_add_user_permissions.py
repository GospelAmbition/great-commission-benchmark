"""Add user permission columns

Revision ID: 015
Revises: 014
Create Date: 2025-01-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '015'
down_revision = '014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add permission boolean columns with default False
    op.add_column(
        'users',
        sa.Column('can_view_benchmark', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'users',
        sa.Column('can_edit_benchmark', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'users',
        sa.Column('can_moderate', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'users',
        sa.Column('can_manage_blog', sa.Boolean(), nullable=False, server_default='false')
    )
    op.add_column(
        'users',
        sa.Column('can_admin', sa.Boolean(), nullable=False, server_default='false')
    )
    
    # Set default permissions based on existing roles
    # Note: This sets defaults, but admins should manually review and assign permissions
    op.execute("""
        UPDATE users 
        SET can_moderate = true 
        WHERE role = 'moderator'
    """)
    
    op.execute("""
        UPDATE users 
        SET can_manage_blog = true 
        WHERE role = 'blog_manager'
    """)
    
    op.execute("""
        UPDATE users 
        SET can_view_benchmark = true,
            can_edit_benchmark = true
        WHERE role = 'benchmark_developer'
    """)
    
    op.execute("""
        UPDATE users 
        SET can_admin = true 
        WHERE role = 'admin'
    """)


def downgrade() -> None:
    op.drop_column('users', 'can_admin')
    op.drop_column('users', 'can_manage_blog')
    op.drop_column('users', 'can_moderate')
    op.drop_column('users', 'can_edit_benchmark')
    op.drop_column('users', 'can_view_benchmark')
