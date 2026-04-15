"""Add blog_post_models junction table for cross-referencing articles and models

Revision ID: 029
Revises: 028
Create Date: 2026-04-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "029"
down_revision = "028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blog_post_models",
        sa.Column("post_id", UUID(as_uuid=True), sa.ForeignKey("blog_posts.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("model_id", UUID(as_uuid=True), sa.ForeignKey("models.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_index("ix_blog_post_models_model_id", "blog_post_models", ["model_id"])


def downgrade() -> None:
    op.drop_index("ix_blog_post_models_model_id", table_name="blog_post_models")
    op.drop_table("blog_post_models")
