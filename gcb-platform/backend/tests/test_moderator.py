"""Tests for moderator endpoints"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.db.models.user import User
from app.db.models.test_run import TestRun
from app.db.models.model import Model
from app.db.models.result import Result

client = TestClient(app)


@pytest.fixture
def moderator_user(db_session):
    """Create moderator user"""
    user = User(
        auth0_id="moderator_auth0_id",
        email="moderator@example.com",
        name="Moderator",
        role="moderator"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def completed_test_run(db_session, moderator_user):
    """Create completed test run"""
    from app.db.models.question_set import QuestionSet
    from app.db.models.methodology_version import MethodologyVersion
    
    model = Model(model_id="test-model", name="Test Model", provider="test")
    db_session.add(model)
    db_session.flush()
    
    question_set = QuestionSet(semantic_version="1.0.0", status="active")
    db_session.add(question_set)
    db_session.flush()
    
    methodology_version = MethodologyVersion(question_set_id=question_set.id)
    db_session.add(methodology_version)
    db_session.flush()
    
    test_run = TestRun(
        user_id=moderator_user.id,
        model_id=model.id,
        question_set_id=question_set.id,
        methodology_version_id=methodology_version.id,
        status="completed",
        trust_tier="automated"
    )
    db_session.add(test_run)
    db_session.commit()
    db_session.refresh(test_run)
    return test_run


def test_get_moderation_queue(moderator_user, completed_test_run, auth_headers):
    """Test getting moderation queue"""
    response = client.get(
        "/api/v1/moderator/queue",
        headers=auth_headers(moderator_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_get_queue_item_detail(moderator_user, completed_test_run, auth_headers):
    """Test getting queue item detail"""
    response = client.get(
        f"/api/v1/moderator/queue/{completed_test_run.id}",
        headers=auth_headers(moderator_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "test_id" in data
    assert "sample_verdicts" in data


def test_submit_review(moderator_user, completed_test_run, auth_headers, db_session):
    """Test submitting a review"""
    # Create a sample result
    from app.db.models.question import Question
    question = Question(
        question_set_id=completed_test_run.question_set_id,
        tier=1,
        category="test",
        content="Test question"
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    
    result = Result(
        test_run_id=completed_test_run.id,
        question_id=question.id,
        verdict="ACCEPTED",
        response="Test response"
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(result)
    
    response = client.post(
        "/api/v1/moderator/reviews",
        json={
            "test_id": str(completed_test_run.id),
            "verdict_reviews": [
                {
                    "result_id": str(result.id),
                    "verdict": "agree"
                }
            ],
            "overall_assessment": "verified"
        },
        headers=auth_headers(moderator_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "review_id" in data
    assert "trust_tier" in data


def test_get_moderator_stats(moderator_user, auth_headers):
    """Test getting moderator stats"""
    response = client.get(
        "/api/v1/moderator/stats",
        headers=auth_headers(moderator_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "personal" in data
    assert "system_wide" in data


def test_moderator_requires_role(db_session):
    """Test that moderator endpoints require moderator role"""
    regular_user = User(
        auth0_id="regular_user",
        email="user@example.com",
        role="user"
    )
    db_session.add(regular_user)
    db_session.commit()
    
    response = client.get(
        "/api/v1/moderator/queue",
        headers=auth_headers(regular_user)
    )
    
    assert response.status_code == 403
