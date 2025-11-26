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
    foreign,
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


class Verdict(str, Enum):
    """Evaluation verdict for a response."""
    APPROVED = "approved"      # Model provided helpful content
    REFUSED = "refused"        # Model declined the request (hard rejection)
    COMPROMISED = "compromised"  # Model complied but modified/watered down the output away from request
    AMBIGUOUS = "ambiguous"    # Unclear or partial response


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
    # responses relationship configured after Response class is defined

    def get_tags(self) -> List[str]:
        """Get tags as a Python list."""
        return json.loads(self.tags) if self.tags else []

    def set_tags(self, tag_list: List[str]) -> None:
        """Set tags from a Python list."""
        self.tags = json.dumps(tag_list)

    def __repr__(self) -> str:
        return f"<Question {self.id[:8]}... [{self.acceptance_level.value}]>"


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
    """Raw LLM output for a question."""
    __tablename__ = "responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    test_run_id = Column(String(36), ForeignKey("test_runs.id"), nullable=False)
    model_id = Column(String(36), ForeignKey("models.id"), nullable=False)
    question_id = Column(String(36), nullable=True)  # Removed FK constraint for dual-DB support
    # Denormalized question data for permanent record
    question_text = Column(Text, nullable=True)  # Snapshot of question text at time of response
    acceptance_level = Column(SQLEnum(AcceptanceLevel), nullable=True)  # Snapshot of acceptance level
    prompt_type = Column(SQLEnum(PromptType), nullable=True)  # Snapshot of prompt type
    response_text = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (only work when using single database)
    test_run = relationship("TestRun", back_populates="responses")
    model = relationship("Model", back_populates="responses")
    # question relationship configured after all classes are defined
    evaluation = relationship("Evaluation", back_populates="response", uselist=False)
    
    def get_question_text(self) -> str:
        """Get question text from denormalized field or relationship."""
        if self.question_text:
            return self.question_text
        if self.question:
            return self.question.text
        return ""
    
    def get_acceptance_level(self) -> Optional[AcceptanceLevel]:
        """Get acceptance level from denormalized field or relationship."""
        if self.acceptance_level:
            return self.acceptance_level
        if self.question:
            return self.question.acceptance_level
        return None
    
    def get_prompt_type(self) -> Optional[PromptType]:
        """Get prompt type from denormalized field or relationship."""
        if self.prompt_type:
            return self.prompt_type
        if self.question:
            return self.question.prompt_type
        return None

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
# Configure relationships after all classes are defined
# ============================================================================

# Reconfigure relationships that don't have ForeignKey constraints
# This ensures SQLAlchemy can properly resolve the join conditions
Question.responses = relationship(
    "Response",
    back_populates="question",
    primaryjoin=Question.id == foreign(Response.question_id)
)
Response.question = relationship(
    "Question",
    back_populates="responses",
    primaryjoin=foreign(Response.question_id) == Question.id
)


# ============================================================================
# Database Manager
# ============================================================================

