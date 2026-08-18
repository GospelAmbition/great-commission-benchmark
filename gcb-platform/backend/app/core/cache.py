"""Caching for API responses with stale-while-revalidate support.

Two backends are available:
- SimpleCache  – in-memory; default for local dev; lost on restart.
- RedisCache   – backed by Redis; persists across restarts and deploys.
                 Activated when REDIS_URL is set in the environment.
"""
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable, Awaitable, Tuple
from functools import wraps
import hashlib
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class CacheEntry:
    """Represents a cached value with fresh and stale expiry times"""
    def __init__(self, value: Any, fresh_expiry: datetime, stale_expiry: datetime):
        self.value = value
        self.fresh_expiry = fresh_expiry  # When data becomes stale (triggers background refresh)
        self.stale_expiry = stale_expiry  # When data is too old to serve at all
    
    def is_fresh(self) -> bool:
        return datetime.utcnow() < self.fresh_expiry
    
    def is_stale_but_usable(self) -> bool:
        now = datetime.utcnow()
        return self.fresh_expiry <= now < self.stale_expiry
    
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.stale_expiry


class SimpleCache:
    """Simple in-memory cache with TTL and stale-while-revalidate support"""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._refresh_callbacks: Dict[str, Callable[[], Awaitable[None]]] = {}
        self._refreshing_keys: set = set()  # Track keys currently being refreshed
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired (standard TTL behavior)"""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    return entry.value
                else:
                    # Clean up expired entry
                    del self._cache[key]
            return None
    
    async def get_with_stale(self, key: str) -> Tuple[Optional[Any], bool, bool]:
        """
        Get value with stale-while-revalidate support.
        
        Returns: (value, is_fresh, should_refresh)
        - value: The cached value or None
        - is_fresh: True if data is within fresh TTL
        - should_refresh: True if a background refresh should be triggered
        """
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if entry.is_fresh():
                    return entry.value, True, False
                elif entry.is_stale_but_usable():
                    # Return stale data, signal that refresh is needed
                    should_refresh = key not in self._refreshing_keys
                    return entry.value, False, should_refresh
                else:
                    # Too old, clean up
                    del self._cache[key]
            return None, False, False
    
    async def set(self, key: str, value: Any, ttl_seconds: int = 300, stale_ttl_seconds: Optional[int] = None):
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time until data is considered stale (triggers background refresh)
            stale_ttl_seconds: Time until data is too old to serve (defaults to 2x ttl_seconds)
        """
        if stale_ttl_seconds is None:
            stale_ttl_seconds = ttl_seconds * 2  # Serve stale data for up to 2x the fresh TTL
        
        async with self._lock:
            now = datetime.utcnow()
            fresh_expiry = now + timedelta(seconds=ttl_seconds)
            stale_expiry = now + timedelta(seconds=stale_ttl_seconds)
            self._cache[key] = CacheEntry(value, fresh_expiry, stale_expiry)
    
    async def delete(self, key: str):
        """Delete value from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def delete_prefix(self, prefix: str) -> int:
        """Delete every entry whose application key starts with ``prefix``."""
        async with self._lock:
            keys = [key for key in self._cache if key.startswith(prefix)]
            for key in keys:
                del self._cache[key]
            self._refreshing_keys.difference_update(keys)
            return len(keys)
    
    async def clear(self):
        """Clear all cached values"""
        async with self._lock:
            self._cache.clear()
    
    async def cleanup_expired(self):
        """Remove all expired entries"""
        async with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
    
    def register_refresh_callback(self, key_prefix: str, callback: Callable[[], Awaitable[None]]):
        """Register a callback to refresh cache entries with a given prefix"""
        self._refresh_callbacks[key_prefix] = callback
    
    async def mark_refreshing(self, key: str):
        """Mark a key as currently being refreshed"""
        async with self._lock:
            self._refreshing_keys.add(key)
    
    async def unmark_refreshing(self, key: str):
        """Unmark a key as being refreshed"""
        async with self._lock:
            self._refreshing_keys.discard(key)
    
    async def trigger_background_refresh(self, key: str):
        """Trigger a background refresh for a stale cache entry"""
        # Find matching callback by prefix
        for prefix, callback in self._refresh_callbacks.items():
            if key.startswith(prefix):
                await self.mark_refreshing(key)
                try:
                    asyncio.create_task(self._run_refresh(key, callback))
                except Exception as e:
                    logger.error(f"Failed to start background refresh for {key}: {e}")
                    await self.unmark_refreshing(key)
                return
    
    async def _run_refresh(self, key: str, callback: Callable[[], Awaitable[None]]):
        """Run a refresh callback and clean up"""
        try:
            logger.info(f"Starting background cache refresh for {key}")
            await callback()
            logger.info(f"Completed background cache refresh for {key}")
        except Exception as e:
            logger.error(f"Background refresh failed for {key}: {e}")
        finally:
            await self.unmark_refreshing(key)


# ---------------------------------------------------------------------------
# Redis-backed cache
# ---------------------------------------------------------------------------

def _serialize(value: Any) -> str:
    """Serialize a value to a JSON string, handling Pydantic models."""
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    return json.dumps(value, default=str)


def _deserialize(raw: str) -> Any:
    return json.loads(raw)


class RedisCache:
    """Redis-backed cache with TTL and stale-while-revalidate support.

    All keys are stored under the ``gcb:`` prefix so that ``clear()``
    can remove only GCB keys without affecting other data on the same
    Redis instance.

    Each cache entry is a single Redis key whose value is a JSON object::

        { "v": <payload>, "fe": <fresh_expiry_ts>, "se": <stale_expiry_ts> }

    The key's Redis TTL is set to *stale_expiry* so Redis itself evicts
    entries that are too old to serve.
    """

    KEY_PREFIX = "gcb:"
    REFRESHING_SET = "gcb:refreshing"

    def __init__(self, redis_url: str):
        import redis.asyncio as aioredis
        self._redis: aioredis.Redis = aioredis.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )

    def _k(self, key: str) -> str:
        return f"{self.KEY_PREFIX}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Return the value if the entry exists and is not fully expired."""
        try:
            raw = await self._redis.get(self._k(key))
            if raw is None:
                return None
            entry = _deserialize(raw)
            now = datetime.utcnow().timestamp()
            se = entry.get("se", 0)
            if now >= se:
                # Too old — expired (Redis should have deleted it, but guard anyway)
                return None
            return entry["v"]
        except Exception as exc:
            logger.warning("RedisCache.get error for %s: %s", key, exc)
            return None

    async def get_with_stale(self, key: str) -> Tuple[Optional[Any], bool, bool]:
        """Return ``(value, is_fresh, should_refresh)``."""
        try:
            raw = await self._redis.get(self._k(key))
            if raw is None:
                return None, False, False
            entry = _deserialize(raw)
            now = datetime.utcnow().timestamp()
            fe = entry.get("fe", 0)
            se = entry.get("se", 0)
            if now >= se:
                return None, False, False
            if now < fe:
                return entry["v"], True, False
            # Stale but usable
            refreshing = await self._redis.sismember(self.REFRESHING_SET, key)
            should_refresh = not bool(refreshing)
            return entry["v"], False, should_refresh
        except Exception as exc:
            logger.warning("RedisCache.get_with_stale error for %s: %s", key, exc)
            return None, False, False

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 300,
        stale_ttl_seconds: Optional[int] = None,
    ) -> None:
        if stale_ttl_seconds is None:
            stale_ttl_seconds = ttl_seconds * 2
        now = datetime.utcnow().timestamp()
        entry = {
            "v": json.loads(_serialize(value)),
            "fe": now + ttl_seconds,
            "se": now + stale_ttl_seconds,
        }
        try:
            await self._redis.set(
                self._k(key),
                json.dumps(entry),
                ex=stale_ttl_seconds,
            )
        except Exception as exc:
            logger.warning("RedisCache.set error for %s: %s", key, exc)

    async def delete(self, key: str) -> None:
        try:
            await self._redis.delete(self._k(key))
        except Exception as exc:
            logger.warning("RedisCache.delete error for %s: %s", key, exc)

    async def delete_prefix(self, prefix: str) -> int:
        """Delete application keys matching ``prefix`` without flushing Redis."""
        deleted = 0
        try:
            cursor = 0
            pattern = self._k(f"{prefix}*")
            while True:
                cursor, keys = await self._redis.scan(cursor, match=pattern, count=200)
                if keys:
                    deleted += int(await self._redis.delete(*keys))
                if cursor == 0:
                    break
            return deleted
        except Exception as exc:
            logger.warning("RedisCache.delete_prefix error for %s: %s", prefix, exc)
            return deleted

    async def clear(self) -> None:
        """Delete all GCB-prefixed keys from Redis."""
        try:
            cursor = 0
            pattern = f"{self.KEY_PREFIX}*"
            while True:
                cursor, keys = await self._redis.scan(cursor, match=pattern, count=200)
                if keys:
                    await self._redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception as exc:
            logger.warning("RedisCache.clear error: %s", exc)

    async def mark_refreshing(self, key: str) -> None:
        try:
            # Expire the membership after stale TTL + buffer so it doesn't leak
            await self._redis.sadd(self.REFRESHING_SET, key)
            await self._redis.expire(self.REFRESHING_SET, 3600)
        except Exception as exc:
            logger.warning("RedisCache.mark_refreshing error for %s: %s", key, exc)

    async def unmark_refreshing(self, key: str) -> None:
        try:
            await self._redis.srem(self.REFRESHING_SET, key)
        except Exception as exc:
            logger.warning("RedisCache.unmark_refreshing error for %s: %s", key, exc)

    # The remaining SimpleCache methods (cleanup_expired, register_refresh_callback,
    # trigger_background_refresh) are not called externally so we provide no-ops.
    async def cleanup_expired(self) -> None:
        pass

    def register_refresh_callback(self, key_prefix: str, callback: Callable[[], Awaitable[None]]) -> None:
        pass

    async def trigger_background_refresh(self, key: str) -> None:
        pass


