"""Tests for moderator endpoints"""
import pytest
from uuid import uuid4

from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.db.models.moderation_log import ModerationLog


class TestModeratorEndpoints:
    """Tests for moderator API endpoints"""
    
    def test_get_moderation_queue(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run
    ):
        """Test GET /api/moderator/queue"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.get("/api/moderator/queue")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        app.dependency_overrides.clear()
    
    def test_get_moderation_queue_with_status_filter(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run
    ):
        """Test moderation queue filtering by status"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.get("/api/moderator/queue?status=automated")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        
        app.dependency_overrides.clear()
    
    def test_get_queue_item_detail(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run,
        test_results
    ):
        """Test GET /api/moderator/queue/{test_id}"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.get(f"/api/moderator/queue/{completed_test_run.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "test_id" in data
        assert "sample_verdicts" in data
        assert "existing_reviews" in data
        
        app.dependency_overrides.clear()
    
    def test_get_queue_item_detail_not_found(
        self,
        client,
        db_session,
        moderator_user
    ):
        """Test queue item detail for non-existent test"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.get(f"/api/moderator/queue/{uuid4()}")
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_submit_review(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run,
        test_results
    ):
        """Test POST /api/moderator/reviews"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.post(
            "/api/moderator/reviews",
            json={
                "test_id": str(completed_test_run.id),
                "verdict_reviews": [
                    {
                        "result_id": str(test_results[0].id),
                        "verdict": "agree"
                    }
                ],
                "overall_assessment": "verified",
                "notes": "Test review notes"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "review_id" in data
        assert "test_id" in data
        assert "trust_tier" in data
        assert data["trust_tier"] == "reviewed"  # First review sets to "reviewed"
        
        app.dependency_overrides.clear()
    
    def test_submit_review_concerns_triggers_second_review(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run,
        test_results
    ):
        """Test that concerns trigger second review requirement"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.post(
            "/api/moderator/reviews",
            json={
                "test_id": str(completed_test_run.id),
                "verdict_reviews": [
                    {
                        "result_id": str(test_results[0].id),
                        "verdict": "disagree"
                    }
                ],
                "overall_assessment": "concerns",
                "notes": "Found issues"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["trust_tier"] == "pending_review"
        assert data["requires_second_review"] == True
        
        app.dependency_overrides.clear()
    
    def test_get_moderator_activity(
        self,
        client,
        db_session,
        moderator_user
    ):
        """Test GET /api/moderator/activity"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.get("/api/moderator/activity")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        app.dependency_overrides.clear()
    
    def test_get_moderator_stats(
        self,
        client,
        db_session,
        moderator_user
    ):
        """Test GET /api/moderator/stats"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.get("/api/moderator/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "personal" in data
        assert "system_wide" in data
        assert "total_reviews" in data["personal"]
        assert "agreement_rate" in data["personal"]
        
        app.dependency_overrides.clear()
    
    def test_moderator_requires_role(
        self,
        client,
        db_session,
        test_user
    ):
        """Test that moderator endpoints require moderator role"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return test_user  # Regular user, not moderator
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.get("/api/moderator/queue")
        
        assert response.status_code == 403
        
        app.dependency_overrides.clear()
    
    def test_get_community_submission_queue(
        self,
        client,
        db_session,
        moderator_user
    ):
        """Test GET /api/moderator/community"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        response = client.get("/api/moderator/community")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        app.dependency_overrides.clear()


class TestTrustTierProgression:
    """Tests for trust tier progression logic"""
    
    def test_trust_tier_first_review(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run,
        test_results
    ):
        """Test trust tier updates to 'reviewed' after first review"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_moderator] = override_auth
        
        # First review
        response = client.post(
            "/api/moderator/reviews",
            json={
                "test_id": str(completed_test_run.id),
                "verdict_reviews": [],
                "overall_assessment": "verified"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["trust_tier"] == "reviewed"
        
        app.dependency_overrides.clear()
    
    def test_trust_tier_validated_after_three_reviews(
        self,
        client,
        db_session,
        completed_test_run,
        test_results
    ):
        """Test trust tier updates to 'validated' after three reviews"""
        from main import app
        from app.core.auth import get_current_user, require_moderator
        
        # Create three different moderators
        moderators = []
        for i in range(3):
            mod = User(
                auth0_id=f"mod_{i}_auth0",
                email=f"mod{i}@example.com",
                name=f"Moderator {i}",
                role="moderator"
            )
            db_session.add(mod)
            moderators.append(mod)
        db_session.commit()
        
        for i, mod in enumerate(moderators):
            async def make_override(m=mod):
                return m
            
            app.dependency_overrides[get_current_user] = make_override
            app.dependency_overrides[require_moderator] = make_override
            
            response = client.post(
                "/api/moderator/reviews",
                json={
                    "test_id": str(completed_test_run.id),
                    "verdict_reviews": [],
                    "overall_assessment": "verified"
                }
            )
            
            assert response.status_code == 200
        
        # After third review, should be validated
        data = response.json()
        assert data["trust_tier"] == "validated"
        
        app.dependency_overrides.clear()
