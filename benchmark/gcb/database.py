"""
Database models and utilities for Great Commission Benchmark.

Uses SQLAlchemy ORM with SQLite backend.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    Float,
    ForeignKey,
    Enum as SQLEnum,
    event,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    sessionmaker,
    Session,
)


# ============================================================================
# Enums
# ============================================================================

class AcceptanceLevel(str, Enum):
    """Expected acceptance level for a question."""
    GREEN = "green"    # Should always be accepted
    ORANGE = "orange"  # Borderline - sometimes accepted, sometimes refused
    RED = "red"        # Should always be refused


class PromptType(str, Enum):
    """Type of prompt strategy used."""
    DIRECT = "direct"          # Straightforward request
    ROLEPLAY = "roleplay"      # Framed as fiction or scenario
    ENCODED = "encoded"        # Indirect or euphemistic language
    MULTI_TURN = "multi_turn"  # Escalation sequence


class Verdict(str, Enum):
    """Evaluation verdict for a response."""
    APPROVED = "approved"    # Model provided helpful content
    REFUSED = "refused"      # Model declined the request
    AMBIGUOUS = "ambiguous"  # Unclear or partial response


class TestRunStatus(str, Enum):
    """Status of a test run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================================================
# Base Model
# ============================================================================

class Base(DeclarativeBase):
    """Base class for all models."""
    pass


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


# ============================================================================
# Models
# ============================================================================

class Question(Base):
    """Individual test prompt."""
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    text = Column(Text, nullable=False)
    acceptance_level = Column(SQLEnum(AcceptanceLevel), nullable=False)
    prompt_type = Column(SQLEnum(PromptType), nullable=False, default=PromptType.DIRECT)
    tags = Column(Text, default="[]")  # JSON array
    parent_id = Column(String(36), ForeignKey("questions.id"), nullable=True)
    sequence_order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Question", remote_side=[id], backref="children")
    responses = relationship("Response", back_populates="question")

    def get_tags(self) -> List[str]:
        """Get tags as a Python list."""
        return json.loads(self.tags) if self.tags else []

    def set_tags(self, tag_list: List[str]) -> None:
        """Set tags from a Python list."""
        self.tags = json.dumps(tag_list)

    def __repr__(self) -> str:
        return f"<Question {self.id[:8]}... [{self.acceptance_level.value}]>"


class Conversation(Base):
    """Complete multi-turn test case."""
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    acceptance_level = Column(SQLEnum(AcceptanceLevel), nullable=False)
    turns = Column(Text, default="[]")  # JSON array of message objects
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    responses = relationship("Response", back_populates="conversation")

    def get_turns(self) -> List[dict]:
        """Get turns as a Python list."""
        return json.loads(self.turns) if self.turns else []

    def set_turns(self, turn_list: List[dict]) -> None:
        """Set turns from a Python list."""
        self.turns = json.dumps(turn_list)

    def __repr__(self) -> str:
        return f"<Conversation {self.id[:8]}... '{self.name}'>"


class Model(Base):
    """LLM model to test."""
    __tablename__ = "models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=False)  # e.g., "lmstudio", "openrouter"
    api_identifier = Column(String(255), nullable=False)  # e.g., "local-model", "openai/gpt-4"
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    responses = relationship("Response", back_populates="model")

    def __repr__(self) -> str:
        return f"<Model {self.name} ({self.provider})>"


class TestRun(Base):
    """Execution batch for running tests."""
    __tablename__ = "test_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(TestRunStatus), default=TestRunStatus.PENDING)
    config = Column(Text, default="{}")  # JSON config used for this run

    # Relationships
    responses = relationship("Response", back_populates="test_run")

    def get_config(self) -> dict:
        """Get config as a Python dict."""
        return json.loads(self.config) if self.config else {}

    def set_config(self, config_dict: dict) -> None:
        """Set config from a Python dict."""
        self.config = json.dumps(config_dict)

    def __repr__(self) -> str:
        return f"<TestRun {self.id[:8]}... [{self.status.value}]>"


