"""Rate limiting middleware and utilities"""
import time
from typing import Dict, Optional, Callable
from collections import defaultdict
from fastapi import Request, HTTPException, Depends
from functools import wraps


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self):
        # Store: {key: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
    
    def _cleanup_old_requests(self, key: str, window_seconds: int):
        """Remove requests older than the window"""
        cutoff = time.time() - window_seconds
        self._requests[key] = [
            (ts, count) for ts, count in self._requests[key]
            if ts > cutoff
        ]
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique identifier (e.g., IP, API key, user ID)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        now = time.time()
        
        # Cleanup old requests
        self._cleanup_old_requests(key, window_seconds)
        
        # Count requests in current window
        total_requests = sum(count for _, count in self._requests[key])
        
        if total_requests >= limit:
            # Calculate reset time
            if self._requests[key]:
                oldest = min(ts for ts, _ in self._requests[key])
                reset_time = int(oldest + window_seconds - now)
            else:
                reset_time = window_seconds
            return False, 0, reset_time
        
        # Add current request
        self._requests[key].append((now, 1))
        
        remaining = limit - total_requests - 1
        return True, remaining, window_seconds
    
    def reset(self, key: str):
        """Reset rate limit for a key"""
        if key in self._requests:
            del self._requests[key]


# Global rate limiter instance
rate_limiter = RateLimiter()


# Rate limit configurations
RATE_LIMITS = {
    "public": {"limit": 100, "window": 60},      # 100 req/min
    "authenticated": {"limit": 300, "window": 60}, # 300 req/min
    "submissions": {"limit": 10, "window": 3600}, # 10 req/hour
}


def get_client_identifier(request: Request) -> str:
    """Get unique identifier for the client"""
    # Try to get API key first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api:{api_key[:16]}"  # Use first 16 chars of API key
    
    # Fall back to IP address
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get the first IP in the chain (original client)
        return f"ip:{forwarded.split(',')[0].strip()}"
    
    return f"ip:{request.client.host if request.client else 'unknown'}"


class RateLimitDependency:
    """
    FastAPI dependency for rate limiting.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(
            _: bool = Depends(RateLimitDependency("public"))
        ):
            ...
    """
    
    def __init__(self, limit_type: str = "public"):
        self.limit_type = limit_type
        self.config = RATE_LIMITS.get(limit_type, RATE_LIMITS["public"])
    
    async def __call__(self, request: Request) -> bool:
        client_id = get_client_identifier(request)
        key = f"{self.limit_type}:{client_id}"
        
        allowed, remaining, reset_time = rate_limiter.check_rate_limit(
            key=key,
            limit=self.config["limit"],
            window_seconds=self.config["window"]
        )
        
        # Add rate limit headers to response
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(self.config["limit"]),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
            "X-RateLimit-Window": str(self.config["window"])
        }
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.config["limit"],
                    "window_seconds": self.config["window"],
                    "retry_after": reset_time
                },
                headers={
                    "Retry-After": str(reset_time),
                    "X-RateLimit-Limit": str(self.config["limit"]),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time)
                }
            )
        
        return True


# Convenience functions for common rate limits
def rate_limit_public():
    """Rate limit for public endpoints: 100 req/min"""
    return RateLimitDependency("public")

def rate_limit_authenticated():
    """Rate limit for authenticated endpoints: 300 req/min"""
    return RateLimitDependency("authenticated")

def rate_limit_submissions():
    """Rate limit for submission endpoints: 10 req/hour"""
    return RateLimitDependency("submissions")
