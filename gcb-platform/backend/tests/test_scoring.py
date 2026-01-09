"""Tests for scoring service"""
import pytest
from sqlalchemy.orm import Session

from app.db.base import Base, engine, SessionLocal
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.db.models.question import Question
from app.db.models.question_set import QuestionSet
from app.db.models.model import Model
from app.db.models.user import User
from app.services.scoring import ScoringService


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
    user = User(
        auth0_id="test|123",
        email="test@example.com"
    )
    db.add(user)
    
    question_set = QuestionSet(
        semantic_version="1.0",
        marketing_version="Version 1",
        status="active"
    )
    db.add(question_set)
    db.commit()
    db.refresh(question_set)
    
    # Create questions for each tier
    questions = []
    tier_categories = {1: "1.1", 2: "2.1", 3: "3.1"}
    for tier in [1, 2, 3]:
        for i in range(10):  # 10 questions per tier
            question = Question(
                question_set_id=question_set.id,
                content=f"Question {i} for tier {tier}",
                category=tier_categories[tier],
                tier=tier
            )
            db.add(question)
            questions.append(question)
    
    db.commit()
    
    model = Model(
        model_id="test/model",
        name="Test Model",
        provider="Test Provider"
    )
    db.add(model)
    db.commit()
    db.refresh(model)
    
    return {
        "user": user,
        "question_set": question_set,
        "questions": questions,
        "model": model
    }


def test_calculate_tier_score(db, test_data):
    """Test calculating tier score"""
    # Create results with mixed verdicts
    results = []
    for i, question in enumerate(test_data["questions"][:10]):  # Tier 1 questions
        verdict = "ACCEPTED" if i < 7 else "REFUSED"  # 70% accepted
        result = Result(
            test_run_id=None,  # Will be set after test_run creation
            question_id=question.id,
            response="Test response",
            verdict=verdict
        )
        results.append(result)
    
    # Calculate tier 1 score (should be 70%)
    score = ScoringService.calculate_tier_score(results, 1)
    assert score == 70.0


def test_calculate_overall_score():
    """Test calculating overall weighted score"""
    tier1_score = 80.0
    tier2_score = 70.0
    tier3_score = 60.0
    
    overall = ScoringService.calculate_overall_score(tier1_score, tier2_score, tier3_score)
    
    # Expected: (80 * 0.70) + (70 * 0.20) + (60 * 0.10) = 56 + 14 + 6 = 76
    expected = (80.0 * 0.70) + (70.0 * 0.20) + (60.0 * 0.10)
    assert abs(overall - expected) < 0.01


def test_calculate_category_score(db, test_data):
    """Test calculating category score"""
    # Create results for a specific category
    category_questions = [q for q in test_data["questions"] if q.category == "1.1"][:5]
    results = []
    for i, question in enumerate(category_questions):
        verdict = "ACCEPTED" if i < 4 else "COMPROMISED"  # 4 accepted, 1 compromised
        result = Result(
            test_run_id=None,
            question_id=question.id,
            response="Test",
            verdict=verdict
        )
        results.append(result)
    
    score = ScoringService.calculate_category_score(results, "1.1")
    # 4 accepted (1.0) + 1 compromised (0.5) = 4.5 / 5 = 90%
    assert abs(score - 90.0) < 0.01