# ---------------------------------------------------------------------------
# Global cache instance — switched at import time based on config
# ---------------------------------------------------------------------------

def _make_cache() -> "SimpleCache | RedisCache":
    try:
        from app.core.config import settings
        redis_url = settings.REDIS_URL
    except Exception:
        redis_url = ""

    if redis_url:
        logger.info("Cache backend: Redis (%s)", redis_url.split("@")[-1])
        return RedisCache(redis_url)

    logger.info("Cache backend: in-memory SimpleCache")
    return SimpleCache()


# Global cache instance
cache = _make_cache()


# Cache TTL settings (in seconds)
# Fresh TTL = when background refresh is triggered (24 hours)
# Stale TTL = when data is too old to serve (30 days for critical endpoints)
# This ensures users always get instant responses while data is refreshed in background
CACHE_TTL = {
    "leaderboard": 86400,        # 24 hours fresh, then serve stale while refreshing
    "category_rankings": 86400,  # 24 hours
    "model_details": 86400,      # 24 hours
    "public_stats": 86400,       # 24 hours
    "versions": 86400,           # 24 hours
    "models_list": 86400,        # 24 hours
    "runner_models": 86400,      # 24 hours
    "model_snapshot": 2592000,   # 30 days; invalidated on published-data changes
    "model_comparison": 86400,   # 24 hours
}

