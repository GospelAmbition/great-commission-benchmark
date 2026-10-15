"""Tests for admin endpoints"""
import pytest
from uuid import uuid4

from app.db.models.user import User
from app.db.models.question import Question
from app.db.models.question_set import QuestionSet


class TestAdminUserManagement:
    """Tests for admin user management endpoints"""
    
    def test_list_users(
        self,
        client,
        db_session,
        admin_user,
        test_user
    ):
        """Test GET /api/admin/users"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.get("/api/admin/users")
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["total"] >= 2  # admin_user and test_user
        
        app.dependency_overrides.clear()
    
    def test_list_users_with_search(
        self,
        client,
        db_session,
        admin_user,
        test_user
    ):
        """Test user search by email"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.get("/api/admin/users?search=testuser")
        
        assert response.status_code == 200
        data = response.json()
        # Should find the test user
        assert any("testuser" in u["email"] for u in data["users"])
        
        app.dependency_overrides.clear()
    
    def test_list_users_filter_by_role(
        self,
        client,
        db_session,
        admin_user,
        moderator_user
    ):
        """Test user filtering by role"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.get("/api/admin/users?role=moderator")
        
        assert response.status_code == 200
        data = response.json()
        # All users should have moderator role
        for user in data["users"]:
            assert user["role"] == "moderator"
        
        app.dependency_overrides.clear()
    
    def test_update_user_role(
        self,
        client,
        db_session,
        admin_user,
        test_user
    ):
        """Test PUT /api/admin/users/{user_id}/role"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.put(
            f"/api/admin/users/{test_user.id}/role",
            json={"role": "moderator"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "moderator"
        
        # Verify in database
        db_session.refresh(test_user)
        assert test_user.role == "moderator"
        
        app.dependency_overrides.clear()
    
    def test_update_user_role_invalid_role(
        self,
        client,
        db_session,
        admin_user,
        test_user
    ):
        """Test update with invalid role"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.put(
            f"/api/admin/users/{test_user.id}/role",
            json={"role": "invalid_role"}
        )
        
        assert response.status_code == 400
        
        app.dependency_overrides.clear()
    
    def test_cannot_remove_last_admin(
        self,
        client,
        db_session,
        admin_user
    ):
        """Test that last admin cannot be demoted"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.put(
            f"/api/admin/users/{admin_user.id}/role",
            json={"role": "user"}
        )
        
        assert response.status_code == 400
        assert "last admin" in response.json()["detail"].lower()
        
        app.dependency_overrides.clear()
    
    def test_admin_requires_role(
        self,
        client,
        db_session,
        test_user
    ):
        """Test that admin endpoints require admin role"""
        from main import app
        from app.core.auth import get_current_user
        
        async def override_auth():
            return test_user  # Regular user, not admin
        
        app.dependency_overrides[get_current_user] = override_auth
        
        response = client.get("/api/admin/users")
        
        assert response.status_code == 403
        
        app.dependency_overrides.clear()


