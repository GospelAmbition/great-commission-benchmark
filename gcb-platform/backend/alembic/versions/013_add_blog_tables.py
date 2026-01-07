"""Add blog tables for Action CMS

Revision ID: 013
Revises: 012
Create Date: 2025-01-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '013'
down_revision = '012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create blog_categories table
    op.create_table(
        'blog_categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_blog_categories_slug', 'blog_categories', ['slug'])

    # Create blog_posts table
    op.create_table(
        'blog_posts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('excerpt', sa.Text(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('featured_image_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('author_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_blog_posts_slug', 'blog_posts', ['slug'])
    op.create_index('ix_blog_posts_status', 'blog_posts', ['status'])
    op.create_index('ix_blog_posts_published_at', 'blog_posts', ['published_at'])

    # Create blog_post_categories junction table
    op.create_table(
        'blog_post_categories',
        sa.Column('post_id', UUID(as_uuid=True), sa.ForeignKey('blog_posts.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('category_id', UUID(as_uuid=True), sa.ForeignKey('blog_categories.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('blog_post_categories')
    op.drop_index('ix_blog_posts_published_at', 'blog_posts')
    op.drop_index('ix_blog_posts_status', 'blog_posts')
    op.drop_index('ix_blog_posts_slug', 'blog_posts')
    op.drop_table('blog_posts')
    op.drop_index('ix_blog_categories_slug', 'blog_categories')
    op.drop_table('blog_categories')

