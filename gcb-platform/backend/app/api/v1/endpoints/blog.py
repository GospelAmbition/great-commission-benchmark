"""Blog API endpoints for Action section CMS"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from uuid import UUID
from datetime import datetime
import re

from app.core.auth import get_db, require_blog_manager, get_current_user
from app.db.models.user import User
from app.db.models.blog_post import BlogPost
from app.db.models.blog_category import BlogCategory
from app.db.models.model import Model
from app.schemas.blog import (
    BlogCategoryCreate,
    BlogCategoryUpdate,
    BlogCategoryResponse,
    BlogCategoryListResponse,
    BlogPostCreate,
    BlogPostUpdate,
    BlogPostResponse,
    BlogPostListItem,
    BlogPostListResponse,
    BlogPostAuthor,
    BlogRelatedModel,
    ImageUploadResponse,
)
from app.services.storage import upload_image
from app.services.action_log import ActionLogService

# Create routers for public and admin endpoints
public_router = APIRouter()
admin_router = APIRouter()


async def _invalidate_recent_tests_cache() -> None:
    """Refresh model/article links exposed by the Recent Tests collection."""
    from app.services.published_cache import invalidate_namespaces

    await invalidate_namespaces("recent_tests")


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def _resolve_model_ids(db: Session, model_id_strings: List[str]) -> list:
    """Resolve OpenRouter model_id strings to Model ORM objects."""
    if not model_id_strings:
        return []
    return db.query(Model).filter(Model.model_id.in_(model_id_strings)).all()


def _build_related_models(post: BlogPost) -> List[BlogRelatedModel]:
    """Build list of BlogRelatedModel from a post's linked models."""
    return [
        BlogRelatedModel(
            id=m.id,
            model_id=m.model_id,
            name=m.name,
            provider=m.provider,
        )
        for m in (post.models or [])
    ]


def _post_query(db: Session):
    """Return a base query with standard eager-loads for blog posts."""
    return db.query(BlogPost).options(
        joinedload(BlogPost.author),
        joinedload(BlogPost.categories),
        joinedload(BlogPost.models),
    )


# =============================================================================
# Public Endpoints (no auth required)
# =============================================================================

