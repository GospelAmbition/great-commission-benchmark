"""Runner Blog API endpoints - API key authenticated blog management for CLI/scripts"""
from typing import Optional, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, Header, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from uuid import UUID
from datetime import datetime
import re

from app.core.auth import get_db, has_permission
from app.core.rate_limit import RateLimitDependency
from app.db.models.user import User
from app.db.models.blog_post import BlogPost
from app.db.models.blog_category import BlogCategory
from app.db.models.user_api_key import UserAPIKey
from app.api.v1.endpoints.api_keys import validate_api_key
from app.schemas.blog import (
    BlogCategoryCreate,
    BlogCategoryResponse,
    BlogCategoryListResponse,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostResponse,
    BlogPostListItem,
    BlogPostListResponse,
    BlogPostAuthor,
    ImageUploadResponse,
)
from app.services.storage import upload_image

router = APIRouter()

# Rate limiter for blog endpoints: reuse runner rate limit pattern
blog_rate_limit = RateLimitDependency("runner")


class BlogAPIKeyAuth:
    """Dependency for API key authentication that requires can_manage_blog permission"""
    
    async def __call__(
        self,
        x_api_key: Optional[str] = Header(None),
        db: Session = Depends(get_db)
    ) -> Tuple[UserAPIKey, User]:
        """Validate API key and check blog management permission"""
        if not x_api_key:
            raise HTTPException(
                status_code=401,
                detail="API key required. Get one from your dashboard at https://greatcommissionbenchmark.ai/dashboard/settings"
            )
        
        api_key_record, user = validate_api_key(db, x_api_key)
        
        if not api_key_record or not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired API key"
            )
        
        # Check blog management permission
        if not has_permission(user, "can_manage_blog"):
            raise HTTPException(
                status_code=403,
                detail="Blog management permission required. Contact an administrator to request access."
            )
        
        return api_key_record, user


# Dependency instance
require_blog_api_key = BlogAPIKeyAuth()


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def _build_post_response(post: BlogPost, user: User) -> BlogPostResponse:
    """Helper to build BlogPostResponse from a post"""
    return BlogPostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        excerpt=post.excerpt,
        content=post.content,
        featured_image_url=post.featured_image_url,
        status=post.status,
        author=BlogPostAuthor(
            id=post.author.id,
            name=post.author.name,
            email=post.author.email
        ),
        categories=[BlogCategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        ) for cat in post.categories],
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at
    )


def _build_post_list_item(post: BlogPost) -> BlogPostListItem:
    """Helper to build BlogPostListItem from a post"""
    return BlogPostListItem(
        id=post.id,
        title=post.title,
        slug=post.slug,
        excerpt=post.excerpt,
        featured_image_url=post.featured_image_url,
        status=post.status,
        author=BlogPostAuthor(
            id=post.author.id,
            name=post.author.name,
            email=post.author.email
        ),
        categories=[BlogCategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        ) for cat in post.categories],
        created_at=post.created_at,
        published_at=post.published_at
    )


# =============================================================================
# Post Endpoints
# =============================================================================

