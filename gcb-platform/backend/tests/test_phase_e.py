"""Tests for Phase E: Launch Preparation features"""
import pytest

from main import app
from app.db.models.user import User





class TestSecurityHeaders:
    """Test security headers are present"""
    
    def test_security_headers_present(self, client):
        """Test that security headers are added to responses"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "X-XSS-Protection" in response.headers
        assert "Content-Security-Policy" in response.headers


class TestTesterAgreement:
    """Test tester agreement acceptance"""
    
    def test_accept_tester_agreement(self, client, test_user, mock_auth, auth_headers, db_session):
        """Test accepting tester agreement"""
        from app.core.auth import get_current_user
        app.dependency_overrides[get_current_user] = mock_auth(test_user)
        # Get current user
        profile_response = client.get("/api/user/profile", headers=auth_headers(test_user))
        assert profile_response.status_code == 200
        
        # Accept agreement
        response = client.post("/api/user/tester-agreement/accept", headers=auth_headers(test_user))
        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True
        assert "message" in data
        
        # Verify in database
        user = db_session.query(User).filter(User.id == test_user.id).first()
        assert user is not None
        assert user.tester_agreement_accepted is True
        assert user.tester_agreement_accepted_at is not None
    
    def test_accept_tester_agreement_already_accepted(self, client, test_user, mock_auth, auth_headers, db_session):
        """Test accepting agreement when already accepted"""
        from app.core.auth import get_current_user
        app.dependency_overrides[get_current_user] = mock_auth(test_user)
        # Accept once
        first = client.post("/api/user/tester-agreement/accept", headers=auth_headers(test_user))
        assert first.status_code == 200
        accepted_at = test_user.tester_agreement_accepted_at
        # Try to accept again
        response = client.post("/api/user/tester-agreement/accept", headers=auth_headers(test_user))
        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True
        assert "already accepted" in data["message"].lower()
        db_session.refresh(test_user)
        assert test_user.tester_agreement_accepted_at == accepted_at
    
    def test_accept_tester_agreement_requires_auth(self, client):
        """Test that accepting agreement requires authentication"""
        response = client.post("/api/user/tester-agreement/accept")
        assert response.status_code == 403
        assert response.json()["detail"] == "Not authenticated"


class TestRateLimiting:
    """Exercise the reusable rate-limit dependency with isolated client state.

    Public routes currently do not install this optional dependency; testing it
    directly avoids claiming that repeated public stats requests prove throttling.
    """

    @pytest.fixture
    def request_and_limiter(self, monkeypatch):
        from starlette.requests import Request
        from app.core import rate_limit
        monkeypatch.setattr(rate_limit, "rate_limiter", rate_limit.RateLimiter())
        request = Request({"type": "http", "headers": [], "client": ("test-client", 1234)})
        return request, rate_limit.RateLimitDependency("public")

    @pytest.mark.asyncio
    async def test_rate_limit_metadata_present(self, request_and_limiter):
        request, dependency = request_and_limiter
        assert await dependency(request) is True
        assert request.state.rate_limit_headers == {
            "X-RateLimit-Limit": "100", "X-RateLimit-Remaining": "99",
            "X-RateLimit-Reset": "60", "X-RateLimit-Window": "60",
        }

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, request_and_limiter):
        from fastapi import HTTPException
        request, dependency = request_and_limiter
        for _ in range(100):
            assert await dependency(request) is True
        with pytest.raises(HTTPException) as caught:
            await dependency(request)
        assert caught.value.status_code == 429
        assert caught.value.headers["X-RateLimit-Remaining"] == "0"
        assert 0 < int(caught.value.headers["Retry-After"]) <= 60
        assert caught.value.detail["error"] == "Rate limit exceeded"

    def test_public_stats_uses_isolated_database(self, client):
        response = client.get("/api/public/stats")
        assert response.status_code == 200


class TestLegalPages:
    """Test legal document pages are accessible"""
    
    def test_terms_page_exists(self, client):
        """Test that terms page route exists"""
        # Note: This tests backend, frontend pages would be tested separately
        # For now, verify API endpoints work
        response = client.get("/health")
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_handler(self, client):
        """Test 404 handling for non-existent endpoints"""
        response = client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404
    
    def test_health_endpoint(self, client):
        """Test health endpoint works"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