class DatabaseManager:
    """Manages database connections and operations.
    
    Uses dual-database mode:
    - Questions DB: Question table
    - Responses DB: Model, TestRun, Response, and Evaluation tables
    """

    def __init__(
        self,
        questions_db_path: str = "questions.db",
        responses_db_path: str = "responses.db",
    ):
        """Initialize the database manager.
        
        Args:
            questions_db_path: Path to questions database
            responses_db_path: Path to responses database
        """
        self.questions_db_path = Path(questions_db_path)
        self.responses_db_path = Path(responses_db_path)
        
        # Questions database: Question
        self.questions_engine = create_engine(f"sqlite:///{self.questions_db_path}", echo=False)
        self.QuestionsSessionLocal = sessionmaker(bind=self.questions_engine)
        
        # Responses database: Model, TestRun, Response, Evaluation
        self.responses_engine = create_engine(f"sqlite:///{self.responses_db_path}", echo=False)
        self.ResponsesSessionLocal = sessionmaker(bind=self.responses_engine)

    def create_tables(self) -> None:
        """Create all tables in both databases."""
        # Create question tables in questions DB
        Question.metadata.create_all(self.questions_engine)
        
        # Create response tables in responses DB
        Model.metadata.create_all(self.responses_engine)
        TestRun.metadata.create_all(self.responses_engine)
        Response.metadata.create_all(self.responses_engine)
        Evaluation.metadata.create_all(self.responses_engine)

    def drop_tables(self) -> None:
        """Drop all tables from both databases."""
        Question.metadata.drop_all(self.questions_engine)
        Model.metadata.drop_all(self.responses_engine)
        TestRun.metadata.drop_all(self.responses_engine)
        Response.metadata.drop_all(self.responses_engine)
        Evaluation.metadata.drop_all(self.responses_engine)

    def get_session(self) -> Session:
        """Get a new database session for the responses database."""
        return self.ResponsesSessionLocal()
    
    def get_questions_session(self) -> Session:
        """Get a new session for the questions database."""
        return self.QuestionsSessionLocal()

    def verify_schema(self) -> tuple[bool, str]:
        """Verify that all expected tables exist in both databases.
        
        Returns:
            Tuple of (success, message)
        """
        from sqlalchemy import inspect
        
        # Expected tables in questions database
        expected_questions_tables = {"questions"}
        
        # Expected tables in responses database
        expected_responses_tables = {"models", "test_runs", "responses", "evaluations"}
        
        # Check questions database
        questions_inspector = inspect(self.questions_engine)
        questions_tables = set(questions_inspector.get_table_names())
        missing_questions = expected_questions_tables - questions_tables
        
        # Check responses database
        responses_inspector = inspect(self.responses_engine)
        responses_tables = set(responses_inspector.get_table_names())
        missing_responses = expected_responses_tables - responses_tables
        
        missing = missing_questions | missing_responses
        if missing:
            return False, f"Missing tables: {', '.join(missing)}"
        
        return True, f"All {len(expected_questions_tables) + len(expected_responses_tables)} tables exist"
    
    def is_initialized(self) -> bool:
        """Check if databases are initialized (tables exist).
        
        Returns:
            True if all required tables exist, False otherwise
        """
        success, _ = self.verify_schema()
        return success

    def get_stats(self) -> dict:
        """Get statistics about the database contents."""
        with self.get_questions_session() as q_session:
            questions_count = q_session.query(Question).count()
            questions_by_level = {
                level.value: q_session.query(Question).filter(
                    Question.acceptance_level == level
                ).count()
                for level in AcceptanceLevel
            }
            questions_by_type = {
                ptype.value: q_session.query(Question).filter(
                    Question.prompt_type == ptype
                ).count()
                for ptype in PromptType
            }
        
        with self.get_session() as r_session:
            models_count = r_session.query(Model).count()
            test_runs_count = r_session.query(TestRun).count()
            responses_count = r_session.query(Response).count()
            evaluations_count = r_session.query(Evaluation).count()
        
        return {
            "questions": questions_count,
            "models": models_count,
            "test_runs": test_runs_count,
            "responses": responses_count,
            "evaluations": evaluations_count,
            "questions_by_level": questions_by_level,
            "questions_by_type": questions_by_type,
        }

    def delete_model(self, model_id: str) -> dict:
        """Delete a model and all its related data (responses and evaluations).
        
        This method performs a cascading delete:
        - Deletes all evaluations for responses from this model
        - Deletes all responses from this model
        - Deletes the model itself
        
        Args:
            model_id: ID of the model to delete
            
        Returns:
            Dictionary with deletion statistics: {
                "model_deleted": bool,
                "responses_deleted": int,
                "evaluations_deleted": int
            }
        """
        with self.get_session() as session:
            # Find the model
            model = session.query(Model).filter(Model.id == model_id).first()
            if not model:
                return {
                    "model_deleted": False,
                    "responses_deleted": 0,
                    "evaluations_deleted": 0,
                    "error": "Model not found"
                }
            
            # Get all responses for this model
            responses = session.query(Response).filter(Response.model_id == model_id).all()
            response_ids = [r.id for r in responses]
            
            # Delete evaluations for these responses
            evaluations_deleted = 0
            if response_ids:
                evaluations = session.query(Evaluation).filter(
                    Evaluation.response_id.in_(response_ids)
                ).all()
                evaluations_deleted = len(evaluations)
                for eval_obj in evaluations:
                    session.delete(eval_obj)
            
            # Delete responses
            responses_deleted = len(responses)
            for response in responses:
                session.delete(response)
            
            # Delete the model
            session.delete(model)
            session.commit()
            
            return {
                "model_deleted": True,
                "responses_deleted": responses_deleted,
                "evaluations_deleted": evaluations_deleted
            }

    def delete_test_run(self, test_run_id: str) -> dict:
        """Delete a test run and all its related data (responses and evaluations).
        
        Args:
            test_run_id: ID of the test run to delete
            
        Returns:
            Dictionary with deletion statistics: {
                "test_run_deleted": bool,
                "responses_deleted": int,
                "evaluations_deleted": int
            }
        """
        with self.get_session() as session:
            # Find the test run
            test_run = session.query(TestRun).filter(TestRun.id == test_run_id).first()
            if not test_run:
                return {
                    "test_run_deleted": False,
                    "responses_deleted": 0,
                    "evaluations_deleted": 0,
                    "error": "Test run not found"
                }
            
            # Get all responses for this test run
            responses = session.query(Response).filter(Response.test_run_id == test_run_id).all()
            response_ids = [r.id for r in responses]
            
            # Delete evaluations for these responses
            evaluations_deleted = 0
            if response_ids:
                evaluations = session.query(Evaluation).filter(
                    Evaluation.response_id.in_(response_ids)
                ).all()
                evaluations_deleted = len(evaluations)
                for eval_obj in evaluations:
                    session.delete(eval_obj)
            
            # Delete responses
            responses_deleted = len(responses)
            for response in responses:
                session.delete(response)
            
            # Delete the test run
            session.delete(test_run)
            session.commit()
            
            return {
                "test_run_deleted": True,
                "responses_deleted": responses_deleted,
                "evaluations_deleted": evaluations_deleted
            }


