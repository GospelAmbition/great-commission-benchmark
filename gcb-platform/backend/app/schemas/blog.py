"""Blog schemas for request/response validation"""
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# =============================================================================
# Related Model Schema (lightweight, used in blog responses)
# =============================================================================

class BlogRelatedModel(BaseModel):
    """Lightweight model info returned inside blog post responses"""
    id: UUID
    model_id: str
    name: str
    provider: str

    class Config:
        from_attributes = True


# =============================================================================
# Category Schemas
# =============================================================================

class BlogCategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class BlogCategoryCreate(BlogCategoryBase):
    """Schema for creating a category"""
    pass


class BlogCategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class BlogCategoryResponse(BlogCategoryBase):
    """Category response schema"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogCategoryListResponse(BaseModel):
    """List of categories response"""
    items: List[BlogCategoryResponse]
    total: int


# =============================================================================
# Post Schemas
# =============================================================================

class BlogPostBase(BaseModel):
    """Base post schema"""
    title: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    featured_image_url: Optional[str] = None


class BlogPostCreate(BlogPostBase):
    """Schema for creating a post"""
    category_ids: Optional[List[UUID]] = None
    model_ids: Optional[List[str]] = Field(
        None,
        description="OpenRouter model_id strings (e.g. 'openai/gpt-4o') to link to this post"
    )


class BlogPostUpdate(BaseModel):
    """Schema for updating a post"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    excerpt: Optional[str] = None
    content: Optional[str] = None
    featured_image_url: Optional[str] = None
    category_ids: Optional[List[UUID]] = None
    model_ids: Optional[List[str]] = Field(
        None,
        description="OpenRouter model_id strings to link to this post (replaces existing links)"
    )


class BlogPostAuthor(BaseModel):
    """Author info for post response"""
    id: UUID
    name: Optional[str]
    email: str

    class Config:
        from_attributes = True


class BlogPostResponse(BlogPostBase):
    """Post response schema"""
    id: UUID
    status: str
    author: BlogPostAuthor
    categories: List[BlogCategoryResponse]
    related_models: List[BlogRelatedModel] = []
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogPostListItem(BaseModel):
    """Post list item (lighter weight, no full content)"""
    id: UUID
    title: str
    slug: str
    excerpt: Optional[str] = None
    featured_image_url: Optional[str] = None
    status: str
    author: BlogPostAuthor
    categories: List[BlogCategoryResponse]
    related_models: List[BlogRelatedModel] = []
    created_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogPostListResponse(BaseModel):
    """List of posts response"""
    items: List[BlogPostListItem]
    total: int


# =============================================================================
# Image Upload Schemas
# =============================================================================

class ImageUploadResponse(BaseModel):
    """Response for image upload"""
    url: str
    filename: str
    size: int
    content_type: str