@public_router.get("/posts", response_model=BlogPostListResponse)
async def list_published_posts(
    category: Optional[str] = Query(None, description="Filter by category slug"),
    search: Optional[str] = Query(None, description="Search in title or excerpt"),
    model_id: Optional[str] = Query(None, description="Filter by OpenRouter model_id"),
    provider: Optional[str] = Query(None, description="Filter by provider slug"),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List published blog posts, optionally filtered by category, model, or provider."""
    query = _post_query(db).filter(BlogPost.status == "published")
    
    if category:
        query = query.join(BlogPost.categories).filter(BlogCategory.slug == category)

    if model_id or provider:
        query = query.join(BlogPost.models)
        if model_id:
            query = query.filter(Model.model_id == model_id)
        if provider:
            query = query.filter(Model.provider == provider)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (BlogPost.title.ilike(search_filter)) | 
            (BlogPost.excerpt.ilike(search_filter)) |
            (BlogPost.content.ilike(search_filter))
        )
    
    query = query.order_by(desc(BlogPost.published_at))
    
    # Count query (mirrors filters above but without eager loads)
    total_query = db.query(BlogPost).filter(BlogPost.status == "published")
    if category:
        total_query = total_query.join(BlogPost.categories).filter(BlogCategory.slug == category)
    if model_id or provider:
        total_query = total_query.join(BlogPost.models)
        if model_id:
            total_query = total_query.filter(Model.model_id == model_id)
        if provider:
            total_query = total_query.filter(Model.provider == provider)
    if search:
        search_filter = f"%{search}%"
        total_query = total_query.filter(
            (BlogPost.title.ilike(search_filter)) | 
            (BlogPost.excerpt.ilike(search_filter)) |
            (BlogPost.content.ilike(search_filter))
        )
    total = total_query.count()
    
    posts = query.offset(offset).limit(limit).all()
    
    items = []
    for post in posts:
        items.append(BlogPostListItem(
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
            related_models=_build_related_models(post),
            created_at=post.created_at,
            published_at=post.published_at
        ))
    
    return BlogPostListResponse(items=items, total=total)


@public_router.get("/posts/{slug}", response_model=BlogPostResponse)
async def get_published_post(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a single published post by slug"""
    post = _post_query(db).filter(
        BlogPost.slug == slug,
        BlogPost.status == "published"
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
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
        related_models=_build_related_models(post),
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at
    )


@public_router.get("/categories", response_model=BlogCategoryListResponse)
async def list_categories(
    db: Session = Depends(get_db)
):
    """List all blog categories"""
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


# =============================================================================
# Blog Manager Endpoints (require blog_manager role or higher)
# =============================================================================

@admin_router.get("/posts", response_model=BlogPostListResponse)
async def admin_list_posts(
    status: Optional[str] = Query(None, description="Filter by status (draft, published)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """List all blog posts (including drafts) - Blog Manager or higher"""
    query = _post_query(db)
    
    if status:
        query = query.filter(BlogPost.status == status)
    
    query = query.order_by(desc(BlogPost.updated_at))
    
    count_query = db.query(BlogPost)
    if status:
        count_query = count_query.filter(BlogPost.status == status)
    total = count_query.count()
    
    posts = query.offset(offset).limit(limit).all()
    
    items = []
    for post in posts:
        items.append(BlogPostListItem(
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
            related_models=_build_related_models(post),
            created_at=post.created_at,
            published_at=post.published_at
        ))
    
    return BlogPostListResponse(items=items, total=total)


@admin_router.post("/posts", response_model=BlogPostResponse)
async def create_post(
    request: BlogPostCreate,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Create a new blog post - Blog Manager or higher"""
    # Check if slug already exists
    existing = db.query(BlogPost).filter(BlogPost.slug == request.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="A post with this slug already exists")
    
    # Create post
    post = BlogPost(
        title=request.title,
        slug=request.slug,
        excerpt=request.excerpt,
        content=request.content,
        featured_image_url=request.featured_image_url,
        status="draft",
        author_id=current_user.id
    )
    
    # Add categories if provided
    if request.category_ids:
        categories = db.query(BlogCategory).filter(
            BlogCategory.id.in_(request.category_ids)
        ).all()
        post.categories = categories
    
    # Link models if provided
    if request.model_ids:
        post.models = _resolve_model_ids(db, request.model_ids)
    
    db.add(post)
    db.commit()
    db.refresh(post)
    await _invalidate_recent_tests_cache()

    ActionLogService.log_action(
        db, "blog_post.create", "user",
        actor_user_id=current_user.id,
        entity_type="blog_post", entity_id=str(post.id),
        metadata={"slug": post.slug, "title": post.title}
    )
    
    return BlogPostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        excerpt=post.excerpt,
        content=post.content,
        featured_image_url=post.featured_image_url,
        status=post.status,
        author=BlogPostAuthor(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email
        ),
        categories=[BlogCategoryResponse(
            id=cat.id,
            name=cat.name,
            slug=cat.slug,
            description=cat.description,
            created_at=cat.created_at,
            updated_at=cat.updated_at
        ) for cat in post.categories],
        related_models=_build_related_models(post),
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at
    )


@admin_router.get("/posts/{post_id}", response_model=BlogPostResponse)
async def admin_get_post(
    post_id: UUID,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Get a post by ID - Blog Manager or higher"""
    post = _post_query(db).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
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
        related_models=_build_related_models(post),
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at
    )


@admin_router.put("/posts/{post_id}", response_model=BlogPostResponse)
async def update_post(
    post_id: UUID,
    request: BlogPostUpdate,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Update a blog post - Blog Manager or higher"""
    post = _post_query(db).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if request.slug and request.slug != post.slug:
        existing = db.query(BlogPost).filter(
            BlogPost.slug == request.slug,
            BlogPost.id != post_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="A post with this slug already exists")
    
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
    
    if request.category_ids is not None:
        categories = db.query(BlogCategory).filter(
            BlogCategory.id.in_(request.category_ids)
        ).all()
        post.categories = categories
    
    if request.model_ids is not None:
        post.models = _resolve_model_ids(db, request.model_ids)
    
    db.commit()
    db.refresh(post)
    await _invalidate_recent_tests_cache()

    ActionLogService.log_action(
        db, "blog_post.update", "user",
        actor_user_id=current_user.id,
        entity_type="blog_post", entity_id=str(post.id),
        metadata={"slug": post.slug, "title": post.title}
    )
    
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
        related_models=_build_related_models(post),
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at
    )


@admin_router.delete("/posts/{post_id}")
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Delete a blog post - Blog Manager or higher"""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_slug, post_title = post.slug, post.title
    db.delete(post)
    db.commit()
    await _invalidate_recent_tests_cache()

    ActionLogService.log_action(
        db, "blog_post.delete", "user",
        actor_user_id=current_user.id,
        entity_type="blog_post", entity_id=str(post_id),
        metadata={"slug": post_slug, "title": post_title}
    )
    
    return {"message": "Post deleted successfully"}


@admin_router.post("/posts/{post_id}/publish", response_model=BlogPostResponse)
async def publish_post(
    post_id: UUID,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Publish a draft post - Blog Manager or higher"""
    post = _post_query(db).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "published":
        raise HTTPException(status_code=400, detail="Post is already published")
    
    post.status = "published"
    post.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(post)
    await _invalidate_recent_tests_cache()

    ActionLogService.log_action(
        db, "blog_post.publish", "user",
        actor_user_id=current_user.id,
        entity_type="blog_post", entity_id=str(post.id),
        metadata={"slug": post.slug, "title": post.title}
    )
    
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
        related_models=_build_related_models(post),
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at
    )


@admin_router.post("/posts/{post_id}/unpublish", response_model=BlogPostResponse)
async def unpublish_post(
    post_id: UUID,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Unpublish a post (revert to draft) - Blog Manager or higher"""
    post = _post_query(db).filter(BlogPost.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.status == "draft":
        raise HTTPException(status_code=400, detail="Post is already a draft")
    
    post.status = "draft"
    
    db.commit()
    db.refresh(post)
    await _invalidate_recent_tests_cache()

    ActionLogService.log_action(
        db, "blog_post.unpublish", "user",
        actor_user_id=current_user.id,
        entity_type="blog_post", entity_id=str(post.id),
        metadata={"slug": post.slug, "title": post.title}
    )
    
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
        related_models=_build_related_models(post),
        created_at=post.created_at,
        updated_at=post.updated_at,
        published_at=post.published_at
    )


@admin_router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_blog_image(
    file: UploadFile = File(...),
    current_user: User = Depends(require_blog_manager),
):
    """Upload an image for blog posts - Blog Manager or higher"""
    result = await upload_image(file, folder="blog")
    return ImageUploadResponse(**result)


# =============================================================================
# Category Admin Endpoints
# =============================================================================

@admin_router.get("/categories", response_model=BlogCategoryListResponse)
async def admin_list_categories(
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """List all categories - Blog Manager or higher"""
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


@admin_router.post("/categories", response_model=BlogCategoryResponse)
async def create_category(
    request: BlogCategoryCreate,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Create a new category - Blog Manager or higher"""
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

    ActionLogService.log_action(
        db, "blog_category.create", "user",
        actor_user_id=current_user.id,
        entity_type="blog_category", entity_id=str(category.id),
        metadata={"slug": category.slug, "name": category.name}
    )
    
    return BlogCategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@admin_router.put("/categories/{category_id}", response_model=BlogCategoryResponse)
async def update_category(
    category_id: UUID,
    request: BlogCategoryUpdate,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Update a category - Blog Manager or higher"""
    category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check uniqueness if changing name/slug
    if request.name and request.name != category.name:
        existing = db.query(BlogCategory).filter(
            BlogCategory.name == request.name,
            BlogCategory.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="A category with this name already exists")
    
    if request.slug and request.slug != category.slug:
        existing = db.query(BlogCategory).filter(
            BlogCategory.slug == request.slug,
            BlogCategory.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="A category with this slug already exists")
    
    # Update fields
    if request.name is not None:
        category.name = request.name
    if request.slug is not None:
        category.slug = request.slug
    if request.description is not None:
        category.description = request.description
    
    db.commit()
    db.refresh(category)

    ActionLogService.log_action(
        db, "blog_category.update", "user",
        actor_user_id=current_user.id,
        entity_type="blog_category", entity_id=str(category.id),
        metadata={"slug": category.slug, "name": category.name}
    )
    
    return BlogCategoryResponse(
        id=category.id,
        name=category.name,
        slug=category.slug,
        description=category.description,
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@admin_router.delete("/categories/{category_id}")
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(require_blog_manager),
    db: Session = Depends(get_db)
):
    """Delete a category - Blog Manager or higher"""
    category = db.query(BlogCategory).filter(BlogCategory.id == category_id).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    cat_slug, cat_name = category.slug, category.name
    db.delete(category)
    db.commit()

    ActionLogService.log_action(
        db, "blog_category.delete", "user",
        actor_user_id=current_user.id,
        entity_type="blog_category", entity_id=str(category_id),
        metadata={"slug": cat_slug, "name": cat_name}
    )
    
    return {"message": "Category deleted successfully"}
