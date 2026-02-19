"""Tests for public API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.base import Base, engine, SessionLocal
from app.db.models.user import User
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.db.models.methodology_version import MethodologyVersion

client = TestClient(app)


@pytest.fixture
def db():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_data(db: Session):
    """Create test data"""
    # Create question set
    question_set = QuestionSet(
        semantic_version="1.0",
        marketing_version="Version 1",
        status="active"
    )
    db.add(question_set)
    db.commit()
    db.refresh(question_set)
    
    # Create questions - categories match their tier (1.x for T1, 2.x for T2, 3.x for T3)
    tier_categories = {1: ["1.1", "1.2"], 2: ["2.1", "2.2"], 3: ["3.1", "3.2"]}
    for tier in [1, 2, 3]:
        for category in tier_categories[tier]:
            question = Question(
                question_set_id=question_set.id,
                content=f"Test question for tier {tier}, category {category}",
                category=category,
                tier=tier
            )
            db.add(question)
    
    db.commit()
    
    # Create methodology version
    methodology_version = MethodologyVersion(
        question_set_id=question_set.id,
        scoring_config={"tier1_weight": 0.70, "tier2_weight": 0.20, "tier3_weight": 0.10},
        active_from=db.query(QuestionSet).first().created_at
    )
    db.add(methodology_version)
    db.commit()
    
    # Create model
    model = Model(
        model_id="test/model",
        name="Test Model",
        provider="Test Provider",
        is_active=True
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    
    return {
        "question_set": question_set,
        "model": model,
        "methodology_version": methodology_version
    }


def test_get_leaderboard_empty(db, test_data):
    """Test getting empty leaderboard"""
    response = client.get("/api/public/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_models"] == 0
    assert len(data["entries"]) == 0


def test_get_leaderboard_with_data(db, test_data):
    """Test getting leaderboard with test data"""
    # Create a completed test run
    user = User(
        auth0_id="test|123",
        email="test@example.com",
        name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    test_run = TestRun(
        user_id=user.id,
        model_id=test_data["model"].id,
        question_set_id=test_data["question_set"].id,
        methodology_version_id=test_data["methodology_version"].id,
        status="completed",
        trust_tier="automated"
    )
    db.add(test_run)
    db.commit()
    db.refresh(test_run)
    
    # Create some results
    questions = db.query(Question).filter(
        Question.question_set_id == test_data["question_set"].id
    ).all()
    
    for question in questions[:3]:  # Add 3 results
        result = Result(
            test_run_id=test_run.id,
            question_id=question.id,
            response="Test response",
            verdict="ACCEPTED"
        )
        db.add(result)
    
    db.commit()
    db.refresh(test_run)

    # Pre-compute scores so leaderboard includes this test run
    from app.services.scoring import compute_and_store_test_run_scores
    compute_and_store_test_run_scores(db, test_run)
    db.commit()
    
    response = client.get("/api/public/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_models"] >= 1


def test_list_models(db, test_data):
    """Test listing models"""
    response = client.get("/api/public/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "pagination" in data


def test_get_model_detail(db, test_data):
    """Test getting model detail"""
    model_id = test_data["model"].id
    response = client.get(f"/api/public/models/{model_id}")
    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert data["model"]["id"] == str(model_id)


def test_get_versions(db, test_data):
    """Test getting versions"""
    response = client.get("/api/public/versions")
    assert response.status_code == 200
    data = response.json()
    assert "versions" in data
    assert "current_version" in data
    assert len(data["versions"]) > 0


def test_get_stats(db, test_data):
    """Test getting platform stats"""
    response = client.get("/api/public/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_models_tested" in data
    assert "total_test_runs" in data
    assert "current_benchmark_version" in data


def test_compare_models(db, test_data):
    """Test comparing models"""
    model_id = test_data["model"].id
    response = client.get(f"/api/public/leaderboard/compare?models={model_id}")
    # Should work even with one model
    assert response.status_code in [200, 400]  # 400 if validation fails