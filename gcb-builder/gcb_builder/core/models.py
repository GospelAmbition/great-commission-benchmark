"""
SQLAlchemy database models for GCB Builder.

This module defines all database tables used by the builder:
- Question: Individual benchmark questions with metadata
- BenchmarkVersion: Publishable benchmark versions
- VersionQuestion: Links questions to versions
- JudgeTestCase: Test cases for validating judge prompts
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


class Question(Base):
    """
    A benchmark question with all associated metadata.
    
    Questions go through a lifecycle:
    - draft: Initial creation, can be freely edited/deleted
    - review: Under curation review
    - approved: Approved for inclusion in versions
    - retired: No longer used but preserved for history
    
    Approved questions can be "locked" to protect from accidental deletion
    during bulk operations.
    """
    
    __tablename__ = "questions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Classification
    category: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    tier: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    
    # Expected evaluation outcome
    expected_verdict: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_refusal_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Curation workflow
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Locking (protects approved questions from deletion)
    locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    locked_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Capability vs Willingness testing (Principle 3)
    tests_capability: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    tests_willingness: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Actionable insight metadata (Principle 7)
    # Stored as comma-separated values for SQLite compatibility
    use_case_tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audience_context: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ministry_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    version_links: Mapped[list["VersionQuestion"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    test_cases: Mapped[list["JudgeTestCase"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Question(id={self.id}, category={self.category}, status={self.status})>"
    
    @property
    def use_case_tags_list(self) -> list[str]:
        """Get use_case_tags as a list."""
        if not self.use_case_tags:
            return []
        return [tag.strip() for tag in self.use_case_tags.split(",") if tag.strip()]
    
    @use_case_tags_list.setter
    def use_case_tags_list(self, tags: list[str]) -> None:
        """Set use_case_tags from a list."""
        self.use_case_tags = ",".join(tags) if tags else None
    
    def can_delete(self) -> bool:
        """Check if this question can be deleted."""
        return not self.locked and self.status in ("draft", "review")
    
    def can_edit(self) -> bool:
        """Check if this question can be edited."""
        return not self.locked
    
    def can_lock(self) -> bool:
        """Check if this question can be locked."""
        return self.status == "approved" and not self.locked


class BenchmarkVersion(Base):
    """
    A complete, publishable benchmark version.
    
    Versions go through a lifecycle:
    - building: Questions being assembled
    - validating: Pre-publish validation in progress
    - locked: Finalized, ready for publication
    - published: Released for use
    """
    
    __tablename__ = "benchmark_versions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Version identification
    version: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Lifecycle status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="building")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Integrity
    checksum: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Relationships
    question_links: Mapped[list["VersionQuestion"]] = relationship(
        back_populates="version", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<BenchmarkVersion(version={self.version}, status={self.status})>"
    
    @property
    def question_count(self) -> int:
        """Get the number of questions in this version."""
        return len(self.question_links)
    
    def can_edit(self) -> bool:
        """Check if this version can still be edited."""
        return self.status in ("building", "validating")
    
    def can_publish(self) -> bool:
        """Check if this version can be published."""
        return self.status == "locked"


class VersionQuestion(Base):
    """
    Links questions to a specific benchmark version.
    
    This allows the same question to be included in multiple versions,
    and preserves the order of questions within each version.
    """
    
    __tablename__ = "version_questions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    version_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("benchmark_versions.id"), nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id"), nullable=False
    )
    
    # Order within the version
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Relationships
    version: Mapped["BenchmarkVersion"] = relationship(back_populates="question_links")
    question: Mapped["Question"] = relationship(back_populates="version_links")
    
    # Ensure each question appears only once per version
    __table_args__ = (
        UniqueConstraint("version_id", "question_id", name="uq_version_question"),
    )
    
    def __repr__(self) -> str:
        return f"<VersionQuestion(version_id={self.version_id}, question_id={self.question_id})>"


class JudgeTestCase(Base):
    """
    Known-answer test cases for validating judge prompts.
    
    These are used to measure judge accuracy - given a question and 
    a sample response, the judge should produce the expected verdict.
    Test cases ensure judges maintain ≥90% accuracy before being locked.
    """
    
    __tablename__ = "judge_test_cases"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Link to question (optional - can have standalone test cases)
    question_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("questions.id"), nullable=True
    )
    
    # Test case content
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    sample_response: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Expected judge output
    expected_verdict: Mapped[str] = mapped_column(String(20), nullable=False)
    expected_refusal_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Reasoning for this being the correct answer
    verdict_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Classification
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    
    # Relationships
    question: Mapped[Optional["Question"]] = relationship(back_populates="test_cases")
    
    def __repr__(self) -> str:
        return f"<JudgeTestCase(id={self.id}, expected_verdict={self.expected_verdict})>"


class JudgeTestResult(Base):
    """
    Results from running a judge prompt against test cases.
    
    Tracks accuracy over time and identifies problematic classifications.
    """
    
    __tablename__ = "judge_test_results"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Link to test case
    test_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("judge_test_cases.id"), nullable=False
    )
    
    # What the judge produced
    actual_verdict: Mapped[str] = mapped_column(String(20), nullable=False)
    actual_refusal_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Full judge response for debugging
    judge_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Which judge prompt version was used
    judge_prompt_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Model used for judging
    judge_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Did it match expected?
    verdict_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    refusal_type_correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    
    # Timestamp
    tested_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<JudgeTestResult(id={self.id}, correct={self.verdict_correct})>"
