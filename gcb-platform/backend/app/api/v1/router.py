"""API v1 router"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    public,
    user,
    tests,
    submissions,
    runner,
    newsletter
)

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Public API
api_router.include_router(public.router, prefix="/public", tags=["public"])

# User API
api_router.include_router(user.router, prefix="/user", tags=["user"])

# Tests API
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])

# Submissions API
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])

# Runner API (for CLI)
api_router.include_router(runner.router, prefix="/runner", tags=["runner"])

# Newsletter API
api_router.include_router(newsletter.router, prefix="/newsletter", tags=["newsletter"])
