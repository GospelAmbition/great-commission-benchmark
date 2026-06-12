"""Blog Post model"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import backref, relationship
import uuid

from app.db.base import Base


# Junction table for many-to-many relationship between posts and categories
blog_post_categories = Table(
    'blog_post_categories',
    Base.metadata,
    Column('post_id', UUID(as_uuid=True), ForeignKey('blog_posts.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', UUID(as_uuid=True), ForeignKey('blog_categories.id', ondelete='CASCADE'), primary_key=True)
)

# Junction table for many-to-many relationship between posts and models
blog_post_models = Table(
    'blog_post_models',
    Base.metadata,
    Column('post_id', UUID(as_uuid=True), ForeignKey('blog_posts.id', ondelete='CASCADE'), primary_key=True),
    Column('model_id', UUID(as_uuid=True), ForeignKey('models.id', ondelete='CASCADE'), primary_key=True)
)


class BlogPost(Base):
    """Blog post for Action section"""
    __tablename__ = "blog_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    featured_image_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="draft")  # 'draft', 'published'
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    author = relationship("User", backref="blog_posts")
    categories = relationship(
        "BlogCategory",
        secondary=blog_post_categories,
        back_populates="posts",
        passive_deletes=True,
    )
    models = relationship(
        "Model",
        secondary=blog_post_models,
        backref=backref("blog_posts", passive_deletes=True),
        passive_deletes=True,
    )
