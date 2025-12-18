"""Tests for rate limiting"""
import pytest
import time
from unittest.mock import MagicMock

from app.core.rate_limit import RateLimiter, RateLimitDependency, RATE_LIMITS


class TestRateLimiter:
    """Test cases for RateLimiter"""
    
    @pytest.fixture
    def limiter(self):
        """Create fresh rate limiter"""
        return RateLimiter()
    
    def test_first_request_allowed(self, limiter):
        """Test that first request is always allowed"""
        allowed, remaining, reset = limiter.check_rate_limit(
            key="test_key",
            limit=10,
            window_seconds=60
        )
        
        assert allowed is True
        assert remaining == 9
    
    def test_requests_within_limit(self, limiter):
        """Test requests within limit are allowed"""
        for i in range(5):
            allowed, remaining, _ = limiter.check_rate_limit(
                key="test_key",
                limit=10,
                window_seconds=60
            )
            assert allowed is True
            assert remaining == 10 - i - 1
    
    def test_requests_exceed_limit(self, limiter):
        """Test requests exceeding limit are blocked"""
        # Use up all requests
        for _ in range(10):
            limiter.check_rate_limit(
                key="test_key",
                limit=10,
                window_seconds=60
            )
        
        # Next request should be blocked
        allowed, remaining, reset = limiter.check_rate_limit(
            key="test_key",
            limit=10,
            window_seconds=60
        )
        
        assert allowed is False
        assert remaining == 0
        assert reset > 0
    
    def test_different_keys_independent(self, limiter):
        """Test that different keys have independent limits"""
        # Exhaust limit for key1
        for _ in range(10):
            limiter.check_rate_limit("key1", limit=10, window_seconds=60)
        
        # key2 should still be allowed
        allowed, remaining, _ = limiter.check_rate_limit(
            "key2", limit=10, window_seconds=60
        )
        
        assert allowed is True
        assert remaining == 9
    
    def test_reset_clears_limit(self, limiter):
        """Test that reset clears the rate limit"""
        # Use up all requests
        for _ in range(10):
            limiter.check_rate_limit("test_key", limit=10, window_seconds=60)
        
        # Reset the key
        limiter.reset("test_key")
        
        # Should be allowed again
        allowed, remaining, _ = limiter.check_rate_limit(
            "test_key", limit=10, window_seconds=60
        )
        
        assert allowed is True
        assert remaining == 9


class TestRateLimitConfigurations:
    """Test rate limit configurations"""
    
    def test_public_rate_limit(self):
        """Test public rate limit configuration"""
        config = RATE_LIMITS["public"]
        assert config["limit"] == 100
        assert config["window"] == 60
    
    def test_authenticated_rate_limit(self):
        """Test authenticated rate limit configuration"""
        config = RATE_LIMITS["authenticated"]
        assert config["limit"] == 300
        assert config["window"] == 60
    
    def test_runner_rate_limit(self):
        """Test runner rate limit configuration"""
        config = RATE_LIMITS["runner"]
        assert config["limit"] == 50
        assert config["window"] == 3600


class TestRateLimitDependency:
    """Test RateLimitDependency"""
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request"""
        request = MagicMock()
        request.headers = {}
        request.client.host = "127.0.0.1"
        request.state = MagicMock()
        return request
    
    @pytest.mark.asyncio
    async def test_dependency_allows_request(self, mock_request):
        """Test dependency allows request within limit"""
        dependency = RateLimitDependency("public")
        
        # First request should be allowed
        result = await dependency(mock_request)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_dependency_sets_headers(self, mock_request):
        """Test dependency sets rate limit headers"""
        dependency = RateLimitDependency("public")
        
        await dependency(mock_request)
        
        headers = mock_request.state.rate_limit_headers
        assert "X-RateLimit-Limit" in headers
        assert "X-RateLimit-Remaining" in headers
        assert "X-RateLimit-Reset" in headers
    
    @pytest.mark.asyncio
    async def test_dependency_uses_api_key(self):
        """Test dependency uses API key for identification"""
        request = MagicMock()
        request.headers = {"X-API-Key": "test-api-key-12345678901234567890"}
        request.state = MagicMock()
        
        dependency = RateLimitDependency("runner")
        result = await dependency(request)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_dependency_uses_forwarded_ip(self):
        """Test dependency uses X-Forwarded-For header"""
        request = MagicMock()
        request.headers = {"X-Forwarded-For": "1.2.3.4, 5.6.7.8"}
        request.client = None
        request.state = MagicMock()
        
        dependency = RateLimitDependency("public")
        result = await dependency(request)
        
        assert result is True