class TestAdminQuestionManagement:
    """Tests for admin question management endpoints"""
    
    def test_list_questions(
        self,
        client,
        db_session,
        admin_user,
        test_questions
    ):
        """Test GET /api/admin/questions"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.get("/api/admin/questions")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 10  # 7 tier1 + 2 tier2 + 1 tier3
        
        app.dependency_overrides.clear()
    
    def test_list_questions_filter_by_tier(
        self,
        client,
        db_session,
        admin_user,
        test_questions
    ):
        """Test filtering questions by tier"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.get("/api/admin/questions?tier=1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 7
        for item in data["items"]:
            assert item["tier"] == 1
        
        app.dependency_overrides.clear()
    
    def test_get_question_detail(
        self,
        client,
        db_session,
        admin_user,
        test_questions
    ):
        """Test GET /api/admin/questions/{question_id}"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        question = test_questions[0]
        response = client.get(f"/api/admin/questions/{question.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(question.id)
        assert data["content"] == question.content
        
        app.dependency_overrides.clear()
    
    def test_update_question(
        self,
        client,
        db_session,
        admin_user,
        test_questions
    ):
        """Test PUT /api/admin/questions/{question_id}"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        question = test_questions[0]
        response = client.put(
            f"/api/admin/questions/{question.id}",
            json={
                "content": "Updated question content",
                "category": "Updated Category"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated question content"
        assert data["category"] == "Updated Category"
        
        app.dependency_overrides.clear()
    
    def test_delete_question(
        self,
        client,
        db_session,
        admin_user,
        test_questions
    ):
        """Test DELETE /api/admin/questions/{question_id}"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        question = test_questions[0]
        response = client.delete(f"/api/admin/questions/{question.id}")
        
        assert response.status_code == 200
        
        # Verify deleted
        deleted = db_session.query(Question).filter(Question.id == question.id).first()
        assert deleted is None
        
        app.dependency_overrides.clear()
    
    def test_import_questions_dry_run(
        self,
        client,
        db_session,
        admin_user,
        test_question_set
    ):
        """Test question import with dry run"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.post(
            "/api/admin/questions/import",
            json={
                "questions": [
                    {
                        "question_set_id": str(test_question_set.id),
                        "tier": 1,
                        "category": "Test",
                        "content": "Import test question 1"
                    },
                    {
                        "question_set_id": str(test_question_set.id),
                        "tier": 2,
                        "category": "Test",
                        "content": "Import test question 2"
                    }
                ],
                "dry_run": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 2
        assert data["dry_run"] == True
        assert len(data["errors"]) == 0
        
        app.dependency_overrides.clear()
    
    def test_import_questions_actual(
        self,
        client,
        db_session,
        admin_user,
        test_question_set
    ):
        """Test actual question import"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        initial_count = db_session.query(Question).filter(
            Question.question_set_id == test_question_set.id
        ).count()
        
        response = client.post(
            "/api/admin/questions/import",
            json={
                "questions": [
                    {
                        "question_set_id": str(test_question_set.id),
                        "tier": 1,
                        "category": "Import",
                        "content": "Imported question"
                    }
                ],
                "dry_run": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["imported"] == 1
        
        # Verify in database
        final_count = db_session.query(Question).filter(
            Question.question_set_id == test_question_set.id
        ).count()
        assert final_count == initial_count + 1
        
        app.dependency_overrides.clear()


class TestAdminVersionManagement:
    """Tests for admin version management endpoints"""
    
    def test_create_version_draft(
        self,
        client,
        db_session,
        admin_user,
        test_questions
    ):
        """Test POST /api/admin/versions"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        question_ids = [str(q.id) for q in test_questions]
        original_set_ids = {q.id: q.question_set_id for q in test_questions}
        test_questions[0].question_metadata = {"difficulty": "hard"}
        test_questions[0].notes = "Preserve source context"
        db_session.commit()
        
        response = client.post(
            "/api/admin/versions",
            json={
                "semantic_version": "2.0.0",
                "question_ids": question_ids,
                "description": "Test version 2"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["semantic_version"] == "2.0.0"
        assert data["question_count"] == len(test_questions)
        assert "tier_distribution" in data
        created = db_session.query(QuestionSet).filter_by(semantic_version="2.0.0").one()
        assert created.status == "draft"
        assert created.marketing_version == "Version 2.0.0"
        assert created.notes == "Test version 2"
        copies = db_session.query(Question).filter_by(question_set_id=created.id).all()
        assert len(copies) == len(test_questions)
        assert not {q.id for q in copies}.intersection(original_set_ids)
        for source in test_questions:
            db_session.refresh(source)
            assert source.question_set_id == original_set_ids[source.id]
            copy = next(q for q in copies if q.content == source.content)
            for field in ("category", "tier", "subcategory", "expected_verdict", "question_metadata", "notes"):
                assert getattr(copy, field) == getattr(source, field)
            assert copy.is_locked is False
        
        app.dependency_overrides.clear()
    
    @pytest.mark.parametrize("version,status", [("1.0", 400), ("", 422), ("12345678901", 422)])
    def test_create_version_rejects_duplicate_or_invalid_length(
        self, client, db_session, admin_user, test_question_set, test_questions, version, status
    ):
        from main import app
        from app.core.auth import get_current_user

        async def override_auth():
            return admin_user

        app.dependency_overrides[get_current_user] = override_auth
        original_count = db_session.query(QuestionSet).count()
        question_count = db_session.query(Question).count()
        response = client.post("/api/admin/versions", json={
            "semantic_version": test_question_set.semantic_version if version == "1.0" else version,
            "question_ids": [str(q.id) for q in test_questions],
        })
        assert response.status_code == status
        if status == 400:
            assert "already exists" in response.json()["detail"]
        assert db_session.query(QuestionSet).count() == original_count
        assert db_session.query(Question).count() == question_count
        db_session.refresh(test_question_set)
        assert test_question_set.status == "active"

    def test_publish_version(
        self,
        client,
        db_session,
        admin_user,
        test_question_set
    ):
        """Test PUT /api/admin/versions/{version}/publish"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        # Create a draft version first
        draft_version = QuestionSet(
            semantic_version="3.0.0",
            marketing_version="Version 3.0",
            status="draft"
        )
        db_session.add(draft_version)
        db_session.commit()
        
        response = client.put(
            "/api/admin/versions/3.0.0/publish"
        )
        
        assert response.status_code == 400
        assert "Only locked versions" in response.json()["detail"]
        db_session.refresh(test_question_set)
        assert test_question_set.status == "active"
        draft_version.status = "locked"
        db_session.commit()
        response = client.put("/api/admin/versions/3.0.0/publish")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        db_session.refresh(draft_version)
        assert draft_version.is_publicly_visible is True
        
        # Verify the original test_question_set is now archived
        db_session.refresh(test_question_set)
        assert test_question_set.status == "archived"
        
        app.dependency_overrides.clear()


class TestAdminStats:
    """Tests for admin statistics endpoint"""
    
    def test_get_admin_stats(
        self,
        client,
        db_session,
        admin_user,
        test_user,
        completed_test_run
    ):
        """Test GET /api/admin/stats"""
        from main import app
        from app.core.auth import get_current_user, require_admin
        
        async def override_auth():
            return admin_user
        
        app.dependency_overrides[get_current_user] = override_auth
        app.dependency_overrides[require_admin] = override_auth
        
        response = client.get("/api/admin/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check all stat categories exist
        assert "users" in data
        assert "tests" in data
        assert "revenue" in data
        assert "moderation" in data
        
        # Check user stats
        assert "total" in data["users"]
        assert "new_last_30_days" in data["users"]
        
        # Check test stats
        assert "total" in data["tests"]
        assert "completed" in data["tests"]
        assert "running" in data["tests"]
        
        # Check revenue stats
        assert "total" in data["revenue"]
        assert "last_30_days" in data["revenue"]
        
        # Check moderation stats
        assert "pending_reviews" in data["moderation"]
        assert "total_reviews" in data["moderation"]
        
        app.dependency_overrides.clear()


class TestAdminDescriptionSync:
    @pytest.fixture
    def sync_setup(self, client, db_session, admin_user, monkeypatch):
        from unittest.mock import AsyncMock
        from main import app
        from app.core.auth import get_current_user
        from app.db.models.model import Model
        from app.api.v1.endpoints import admin
        from app.services import published_cache

        async def authenticate():
            return admin_user

        app.dependency_overrides[get_current_user] = authenticate
        for index in range(4):
            db_session.add(Model(model_id=f"test/model-{index}", name=f"Model {index}", provider="Test"))
        db_session.commit()
        sync = AsyncMock(return_value=2)
        clear = AsyncMock()
        monkeypatch.setattr(admin, "sync_all_model_descriptions", sync)
        monkeypatch.setattr(published_cache, "clear_published_caches", clear)
        return sync, clear

    def test_batches_preserve_offsets_and_invalidate_only_changes(self, client, db_session, sync_setup):
        sync, clear = sync_setup
        response = client.post("/api/admin/models/sync-descriptions?all_models=true&offset=0&limit=3")
        assert response.status_code == 200
        assert response.json()["updated_count"] == 2
        assert response.json()["total_models"] == 4
        assert response.json()["next_offset"] == 3
        assert response.json()["remaining_incomplete"] is None
        sync.assert_awaited_once_with(db_session, all_models=True, offset=0, limit=3)
        clear.assert_awaited_once()

        sync.reset_mock()
        sync.return_value = 0
        response = client.post("/api/admin/models/sync-descriptions?offset=3&limit=3")
        assert response.status_code == 200
        assert response.json()["updated_count"] == 0
        assert response.json()["total_models"] == 4
        assert response.json()["next_offset"] is None
        assert response.json()["remaining_incomplete"] == 4
        sync.assert_awaited_once_with(db_session, all_models=False, offset=3, limit=3)
        clear.assert_awaited_once()

    @pytest.mark.parametrize("query", ["limit=11", "limit=0", "offset=-1"])
    def test_rejects_unbounded_or_invalid_batches(self, client, sync_setup, query):
        sync, clear = sync_setup
        assert client.post(f"/api/admin/models/sync-descriptions?{query}").status_code == 422
        sync.assert_not_awaited()
        clear.assert_not_awaited()

    def test_non_admin_cannot_start_sync(self, client, sync_setup, test_user):
        from main import app
        from app.core.auth import get_current_user

        async def authenticate():
            return test_user

        app.dependency_overrides[get_current_user] = authenticate
        assert client.post("/api/admin/models/sync-descriptions").status_code == 403
        sync, clear = sync_setup
        sync.assert_not_awaited()
        clear.assert_not_awaited()


    @pytest.mark.parametrize("descriptions, expected", [
        ([None, " ", "Still abbreviated…", "Complete description."], 3),
        (["Complete description."] * 4, 0),
    ])
    def test_final_batch_reports_remaining_stored_descriptions(self, client, db_session, sync_setup, descriptions, expected):
        from app.db.models.model import Model
        sync, _ = sync_setup
        models = db_session.query(Model).order_by(Model.model_id).all()

        async def apply_batch(*args, **kwargs):
            for model, description in zip(models, descriptions):
                model.description = description
            db_session.commit()
            return 1

        sync.side_effect = apply_batch
        response = client.post("/api/admin/models/sync-descriptions?offset=3&limit=3")
        assert response.status_code == 200
        assert response.json()["remaining_incomplete"] == expected
