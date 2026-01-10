"""Results storage using SQLite."""

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from gcb_runner.config import get_data_dir

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class TestRun(Base):
    """A single test run against a model."""
    
    __tablename__ = "test_runs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    model: Mapped[str] = mapped_column(String(128))
    backend: Mapped[str] = mapped_column(String(64))
    benchmark_version: Mapped[str] = mapped_column(String(32))
    judge_model: Mapped[str] = mapped_column(String(128))
    judge_backend: Mapped[str | None] = mapped_column(String(64), nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[float | None] = mapped_column(nullable=True)
    tier1_score: Mapped[float | None] = mapped_column(nullable=True)
    tier2_score: Mapped[float | None] = mapped_column(nullable=True)
    tier3_score: Mapped[float | None] = mapped_column(nullable=True)
    started_at: Mapped[datetime] = mapped_column()
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    is_draft_test: Mapped[bool] = mapped_column(default=False)  # True if testing a draft version
    
    responses: Mapped[list["Response"]] = relationship(
        "Response", back_populates="test_run", cascade="all, delete-orphan"
    )


class Response(Base):
    """A single question response and verdict."""
    
    __tablename__ = "responses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    test_run_id: Mapped[int] = mapped_column(ForeignKey("test_runs.id"))
    question_id: Mapped[str] = mapped_column(String(64))
    tier: Mapped[int] = mapped_column()
    category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    response_text: Mapped[str] = mapped_column(Text)
    verdict: Mapped[str] = mapped_column(String(32))  # ACCEPTED, COMPROMISED, REFUSED
    verdict_normalized: Mapped[str] = mapped_column(String(16))  # pass, partial, fail
    judge_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    thought_process: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(nullable=True)
    
    test_run: Mapped["TestRun"] = relationship("TestRun", back_populates="responses")


class ResultsDB:
    """Database interface for test results."""
    
    def __init__(self, db_path: Path | None = None):
        if db_path is None:
            db_path = get_data_dir() / "results.db"
        
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self._migrate_schema()
        self.Session = sessionmaker(bind=self.engine)
    
    def _migrate_schema(self) -> None:
        """Run schema migrations for existing databases."""
        from sqlalchemy import text
        
        with self.engine.connect() as conn:
            # Check if is_draft_test column exists
            result = conn.execute(text("PRAGMA table_info(test_runs)"))
            columns = [row[1] for row in result.fetchall()]
            
            if "is_draft_test" not in columns:
                # Add the column with default value
                conn.execute(text(
                    "ALTER TABLE test_runs ADD COLUMN is_draft_test BOOLEAN NOT NULL DEFAULT 0"
                ))
                conn.commit()
            
            # Check if judge_backend column exists
            if "judge_backend" not in columns:
                # Add the column (nullable, so no default needed)
                conn.execute(text(
                    "ALTER TABLE test_runs ADD COLUMN judge_backend VARCHAR(64)"
                ))
                conn.commit()
            
            # Check if thought_process column exists in responses table
            result_responses = conn.execute(text("PRAGMA table_info(responses)"))
            response_columns = [row[1] for row in result_responses.fetchall()]
            
            if "thought_process" not in response_columns:
                # Add the column (nullable, so no default needed)
                conn.execute(text(
                    "ALTER TABLE responses ADD COLUMN thought_process TEXT"
                ))
                conn.commit()
    
    def create_run(
        self,
        model: str,
        backend: str,
        benchmark_version: str,
        judge_model: str,
        judge_backend: str | None = None,
        is_draft_test: bool = False,
    ) -> TestRun:
        """Create a new test run.
        
        Args:
            model: Model identifier being tested
            backend: Backend used for the model
            benchmark_version: Benchmark version being tested
            judge_model: Model used for judging
            judge_backend: Backend used for judging (None if auto-detected)
            is_draft_test: True if testing a draft/locked version (won't be published to leaderboard)
        """
        session: Session = self.Session()
        try:
            run = TestRun(
                model=model,
                backend=backend,
                benchmark_version=benchmark_version,
                judge_model=judge_model,
                judge_backend=judge_backend,
                started_at=datetime.now(),
                is_draft_test=is_draft_test,
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
        category: str | None = None,
        judge_reasoning: str | None = None,
        thought_process: str | None = None,
        response_time_ms: int | None = None,
    ) -> Response:
        """Add a response to a test run."""
        # Normalize verdict: ACCEPTED -> pass, COMPROMISED -> partial, REFUSED -> fail
        verdict_map = {
            "ACCEPTED": "pass",
            "COMPROMISED": "partial",
            "REFUSED": "fail",
        }
        verdict_normalized = verdict_map.get(verdict.upper(), "fail")
        
        session: Session = self.Session()
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
                thought_process=thought_process,
                response_time_ms=response_time_ms,
            )
            session.add(response)
            session.commit()
            session.refresh(response)
            return response
        finally:
            session.close()
    
    def complete_run(
        self, run_id: int, score: float, tier1_score: float, tier2_score: float, tier3_score: float
    ) -> None:
        """Mark a test run as complete with final scores."""
        session: Session = self.Session()
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
        session: Session = self.Session()
        try:
            return session.query(TestRun).filter(TestRun.id == run_id).first()
        finally:
            session.close()
    
    def list_runs(self, limit: int = 10) -> list[TestRun]:
        """List recent test runs."""
        session: Session = self.Session()
        try:
            return session.query(TestRun).order_by(TestRun.started_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_responses(self, run_id: int) -> list[Response]:
        """Get all responses for a test run."""
        session: Session = self.Session()
        try:
            return (
                session.query(Response)
                .filter(Response.test_run_id == run_id)
                .order_by(Response.tier, Response.id)
                .all()
            )
        finally:
            session.close()
    
    def get_incomplete_run(self, model: str, benchmark_version: str) -> TestRun | None:
        """Get an incomplete run for resuming."""
        session: Session = self.Session()
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
        session: Session = self.Session()
        try:
            responses = session.query(Response.question_id).filter(Response.test_run_id == run_id).all()
            return {r[0] for r in responses}
        finally:
            session.close()