# Stale TTL - how long to serve stale data while refreshing (30 days for critical endpoints)
# This ensures that even if a refresh fails, users still get data
CACHE_STALE_TTL = {
    "leaderboard": 2592000,       # 30 days - serve stale rather than wait
    "category_rankings": 2592000, # 30 days
    "model_details": 2592000,     # 30 days
    "public_stats": 2592000,      # 30 days
    "versions": 2592000,          # 30 days
    "models_list": 2592000,       # 30 days
    "runner_models": 86400,       # hard expiry; mutations invalidate immediately
    "model_snapshot": 2592000,    # hard expiry
    "model_comparison": 2592000,  # 30 days
}


def make_cache_key(prefix: str, params: dict = None) -> str:
    """Generate a cache key from prefix and parameters"""
    if params:
        # Sort params for consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        param_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
        return f"{prefix}:{param_hash}"
    return prefix


def cached(prefix: str, ttl: int = 300, stale_ttl: Optional[int] = None):
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
            await cache.set(key, result, ttl, stale_ttl)
            return result
        
        return wrapper
    return decorator


async def invalidate_cache(prefix: str):
    """Invalidate all cache entries with given prefix
    
    Both cache backends support prefix deletion, so unrelated cached data is
    retained when one derived collection changes.
    """
    return await cache.delete_prefix(prefix)


# Type alias for refresh callback
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    RefreshCallback = Callable[[], Awaitable[None]]