# ============================================================================
# Convenience Functions
# ============================================================================

def get_db(
    questions_db_path: str = "questions.db",
    responses_db_path: str = "responses.db",
) -> DatabaseManager:
    """Get a database manager instance.
    
    Args:
        questions_db_path: Path to questions database
        responses_db_path: Path to responses database
        
    Returns:
        DatabaseManager instance.
    """
    return DatabaseManager(questions_db_path, responses_db_path)


def init_db(
    questions_db_path: str = "questions.db",
    responses_db_path: str = "responses.db",
) -> DatabaseManager:
    """Initialize both databases with all tables.
    
    Args:
        questions_db_path: Path to questions database
        responses_db_path: Path to responses database
        
    Returns:
        DatabaseManager instance with tables created.
    """
    db = DatabaseManager(questions_db_path, responses_db_path)
    db.create_tables()
    return db


def get_db_from_config(config_path: str = "config.yaml") -> DatabaseManager:
    """Get database manager from config file.
    
    Args:
        config_path: Path to config YAML file
        
    Returns:
        DatabaseManager instance configured from config file
    """
    import yaml
    from pathlib import Path
    
    config_file = Path(config_path)
    if not config_file.exists():
        # Default to standard dual DB paths
        return get_db()
    
    with open(config_file) as f:
        config = yaml.safe_load(f) or {}
    
    db_config = config.get("database", {})
    
    # Get database paths (required)
    questions_db = db_config.get("questions_db", "questions.db")
    responses_db = db_config.get("responses_db", "responses.db")
    
    return get_db(
        questions_db_path=questions_db,
        responses_db_path=responses_db,
    )


if __name__ == "__main__":
    # Quick test
    db = init_db("test_gcb.db")
    success, msg = db.verify_schema()
    print(f"Schema verification: {msg}")
    print(f"Stats: {db.get_stats()}")
    
    # Clean up test database
    Path("test_gcb.db").unlink(missing_ok=True)

