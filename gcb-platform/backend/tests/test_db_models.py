"""Tests for database models"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import User, Model, QuestionSet, Question


@pytest.fixture
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_user_model(db_session):
    """Test User model creation"""
    user = User(
        auth0_id="auth0|123456",
        email="test@example.com",
        name="Test User",
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.auth0_id == "auth0|123456"
    assert user.email == "test@example.com"
    assert user.role == "user"


def test_model_model(db_session):
    """Test Model model creation"""
    model = Model(
        model_id="openai/gpt-4",
        name="GPT-4",
        provider="OpenAI",
        is_active=True
    )
    db_session.add(model)
    db_session.commit()
    
    assert model.id is not None
    assert model.model_id == "openai/gpt-4"
    assert model.name == "GPT-4"


def test_question_set_model(db_session):
    """Test QuestionSet model creation"""
    question_set = QuestionSet(
        semantic_version="1.0",
        marketing_version="Version 1",
        status="active"
    )
    db_session.add(question_set)
    db_session.commit()
    
    assert question_set.id is not None
    assert question_set.semantic_version == "1.0"
    assert question_set.status == "active"


def test_question_model(db_session):
    """Test Question model creation"""
    question_set = QuestionSet(
        semantic_version="1.0",
        marketing_version="Version 1",
        status="active"
    )
    db_session.add(question_set)
    db_session.commit()
    
    question = Question(
        question_set_id=question_set.id,
        content="What is the Great Commission?",
        category="3.1",
        tier=1
    )
    db_session.add(question)
    db_session.commit()
    
    assert question.id is not None
    assert question.content == "What is the Great Commission?"
    assert question.tier == 1
