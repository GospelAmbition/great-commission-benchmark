"""Shared test fixtures for pytest"""
import pytest
import uuid
import os
from typing import Generator, Callable
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, event, TypeDecorator, String
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from httpx import AsyncClient


# Custom UUID type that works with SQLite
class UUIDType(TypeDecorator):
    """Platform-independent UUID type."""
    impl = String(36)
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(value))
        return value
    
    def process_result_value(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(value)
        return value


# Patch the PostgreSQL UUID and JSONB to use our custom types for SQLite
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import JSON, Text
_original_uuid = pg.UUID
_original_jsonb = pg.JSONB

class SQLiteCompatibleUUID(UUIDType):
    """UUID type that can be used with SQLite."""
    cache_ok = True
    
    def __init__(self, as_uuid=True, *args, **kwargs):
        self.as_uuid = as_uuid
        super().__init__()
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(_original_uuid(as_uuid=self.as_uuid))
        else:
            return dialect.type_descriptor(String(36))


class SQLiteCompatibleJSONB(TypeDecorator):
    """JSONB type that can be used with SQLite."""
    impl = Text
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        super().__init__()
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(_original_jsonb())
        else:
            return dialect.type_descriptor(JSON())
    
    def process_bind_param(self, value, dialect):
        if dialect.name != 'postgresql' and value is not None:
            import json
            return json.dumps(value)
        return value
    
    def process_result_value(self, value, dialect):
        if dialect.name != 'postgresql' and value is not None:
            if isinstance(value, str):
                import json
                return json.loads(value)
        return value


# Apply the patches before importing models
pg.UUID = SQLiteCompatibleUUID
pg.JSONB = SQLiteCompatibleJSONB


# Now import the app modules
from app.db.base import Base
from app.db.models.user import User
from app.db.models.model import Model
from app.db.models.question_set import QuestionSet
from app.db.models.question import Question
from app.db.models.methodology_version import MethodologyVersion
from app.db.models.test_run import TestRun
from app.db.models.result import Result
from app.db.models.moderation_log import ModerationLog
from app.db.models.community_submission import CommunitySubmission


# Test database engine (SQLite in-memory)
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    """Create test client with overridden database"""
    from main import app
    from app.core.auth import get_db
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    test_client = TestClient(app)
    yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> Callable:
    """Generate auth headers for a given user"""
    def _make_headers(user: User) -> dict:
        # Create a mock JWT token
        # In tests, we'll mock the auth to bypass JWT validation
        return {"Authorization": f"Bearer test_token_{user.id}"}
    return _make_headers


@pytest.fixture
def mock_auth():
    """Mock authentication to return a specific user"""
    def _mock_auth_for_user(user: User):
        async def mock_get_current_user():
            return user
        return mock_get_current_user
    return _mock_auth_for_user


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user with 'user' role"""
    user = User(
        auth0_id="test_user_auth0",
        email="testuser@example.com",
        name="Test User",
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def moderator_user(db_session: Session) -> User:
    """Create a test user with 'moderator' role"""
    user = User(
        auth0_id="moderator_auth0",
        email="moderator@example.com",
        name="Test Moderator",
        role="moderator"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create a test user with 'admin' role"""
    user = User(
        auth0_id="admin_auth0",
        email="admin@example.com",
        name="Test Admin",
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_model(db_session: Session) -> Model:
    """Create a test model"""
    model = Model(
        model_id="test-provider/test-model",
        name="Test Model",
        provider="test-provider",
        is_active=True
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    return model


@pytest.fixture
def test_question_set(db_session: Session) -> QuestionSet:
    """Create a test question set"""
    question_set = QuestionSet(
        semantic_version="1.0.0",
        marketing_version="Version 1.0",
        status="active"
    )
    db_session.add(question_set)
    db_session.commit()
    db_session.refresh(question_set)
    return question_set


@pytest.fixture
def test_methodology_version(db_session: Session, test_question_set: QuestionSet) -> MethodologyVersion:
    """Create a test methodology version"""
    methodology = MethodologyVersion(
        question_set_id=test_question_set.id
    )
    db_session.add(methodology)
    db_session.commit()
    db_session.refresh(methodology)
    return methodology


@pytest.fixture
def test_questions(db_session: Session, test_question_set: QuestionSet) -> list:
    """Create test questions across all tiers"""
    questions = []
    
    # Tier 1 questions (70%)
    for i in range(7):
        q = Question(
            question_set_id=test_question_set.id,
            tier=1,
            category="Task",
            content=f"Test tier 1 question {i+1}"
        )
        questions.append(q)
    
    # Tier 2 questions (20%)
    for i in range(2):
        q = Question(
            question_set_id=test_question_set.id,
            tier=2,
            category="Doctrine",
            content=f"Test tier 2 question {i+1}"
        )
        questions.append(q)
    
    # Tier 3 question (10%)
    q = Question(
        question_set_id=test_question_set.id,
        tier=3,
        category="Worldview",
        content="Test tier 3 question"
    )
    questions.append(q)
    
    db_session.add_all(questions)
    db_session.commit()
    
    for q in questions:
        db_session.refresh(q)
    
    return questions


@pytest.fixture
def test_test_run(
    db_session: Session,
    test_user: User,
    test_model: Model,
    test_question_set: QuestionSet,
    test_methodology_version: MethodologyVersion
) -> TestRun:
    """Create a test run"""
    test_run = TestRun(
        user_id=test_user.id,
        model_id=test_model.id,
        question_set_id=test_question_set.id,
        methodology_version_id=test_methodology_version.id,
        status="pending_payment",
        total_cost=20.0
    )
    db_session.add(test_run)
    db_session.commit()
    db_session.refresh(test_run)
    return test_run


@pytest.fixture
def completed_test_run(
    db_session: Session,
    test_user: User,
    test_model: Model,
    test_question_set: QuestionSet,
    test_methodology_version: MethodologyVersion
) -> TestRun:
    """Create a completed test run"""
    test_run = TestRun(
        user_id=test_user.id,
        model_id=test_model.id,
        question_set_id=test_question_set.id,
        methodology_version_id=test_methodology_version.id,
        status="completed",
        trust_tier="automated",
        payment_status="succeeded"
    )
    db_session.add(test_run)
    db_session.commit()
    db_session.refresh(test_run)
    return test_run


@pytest.fixture
def test_results(db_session: Session, completed_test_run: TestRun, test_questions: list) -> list:
    """Create test results for a completed test run"""
    results = []
    for question in test_questions:
        result = Result(
            test_run_id=completed_test_run.id,
            question_id=question.id,
            response="Test response",
            verdict="ACCEPTED",
            reasoning="Test reasoning"
        )
        results.append(result)
    
    db_session.add_all(results)
    db_session.commit()
    
    for r in results:
        db_session.refresh(r)
    
    return results


@pytest.fixture
def mock_stripe():
    """Mock Stripe API calls"""
    with patch("stripe.PaymentIntent") as mock_intent, \
         patch("stripe.Refund") as mock_refund, \
         patch("stripe.Webhook") as mock_webhook:
        
        # Mock PaymentIntent.create
        mock_intent.create.return_value = MagicMock(
            id="pi_test_123",
            client_secret="pi_test_123_secret_456",
            status="requires_payment_method",
            amount=2000,
            currency="usd"
        )
        
        # Mock PaymentIntent.retrieve
        mock_intent.retrieve.return_value = MagicMock(
            id="pi_test_123",
            status="succeeded",
            amount=2000,
            currency="usd",
            metadata={"test_id": "test-123"}
        )
        
        # Mock Refund.create
        mock_refund.create.return_value = MagicMock(
            id="re_test_123",
            amount=2000,
            currency="usd",
            status="succeeded",
            reason="requested_by_customer"
        )
        
        yield {
            "intent": mock_intent,
            "refund": mock_refund,
            "webhook": mock_webhook
        }


@pytest.fixture
def mock_openrouter():
    """Mock OpenRouter API calls"""
    with patch("app.services.openrouter.OpenRouterClient") as mock_client:
        instance = MagicMock()
        
        # Mock get_model_pricing
        instance.get_model_pricing.return_value = {
            "id": "test-model",
            "pricing": {
                "prompt": "0.001",
                "completion": "0.002"
            }
        }
        
        # Mock complete
        instance.complete.return_value = "Test model response"
        
        # Mock close
        instance.close = MagicMock()
        
        mock_client.return_value = instance
        yield instance


@pytest.fixture
def mock_email():
    """Mock email service"""
    with patch("app.services.email.EmailService") as mock_service:
        mock_service.send_email.return_value = True
        mock_service.send_test_completed_email.return_value = True
        mock_service.send_test_failed_email.return_value = True
        mock_service.send_payment_failed_email.return_value = True
        mock_service.send_submission_approved_email.return_value = True
        mock_service.send_submission_rejected_email.return_value = True
        mock_service.send_welcome_email.return_value = True
        yield mock_service
