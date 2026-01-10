"""API v1 router"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    public,
    user,
    api_keys,
    submissions,
    runner,
    newsletter,
    donations,
    webhooks,
    moderator,
    admin,
    benchmark,
    sponsorship,
    blog,
    files
)

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Public API
api_router.include_router(public.router, prefix="/public", tags=["public"])

# User API
api_router.include_router(user.router, prefix="/user", tags=["user"])

# API Keys (under /user for organization)
api_router.include_router(api_keys.router, prefix="/user/api-keys", tags=["api-keys"])

# Sponsorship (user endpoints)
api_router.include_router(sponsorship.user_router, prefix="/user/sponsorship", tags=["sponsorship"])

# Submissions API
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])

# Runner API (for CLI)
api_router.include_router(runner.router, prefix="/runner", tags=["runner"])

# Newsletter API
api_router.include_router(newsletter.router, prefix="/newsletter", tags=["newsletter"])

# Payments API removed - test payments removed, CLI/sponsorship payments handled in their endpoints

# Donations API (public, no auth required)
api_router.include_router(donations.router, prefix="/donations", tags=["donations"])

# Webhooks API
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Moderator API
api_router.include_router(moderator.router, prefix="/moderator", tags=["moderator"])

# Moderator Sponsorship API
api_router.include_router(sponsorship.moderator_router, prefix="/moderator/sponsorship", tags=["moderator-sponsorship"])

# Admin API
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# Benchmark Development API (for benchmark_developer and admin roles)
api_router.include_router(benchmark.router, prefix="/benchmark", tags=["benchmark"])

# Blog API (public endpoints)
api_router.include_router(blog.public_router, prefix="/blog", tags=["blog"])

# Blog Admin API
api_router.include_router(blog.admin_router, prefix="/admin/blog", tags=["admin-blog"])

# Files API (public proxy for Railway storage - buckets are private by design)
api_router.include_router(files.router, prefix="/files", tags=["files"])