class Response(Base):
    """Raw LLM output for a question or conversation."""
    __tablename__ = "responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    model_id = Column(String(36), ForeignKey("models.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=True)
    response_text = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_run = relationship("TestRun", back_populates="responses")
    model = relationship("Model", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    conversation = relationship("Conversation", back_populates="responses")
    evaluation = relationship("Evaluation", back_populates="response", uselist=False)

    def __repr__(self) -> str:
        return f"<Response {self.id[:8]}... for {self.model_id[:8]}...>"


class Evaluation(Base):
    """Judgment result for a response."""
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    response_id = Column(String(36), ForeignKey("responses.id"), nullable=False, unique=True)
    evaluator_model = Column(String(255), nullable=False)
    verdict = Column(SQLEnum(Verdict), nullable=False)
    reasoning = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    extra_data = Column(Text, default="{}")  # JSON for additional data
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    response = relationship("Response", back_populates="evaluation")

    def get_extra_data(self) -> dict:
        """Get extra data as a Python dict."""
        return json.loads(self.extra_data) if self.extra_data else {}

    def set_extra_data(self, data_dict: dict) -> None:
        """Set extra data from a Python dict."""
        self.extra_data = json.dumps(data_dict)

    def __repr__(self) -> str:
        return f"<Evaluation {self.id[:8]}... [{self.verdict.value}]>"


# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, db_path: str = "gcb.db"):
        """Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = Path(db_path)
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)

    def drop_tables(self) -> None:
        """Drop all tables from the database."""
        Base.metadata.drop_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def verify_schema(self) -> tuple[bool, str]:
        """Verify that all expected tables exist.
        
        Returns:
            Tuple of (success, message)
        """
        expected_tables = {
            "questions", "conversations", "models",
            "test_runs", "responses", "evaluations"
        }
        
        from sqlalchemy import inspect
        inspector = inspect(self.engine)
        existing_tables = set(inspector.get_table_names())
        
        missing = expected_tables - existing_tables
        if missing:
            return False, f"Missing tables: {', '.join(missing)}"
        
        return True, f"All {len(expected_tables)} tables exist"

    def get_stats(self) -> dict:
        """Get statistics about the database contents."""
        with self.get_session() as session:
            return {
                "questions": session.query(Question).count(),
                "conversations": session.query(Conversation).count(),
                "models": session.query(Model).count(),
                "test_runs": session.query(TestRun).count(),
                "responses": session.query(Response).count(),
                "evaluations": session.query(Evaluation).count(),
                "questions_by_level": {
                    level.value: session.query(Question).filter(
                        Question.acceptance_level == level
                    ).count()
                    for level in AcceptanceLevel
                },
                "questions_by_type": {
                    ptype.value: session.query(Question).filter(
                        Question.prompt_type == ptype
                    ).count()
                    for ptype in PromptType
                },
            }


# ============================================================================
# Convenience Functions
# ============================================================================

def get_db(db_path: str = "gcb.db") -> DatabaseManager:
    """Get a database manager instance.
    
    Args:
        db_path: Path to the SQLite database file.
        
    Returns:
        DatabaseManager instance.
    """
    return DatabaseManager(db_path)


def init_db(db_path: str = "gcb.db") -> DatabaseManager:
    """Initialize the database with all tables.
    
    Args:
        db_path: Path to the SQLite database file.
        
    Returns:
        DatabaseManager instance with tables created.
    """
    db = DatabaseManager(db_path)
    db.create_tables()
    return db


if __name__ == "__main__":
    # Quick test
    db = init_db("test_gcb.db")
    success, msg = db.verify_schema()
    print(f"Schema verification: {msg}")
    print(f"Stats: {db.get_stats()}")
    
    # Clean up test database
    Path("test_gcb.db").unlink(missing_ok=True)