@router.get("/posts", response_model=BlogPostListResponse)
async def list_posts(
    status: Optional[str] = Query(None, description="Filter by status (draft, published)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    List all blog posts (including drafts).
    
    Requires API key with blog management permission.
    """
    query = db.query(BlogPost).options(
        joinedload(BlogPost.author),
        joinedload(BlogPost.categories)
    )
    
    if status:
        query = query.filter(BlogPost.status == status)
    
    # Order by updated date, most recent first
    query = query.order_by(desc(BlogPost.updated_at))
    
    # Get total count
    count_query = db.query(BlogPost)
    if status:
        count_query = count_query.filter(BlogPost.status == status)
    total = count_query.count()
    
    posts = query.offset(offset).limit(limit).all()
    
    return BlogPostListResponse(
        items=[_build_post_list_item(post) for post in posts],
        total=total
    )


@router.post("/posts", response_model=BlogPostResponse)
async def create_post(
    request: BlogPostCreate,
    publish: bool = Query(False, description="Publish immediately instead of creating as draft"),
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Create a new blog post.
    
    By default creates as draft. Set publish=true to publish immediately.
    Requires API key with blog management permission.
    """
    api_key_record, user = auth
    
    # Check if slug already exists
    existing = db.query(BlogPost).filter(BlogPost.slug == request.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="A post with this slug already exists")
    
    # Determine status and published_at
    status = "published" if publish else "draft"
    published_at = datetime.utcnow() if publish else None
    
    # Create post
    post = BlogPost(
        title=request.title,
        slug=request.slug,
        excerpt=request.excerpt,
        content=request.content,
        featured_image_url=request.featured_image_url,
        status=status,
        published_at=published_at,
        author_id=user.id
    )
    
    # Add categories if provided
    if request.category_ids:
        categories = db.query(BlogCategory).filter(
            BlogCategory.id.in_(request.category_ids)
        ).all()
        post.categories = categories
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # Reload with relationships
    post = db.query(BlogPost).options(
        joinedload(BlogPost.author),
        joinedload(BlogPost.categories)
    ).filter(BlogPost.id == post.id).first()
    
    return _build_post_response(post, user)


@router.get("/posts/{post_id}", response_model=BlogPostResponse)
async def get_post(
    post_id: UUID,
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Get a post by ID.
    
    Requires API key with blog management permission.
    """
    api_key_record, user = auth
    
    post = db.query(BlogPost).options(
        joinedload(BlogPost.author),
        joinedload(BlogPost.categories)
    ).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return _build_post_response(post, user)


@router.put("/posts/{post_id}", response_model=BlogPostResponse)
async def update_post(
    post_id: UUID,
    request: BlogPostUpdate,
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Update a blog post.
    
    Requires API key with blog management permission.
    """
    api_key_record, user = auth
    
    post = db.query(BlogPost).options(
        joinedload(BlogPost.author),
        joinedload(BlogPost.categories)
    ).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check slug uniqueness if changing
    if request.slug and request.slug != post.slug:
        existing = db.query(BlogPost).filter(
            BlogPost.slug == request.slug,
            BlogPost.id != post_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="A post with this slug already exists")
    
    # Update fields
    if request.title is not None:
        post.title = request.title
    if request.slug is not None:
        post.slug = request.slug
    if request.excerpt is not None:
        post.excerpt = request.excerpt
    if request.content is not None:
        post.content = request.content
    if request.featured_image_url is not None:
        post.featured_image_url = request.featured_image_url
    
    # Update categories if provided
    if request.category_ids is not None:
        categories = db.query(BlogCategory).filter(
            BlogCategory.id.in_(request.category_ids)
        ).all()
        post.categories = categories
    
    db.commit()
    db.refresh(post)
    
    return _build_post_response(post, user)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: UUID,
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Delete a blog post.
    
    Requires API key with blog management permission.
    """
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully", "id": str(post_id)}


@router.post("/posts/{post_id}/publish", response_model=BlogPostResponse)
async def publish_post(
    post_id: UUID,
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Publish a draft post.
    
    Requires API key with blog management permission.
    """
    api_key_record, user = auth
    
    post = db.query(BlogPost).options(
        joinedload(BlogPost.author),
        joinedload(BlogPost.categories)
    ).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "published":
        raise HTTPException(status_code=400, detail="Post is already published")
    
    post.status = "published"
    post.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(post)
    
    return _build_post_response(post, user)


@router.post("/posts/{post_id}/unpublish", response_model=BlogPostResponse)
async def unpublish_post(
    post_id: UUID,
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Unpublish a post (revert to draft).
    
    Requires API key with blog management permission.
    """
    api_key_record, user = auth
    
    post = db.query(BlogPost).options(
        joinedload(BlogPost.author),
        joinedload(BlogPost.categories)
    ).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "draft":
        raise HTTPException(status_code=400, detail="Post is already a draft")
    
    post.status = "draft"
    
    db.commit()
    db.refresh(post)
    
    return _build_post_response(post, user)


# =============================================================================
# Category Endpoints
# =============================================================================

@router.get("/categories", response_model=BlogCategoryListResponse)
async def list_categories(
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    List all blog categories.
    
    Requires API key with blog management permission.
    """
    categories = db.query(BlogCategory).order_by(BlogCategory.name).all()
    
    return BlogCategoryListResponse(
        items=[BlogCategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        ) for cat in categories],
        total=len(categories)
    )


@router.post("/categories", response_model=BlogCategoryResponse)
async def create_category(
    request: BlogCategoryCreate,
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Create a new blog category.
    
    Requires API key with blog management permission.
    """
    # Check if slug already exists
    existing = db.query(BlogCategory).filter(
        (BlogCategory.slug == request.slug) | (BlogCategory.name == request.name)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A category with this name or slug already exists")
    
    category = BlogCategory(
        name=request.name,
        slug=request.slug,
        description=request.description
    )
    
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return BlogCategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


# =============================================================================
# Utility Endpoints
# =============================================================================

@router.post("/generate-slug")
async def generate_slug_endpoint(
    title: str = Query(..., description="Title to generate slug from"),
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    db: Session = Depends(get_db),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Generate a URL-friendly slug from a title.
    
    Also checks if the slug is unique.
    """
    slug = generate_slug(title)
    
    # Check if slug exists
    existing = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    
    return {
        "slug": slug,
        "is_unique": existing is None
    }


@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_blog_image(
    file: UploadFile = File(...),
    auth: Tuple[UserAPIKey, User] = Depends(require_blog_api_key),
    _rate_limit: bool = Depends(blog_rate_limit)
):
    """
    Upload an image for blog posts.

    Returns a URL that can be used as the featured_image_url when creating or updating posts.
    Max file size: 10MB. Allowed types: JPEG, PNG, GIF, WebP.
    Requires API key with blog management permission.
    """
    result = await upload_image(file, folder="blog")
    return ImageUploadResponse(**result)
