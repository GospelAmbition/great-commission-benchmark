"""Simple in-memory caching for API responses"""
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import wraps
import hashlib
import json
import asyncio


class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if datetime.utcnow() < expiry:
                    return value
                else:
                    # Clean up expired entry
                    del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set value in cache with TTL"""
        async with self._lock:
            expiry = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            self._cache[key] = (value, expiry)
    
    async def delete(self, key: str):
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    async def clear(self):
        """Clear all cached values"""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self):
        """Remove all expired entries"""
        async with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if now >= expiry
            ]
            for key in expired_keys:
                del self._cache[key]


# Global cache instance
cache = SimpleCache()


# Cache TTL settings (in seconds)
CACHE_TTL = {
    "leaderboard": 300,      # 5 minutes
    "model_details": 300,    # 5 minutes
    "public_stats": 300,     # 5 minutes
    "versions": 600,         # 10 minutes
    "models_list": 300,      # 5 minutes
}


def make_cache_key(prefix: str, params: dict = None) -> str:
    """Generate a cache key from prefix and parameters"""
    if params:
        # Sort params for consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
        return f"{prefix}:{param_hash}"
    return prefix


def cached(prefix: str, ttl: int = 300):
    """Decorator for caching async function results
    
    Usage:
        @cached("leaderboard", ttl=300)
        async def get_leaderboard(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_params = {
                "args": str(args[1:]) if args else "",  # Skip 'self' or 'db' arg
                "kwargs": str(kwargs)
            }
            key = make_cache_key(prefix, cache_params)
            
            # Try to get from cache
            cached_value = await cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator


async def invalidate_cache(prefix: str):
    """Invalidate all cache entries with given prefix
    
    This is a simple implementation that clears the entire cache.
    For a production system, you'd want Redis with key patterns.
    """
    # For simplicity, just clear the entire cache
    # In production, use Redis with SCAN and pattern matching
    await cache.clear()
