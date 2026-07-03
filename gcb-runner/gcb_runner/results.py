"""Results storage using SQLite."""

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from gcb_runner.config import get_data_dir

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


# Run validity classifications (see VALIDITY_* constants).
#
# These describe whether the run faithfully captured model behavior, NOT
# whether the model scored well. A VALID run may include legitimate REFUSED
# answers; an INVALID run contains at least one question where we could not
# trust what we captured (Class B extraction, unknown response shape, etc.)
# and MUST NOT be uploaded to the leaderboard without an explicit override.
VALIDITY_PENDING = "PENDING"
VALIDITY_COMPLETE_VALID = "COMPLETE_VALID"
VALIDITY_COMPLETE_INVALID = "COMPLETE_INVALID"

# Sentinel verdict for a question where extraction failed (Class B). This
# verdict is EXCLUDED from all scoring aggregations so it cannot be mistaken
# for a model refusal. The runner records it with a machine-readable
# response_text marker and the full extraction metadata.
TEST_ERROR_VERDICT = "TEST_ERROR"
TEST_ERROR_MARKER_PREFIX = "[GCB_EXTRACTION_FAILURE:"
JUDGE_TIMEOUT_OUTCOME = "JUDGE_TIMEOUT"
JUDGE_ERROR_OUTCOME = "JUDGE_ERROR"


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
    is_draft_test: Mapped[bool] = mapped_column(default=False)
    validity: Mapped[str] = mapped_column(String(32), default=VALIDITY_PENDING)
    extraction_error_count: Mapped[int] = mapped_column(default=0)
    validity_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    # response_text remains NOT NULL on purpose: every row must carry a
    # human-readable string. For Class B extractions we write an explicit
    # machine-readable marker (see TEST_ERROR_MARKER_PREFIX), never null,
    # never an empty string masquerading as an answer.
    response_text: Mapped[str] = mapped_column(Text)
    # verdict may be ACCEPTED / COMPROMISED / REFUSED for real model
    # answers, or TEST_ERROR for Class B extractions. TEST_ERROR rows are
    # excluded from all scoring.
    verdict: Mapped[str] = mapped_column(String(32))
    verdict_normalized: Mapped[str] = mapped_column(String(16))
    judge_reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    thought_process: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(nullable=True)
    # Structured extraction metadata. Populated for every row so operators
    # can audit which field we treated as the model answer.
    extraction_outcome: Mapped[str | None] = mapped_column(String(64), nullable=True)
    extraction_sources: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    finish_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_message_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    repaired_at: Mapped[datetime | None] = mapped_column(nullable=True)
    repair_attempts: Mapped[int] = mapped_column(default=0)
    repair_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    repair_original_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)

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
            result = conn.execute(text("PRAGMA table_info(test_runs)"))
            columns = [row[1] for row in result.fetchall()]

            if "is_draft_test" not in columns:
                conn.execute(text(
                    "ALTER TABLE test_runs ADD COLUMN is_draft_test BOOLEAN NOT NULL DEFAULT 0"
                ))
                conn.commit()

            if "judge_backend" not in columns:
                conn.execute(text(
                    "ALTER TABLE test_runs ADD COLUMN judge_backend VARCHAR(64)"
                ))
                conn.commit()

            if "validity" not in columns:
                conn.execute(text(
                    "ALTER TABLE test_runs ADD COLUMN validity VARCHAR(32) "
                    f"NOT NULL DEFAULT '{VALIDITY_PENDING}'"
                ))
                conn.commit()

            if "extraction_error_count" not in columns:
                conn.execute(text(
                    "ALTER TABLE test_runs ADD COLUMN extraction_error_count INTEGER NOT NULL DEFAULT 0"
                ))
                conn.commit()

            if "validity_reason" not in columns:
                conn.execute(text(
                    "ALTER TABLE test_runs ADD COLUMN validity_reason TEXT"
                ))
                conn.commit()

            result_responses = conn.execute(text("PRAGMA table_info(responses)"))
            response_columns = [row[1] for row in result_responses.fetchall()]

            if "thought_process" not in response_columns:
                conn.execute(text(
                    "ALTER TABLE responses ADD COLUMN thought_process TEXT"
                ))
                conn.commit()

            for col, ddl in [
                ("extraction_outcome", "ALTER TABLE responses ADD COLUMN extraction_outcome VARCHAR(64)"),
                ("extraction_sources", "ALTER TABLE responses ADD COLUMN extraction_sources TEXT"),
                ("extraction_provider", "ALTER TABLE responses ADD COLUMN extraction_provider VARCHAR(64)"),
                ("finish_reason", "ALTER TABLE responses ADD COLUMN finish_reason VARCHAR(64)"),
                ("raw_message_summary", "ALTER TABLE responses ADD COLUMN raw_message_summary TEXT"),
                ("repaired_at", "ALTER TABLE responses ADD COLUMN repaired_at DATETIME"),
                ("repair_attempts", "ALTER TABLE responses ADD COLUMN repair_attempts INTEGER NOT NULL DEFAULT 0"),
                ("repair_reason", "ALTER TABLE responses ADD COLUMN repair_reason TEXT"),
                ("repair_original_snapshot", "ALTER TABLE responses ADD COLUMN repair_original_snapshot TEXT"),
            ]:
                if col not in response_columns:
                    conn.execute(text(ddl))
                    conn.commit()

    @staticmethod
    def _verdict_normalized(verdict: str) -> str:
        verdict_map = {
            "ACCEPTED": "pass",
            "COMPROMISED": "partial",
            "REFUSED": "fail",
            TEST_ERROR_VERDICT: "test_error",
        }
        return verdict_map.get(verdict.upper(), "fail")

    @staticmethod
    def _encode_sources(extraction_sources: list[str] | None) -> str | None:
        if extraction_sources is None:
            return None
        try:
            return json.dumps(extraction_sources)
        except Exception:
            return str(extraction_sources)

    @staticmethod
    def response_snapshot(response: Response) -> dict[str, Any]:
        """Return a JSON-serializable audit snapshot of a response row."""
        return {
            "id": response.id,
            "test_run_id": response.test_run_id,
            "question_id": response.question_id,
            "tier": response.tier,
            "category": response.category,
            "response_text": response.response_text,
            "verdict": response.verdict,
            "verdict_normalized": response.verdict_normalized,
            "judge_reasoning": response.judge_reasoning,
            "thought_process": response.thought_process,
            "response_time_ms": response.response_time_ms,
            "extraction_outcome": response.extraction_outcome,
            "extraction_sources": response.extraction_sources,
            "extraction_provider": response.extraction_provider,
            "finish_reason": response.finish_reason,
            "raw_message_summary": response.raw_message_summary,
            "repaired_at": response.repaired_at.isoformat() if response.repaired_at else None,
            "repair_attempts": response.repair_attempts,
            "repair_reason": response.repair_reason,
        }
    
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
        extraction_outcome: str | None = None,
        extraction_sources: list[str] | None = None,
        extraction_provider: str | None = None,
        finish_reason: str | None = None,
        raw_message_summary: str | None = None,
    ) -> Response:
        """Add a response to a test run.

        `response_text` is required and MUST be a non-empty string. For Class B
        extractions, callers are expected to pass an explicit marker starting
        with TEST_ERROR_MARKER_PREFIX so nothing in the database can be
        confused with an empty model answer.
        """
        if not isinstance(response_text, str) or response_text == "":
            raise ValueError(
                "response_text must be a non-empty string. "
                "For extraction failures, pass an explicit TEST_ERROR marker."
            )

        verdict_normalized = self._verdict_normalized(verdict)
        sources_json = self._encode_sources(extraction_sources)

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
                extraction_outcome=extraction_outcome,
                extraction_sources=sources_json,
                extraction_provider=extraction_provider,
                finish_reason=finish_reason,
                raw_message_summary=raw_message_summary,
                repair_attempts=0,
            )
            session.add(response)
            session.commit()
            session.refresh(response)
            return response
        finally:
            session.close()

    def replace_response_for_repair(
        self,
        response_id: int,
        *,
        response_text: str,
        verdict: str,
        judge_reasoning: str | None,
        thought_process: str | None,
        response_time_ms: int | None,
        extraction_outcome: str | None,
        extraction_sources: list[str] | None,
        extraction_provider: str | None,
        finish_reason: str | None,
        raw_message_summary: str | None,
        repair_reason: str,
    ) -> Response:
        """Replace a repairable response row and preserve its prior state."""
        if not isinstance(response_text, str) or response_text == "":
            raise ValueError("response_text must be a non-empty string")

        session: Session = self.Session()
        try:
            response = session.query(Response).filter(Response.id == response_id).first()
            if response is None:
                raise ValueError(f"Response #{response_id} not found")

            prior_snapshot = self.response_snapshot(response)
            response.response_text = response_text
            response.verdict = verdict
            response.verdict_normalized = self._verdict_normalized(verdict)
            response.judge_reasoning = judge_reasoning
            response.thought_process = thought_process
            response.response_time_ms = response_time_ms
            response.extraction_outcome = extraction_outcome
            response.extraction_sources = self._encode_sources(extraction_sources)
            response.extraction_provider = extraction_provider
            response.finish_reason = finish_reason
            response.raw_message_summary = raw_message_summary
            response.repaired_at = datetime.now()
            response.repair_attempts = (response.repair_attempts or 0) + 1
            response.repair_reason = repair_reason
            response.repair_original_snapshot = json.dumps(prior_snapshot, sort_keys=True)
            session.commit()
            session.refresh(response)
            return response
        finally:
            session.close()

    def set_validity(
        self,
        run_id: int,
        validity: str,
        extraction_error_count: int,
        reason: str | None = None,
    ) -> None:
        """Record run-level validity. Used to gate uploads."""
        session: Session = self.Session()
        try:
            run = session.query(TestRun).filter(TestRun.id == run_id).first()
            if run:
                run.validity = validity
                run.extraction_error_count = extraction_error_count
                run.validity_reason = reason
                session.commit()
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
