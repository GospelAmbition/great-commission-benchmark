"""Results storage using SQLite."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

from gcb_runner.config import get_data_dir

Base = declarative_base()


class TestRun(Base):
    """A single test run against a model."""
    
    __tablename__ = "test_runs"
    
    id = Column(Integer, primary_key=True)
    model = Column(String(128), nullable=False)
    backend = Column(String(64), nullable=False)
    benchmark_version = Column(String(32), nullable=False)
    judge_model = Column(String(128), nullable=False)
    system_prompt = Column(Text, nullable=True)
    score = Column(Float, nullable=True)
    tier1_score = Column(Float, nullable=True)
    tier2_score = Column(Float, nullable=True)
    tier3_score = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    responses = relationship("Response", back_populates="test_run", cascade="all, delete-orphan")


class Response(Base):
    """A single question response and verdict."""
    
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, ForeignKey("test_runs.id"), nullable=False)
    question_id = Column(String(64), nullable=False)
    tier = Column(Integer, nullable=False)
    category = Column(String(32), nullable=True)
    response_text = Column(Text, nullable=False)
    verdict = Column(String(32), nullable=False)
    verdict_normalized = Column(String(16), nullable=False)  # pass, partial, fail
    judge_reasoning = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    test_run = relationship("TestRun", back_populates="responses")


class ResultsDB:
    """Database interface for test results."""
    
    def __init__(self, db_path: Path | None = None):
        if db_path is None:
            db_path = get_data_dir() / "results.db"
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def create_run(
        self,
        model: str,
        backend: str,
        benchmark_version: str,
        judge_model: str,
    ) -> TestRun:
        """Create a new test run."""
        session = self.Session()
        try:
            run = TestRun(
                model=model,
                backend=backend,
                benchmark_version=benchmark_version,
                judge_model=judge_model,
                started_at=datetime.now(),
            )
            session.add(run)
            session.commit()
            session.refresh(run)
            return run
        finally:
            session.close()
    
    def add_response(
        self,
        run_id: int,
        question_id: str,
        tier: int,
        response_text: str,
        verdict: str,
        verdict_normalized: str,
        category: str | None = None,
        judge_reasoning: str | None = None,
        response_time_ms: int | None = None,
    ) -> Response:
        """Add a response to a test run."""
        session = self.Session()
        try:
            response = Response(
                test_run_id=run_id,
                question_id=question_id,
                tier=tier,
                category=category,
                response_text=response_text,
                verdict=verdict,
                verdict_normalized=verdict_normalized,
                judge_reasoning=judge_reasoning,
                response_time_ms=response_time_ms,
            )
            session.add(response)
            session.commit()
            session.refresh(response)
            return response
        finally:
            session.close()
    
    def complete_run(self, run_id: int, score: float, tier1_score: float, tier2_score: float, tier3_score: float) -> None:
        """Mark a test run as complete with final scores."""
        session = self.Session()
        try:
            run = session.query(TestRun).filter(TestRun.id == run_id).first()
            if run:
                run.score = score
                run.tier1_score = tier1_score
                run.tier2_score = tier2_score
                run.tier3_score = tier3_score
                run.completed_at = datetime.now()
                session.commit()
        finally:
            session.close()
    
    def get_run(self, run_id: int) -> TestRun | None:
        """Get a test run by ID."""
        session = self.Session()
        try:
            return session.query(TestRun).filter(TestRun.id == run_id).first()
        finally:
            session.close()
    
    def list_runs(self, limit: int = 10) -> list[TestRun]:
        """List recent test runs."""
        session = self.Session()
        try:
            return session.query(TestRun).order_by(TestRun.started_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_responses(self, run_id: int) -> list[Response]:
        """Get all responses for a test run."""
        session = self.Session()
        try:
            return session.query(Response).filter(Response.test_run_id == run_id).order_by(Response.tier, Response.id).all()
        finally:
            session.close()
    
    def get_incomplete_run(self, model: str, benchmark_version: str) -> TestRun | None:
        """Get an incomplete run for resuming."""
        session = self.Session()
        try:
            return session.query(TestRun).filter(
                TestRun.model == model,
                TestRun.benchmark_version == benchmark_version,
                TestRun.completed_at.is_(None)
            ).order_by(TestRun.started_at.desc()).first()
        finally:
            session.close()
    
    def get_answered_question_ids(self, run_id: int) -> set[str]:
        """Get the set of question IDs already answered in a run."""
        session = self.Session()
        try:
            responses = session.query(Response.question_id).filter(Response.test_run_id == run_id).all()
            return {r[0] for r in responses}
        finally:
            session.close()
