"""Tests for moderator endpoints"""
import pytest
from uuid import uuid4

from app.db.models.result import Result


def authenticate(user):
    from main import app
    from app.core.auth import get_current_user

    async def override_auth():
        return user

    app.dependency_overrides[get_current_user] = override_auth


class TestModeratorEndpoints:
    """Tests for moderator API endpoints"""
    
    def test_get_moderation_queue(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run
    ):
        """Test GET /api/moderator/automated-runs"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.get("/api/moderator/automated-runs")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert [item["test_run_id"] for item in data["items"]] == [str(completed_test_run.id)]
        
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
        from app.core.auth import get_current_user
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        from datetime import datetime
        completed_test_run.status = "rejected"
        completed_test_run.moderator_reviewed_at = datetime.utcnow()
        db_session.commit()
        response = client.get("/api/moderator/automated-runs?list_type=history&status=rejected")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["test_run_id"] == str(completed_test_run.id)
        assert client.get("/api/moderator/automated-runs?list_type=history&status=completed").json()["total"] == 0
        
        app.dependency_overrides.clear()
    
    def test_get_queue_item_detail(
        self,
        client,
        db_session,
        moderator_user,
        completed_test_run,
        test_results
    ):
        """Test GET /api/moderator/automated-runs/{test_id}"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.get(f"/api/moderator/automated-runs/{completed_test_run.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["test_run_id"] == str(completed_test_run.id)
        assert data["sample_size"] == len(test_results)
        assert {r["question_id"] for r in data["sample_responses"]} == {
            str(r.question_id) for r in test_results
        }
        
        app.dependency_overrides.clear()
    
    def test_get_queue_item_detail_not_found(
        self,
        client,
        db_session,
        moderator_user
    ):
        """Test queue item detail for non-existent test"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.get(f"/api/moderator/automated-runs/{uuid4()}")
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_accept_run_records_review(self, client, db_session, moderator_user,
                                      completed_test_run, test_results):
        """Accepting preserves publication and records the moderator decision."""
        authenticate(moderator_user)
        response = client.post(f"/api/moderator/automated-runs/{completed_test_run.id}/accept")
        assert response.status_code == 200
        assert response.json()["moderator_decision"] == "accepted"
        db_session.refresh(completed_test_run)
        assert completed_test_run.status == "completed"
        assert completed_test_run.trust_tier == "automated"
        assert completed_test_run.moderator_id == moderator_user.id
        assert completed_test_run.moderator_reviewed_at is not None
        assert completed_test_run.moderator_decision == "accepted"
        assert completed_test_run.overall_score is not None
        assert client.get("/api/moderator/automated-runs").json()["total"] == 0
        history = client.get("/api/moderator/automated-runs?list_type=history&status=completed").json()
        assert [item["test_run_id"] for item in history["items"]] == [str(completed_test_run.id)]

    def test_reject_run_preserves_evidence(self, client, db_session, moderator_user,
                                         completed_test_run, test_results):
        """Concerns now reject the run while retaining every response for audit."""
        authenticate(moderator_user)
        response = client.post(f"/api/moderator/automated-runs/{completed_test_run.id}/reject")
        assert response.status_code == 200
        db_session.refresh(completed_test_run)
        assert completed_test_run.status == "rejected"
        assert completed_test_run.moderator_decision == "rejected"
        assert completed_test_run.moderator_id == moderator_user.id
        assert db_session.query(Result).filter_by(test_run_id=completed_test_run.id).count() == len(test_results)
        assert client.get("/api/moderator/automated-runs").json()["total"] == 0
        history = client.get("/api/moderator/automated-runs?list_type=history&status=rejected").json()
        assert history["total"] == 1
        assert history["items"][0]["test_run_id"] == str(completed_test_run.id)

    def test_get_moderator_activity(
        self,
        client,
        db_session,
        moderator_user
    ):
        """Test GET /api/moderator/activity"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
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
        from app.core.auth import get_current_user
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
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
        
        response = client.get("/api/moderator/automated-runs")
        
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
        from app.core.auth import get_current_user
        
        async def override_auth():
            return moderator_user
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.get("/api/moderator/community")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        
        app.dependency_overrides.clear()


class TestAutomatedReviewTransitions:
    """Automated reviews replace the retired multi-review trust-tier workflow."""

    def test_duplicate_accept_rejected(self, client, db_session, moderator_user,
                                       completed_test_run):
        authenticate(moderator_user)
        url = f"/api/moderator/automated-runs/{completed_test_run.id}/accept"
        assert client.post(url).status_code == 200
        db_session.refresh(completed_test_run)
        reviewed_at = completed_test_run.moderator_reviewed_at
        assert client.post(url).status_code == 400
        db_session.refresh(completed_test_run)
        assert completed_test_run.moderator_reviewed_at == reviewed_at
        assert completed_test_run.trust_tier == "automated"

    def test_reject_is_idempotent_and_restore_preserves_review(self, client, db_session,
                                                              moderator_user, completed_test_run):
        authenticate(moderator_user)
        url = f"/api/moderator/automated-runs/{completed_test_run.id}"
        assert client.post(url + "/reject").status_code == 200
        db_session.refresh(completed_test_run)
        reviewed_at = completed_test_run.moderator_reviewed_at
        repeated = client.post(url + "/reject")
        assert repeated.status_code == 200
        assert repeated.json()["already_rejected"] is True
        assert client.post(url + "/restore").status_code == 200
        db_session.refresh(completed_test_run)
        assert completed_test_run.status == "completed"
        assert completed_test_run.moderator_reviewed_at == reviewed_at
        assert completed_test_run.trust_tier == "automated"
        assert f"Restored by {moderator_user.name}" in completed_test_run.admin_notes
        assert client.post(url + "/restore").status_code == 400

    def test_non_automated_run_excluded(self, client, db_session, moderator_user, completed_test_run):
        authenticate(moderator_user)
        completed_test_run.trust_tier = "reviewed"
        db_session.commit()
        assert client.get("/api/moderator/automated-runs").json()["total"] == 0
        url = f"/api/moderator/automated-runs/{completed_test_run.id}"
        assert client.get(url).status_code == 400
        assert client.post(url + "/accept").status_code == 404
        assert client.post(url + "/reject").status_code == 404
