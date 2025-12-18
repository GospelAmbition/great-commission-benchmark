"""Core application configuration and utilities"""
from app.core.config import settings

# Note: auth and rate_limit imports are done lazily to avoid circular imports
# Use direct imports like: from app.core.auth import require_auth

__all__ = [
    "settings",
]
