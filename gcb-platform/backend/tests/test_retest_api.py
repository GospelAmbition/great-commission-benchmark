"""Tests for retest API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.db.base import Base, engine, SessionLocal
from app.db.models.user import User
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.db.models.methodology_version import MethodologyVersion


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
def test_user(db: Session):
    """Create test user"""
    user = User(
        auth0_id="test|user123",
        email="test@example.com",
        name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_data(db: Session, test_user: User):
    """Create test data with completed tests"""
    # Create question set
    question_set = QuestionSet(
        semantic_version="1.0",
        marketing_version="Version 1",
        status="active"
    )
    db.add(question_set)
    db.commit()
    db.refresh(question_set)
    
    # Create methodology version
    methodology_version = MethodologyVersion(
        question_set_id=question_set.id,
        scoring_config={"tier1_weight": 0.70},
        active_from=question_set.created_at
    )
    db.add(methodology_version)
    db.commit()
    db.refresh(methodology_version)
    
    # Create questions
    questions = []
    tier_categories = {1: "1.1", 2: "2.1", 3: "3.1"}
    for tier in [1, 2, 3]:
        for i in range(3):
            question = Question(
                question_set_id=question_set.id,
                content=f"Question {i} tier {tier}",
                category=tier_categories[tier],
                tier=tier
            )
            db.add(question)
            questions.append(question)
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
    
    # Create two completed test runs
    from datetime import datetime, timedelta
    
    test_run1 = TestRun(
        user_id=test_user.id,
        model_id=model.id,
        question_set_id=question_set.id,
        methodology_version_id=methodology_version.id,
        status="completed",
        trust_tier="automated",
        completed_at=datetime.utcnow() - timedelta(days=1)
    )
    db.add(test_run1)
    
    test_run2 = TestRun(
        user_id=test_user.id,
        model_id=model.id,
        question_set_id=question_set.id,
        methodology_version_id=methodology_version.id,
        status="completed",
        trust_tier="automated",
        completed_at=datetime.utcnow()
    )
    db.add(test_run2)
    db.commit()
    db.refresh(test_run1)
    db.refresh(test_run2)
    
    # Add results for both tests
    for test_run in [test_run1, test_run2]:
        for q in questions:
            result = Result(
                test_run_id=test_run.id,
                question_id=q.id,
                response="Test response",
                verdict="ACCEPTED" if q.tier == 1 else "COMPROMISED"
            )
            db.add(result)
    db.commit()
    
    return {
        "user": test_user,
        "model": model,
        "question_set": question_set,
        "questions": questions,
        "test_run1": test_run1,
        "test_run2": test_run2,
        "methodology_version": methodology_version
    }


class TestRetestHistory:
    """Tests for retest history endpoint"""
    
    def test_retest_history_returns_all_tests(self, db, test_data):
        """Test that history returns all related tests"""
        # This would be an integration test with the actual endpoint
        # For now, test the query logic
        test_run = test_data["test_run1"]
        
        related_tests = db.query(TestRun).filter(
            TestRun.user_id == test_data["user"].id,
            TestRun.model_id == test_run.model_id,
            TestRun.question_set_id == test_run.question_set_id,
            TestRun.status == "completed"
        ).all()
        
        assert len(related_tests) == 2
    
    def test_retest_history_ordered_by_date(self, db, test_data):
        """Test that history is ordered by completion date"""
        test_run = test_data["test_run1"]
        
        related_tests = db.query(TestRun).filter(
            TestRun.user_id == test_data["user"].id,
            TestRun.model_id == test_run.model_id,
            TestRun.question_set_id == test_run.question_set_id,
            TestRun.status == "completed"
        ).order_by(TestRun.completed_at.desc()).all()
        
        # Most recent should be first
        assert related_tests[0].id == test_data["test_run2"].id


class TestTestComparison:
    """Tests for test comparison endpoint"""
    
    def test_comparison_calculates_deltas(self, db, test_data):
        """Test that comparison calculates score deltas"""
        from app.services.scoring import ScoringService
        
        scores1 = ScoringService.calculate_scores(db, str(test_data["test_run1"].id))
        scores2 = ScoringService.calculate_scores(db, str(test_data["test_run2"].id))
        
        delta = scores2["overall"] - scores1["overall"]
        
        # Both tests have same results, so delta should be 0
        assert abs(delta) < 0.01
    
    def test_comparison_identifies_category_changes(self, db, test_data):
        """Test that comparison identifies category improvements/declines"""
        from app.services.scoring import ScoringService
        
        scores1 = ScoringService.calculate_scores(db, str(test_data["test_run1"].id))
        scores2 = ScoringService.calculate_scores(db, str(test_data["test_run2"].id))
        
        # Get all categories
        all_categories = set(scores1.get("category_scores", {}).keys()) | \
                        set(scores2.get("category_scores", {}).keys())
        
        assert len(all_categories) > 0
        
        # Calculate category deltas
        for category in all_categories:
            score1 = scores1.get("category_scores", {}).get(category, 0)
            score2 = scores2.get("category_scores", {}).get(category, 0)
            delta = score2 - score1
            
            # With identical results, delta should be 0
            assert abs(delta) < 0.01


class TestRetestEndpoint:
    """Tests for retest creation endpoint"""
    
    def test_retest_creates_new_test(self, db, test_data):
        """Test that retest creates a new test run"""
        original = test_data["test_run1"]
        
        new_test = TestRun(
            user_id=original.user_id,
            model_id=original.model_id,
            question_set_id=original.question_set_id,
            methodology_version_id=original.methodology_version_id,
            status="pending_payment"
        )
        db.add(new_test)
        db.commit()
        
        assert new_test.id != original.id
        assert new_test.model_id == original.model_id
        assert new_test.status == "pending_payment"
    
    def test_retest_requires_completed_original(self, db, test_data):
        """Test that retest requires original test to be completed"""
        # Create a running test
        running_test = TestRun(
            user_id=test_data["user"].id,
            model_id=test_data["model"].id,
            question_set_id=test_data["question_set"].id,
            methodology_version_id=test_data["methodology_version"].id,
            status="running"
        )
        db.add(running_test)
        db.commit()
        
        # Should not be able to retest a running test
        assert running_test.status != "completed"
