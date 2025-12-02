#!/usr/bin/env python3
"""
Setup script for Benchmark V2 Pipeline.

Creates folder structure, initializes database, and creates sample files.
"""

import os
from pathlib import Path
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    DateTime,
    Integer,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import uuid


# ============================================================================
# Database Models
# ============================================================================

class Base(DeclarativeBase):
    """Base class for all models."""
    pass


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


class Question(Base):
    """Individual test prompt."""
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    text = Column(Text, nullable=False)
    acceptance_level = Column(String(50), nullable=False)  # green/orange/red
    prompt_type = Column(String(50), nullable=False, default="direct")  # direct/roleplay/encoded
    tags = Column(Text, default="[]")  # JSON array
    notes = Column(Text, nullable=True)
    source_file = Column(String(255), nullable=True)  # Which CSV it came from
    created_at = Column(DateTime, default=datetime.utcnow)

    responses = relationship("Response", back_populates="question")


class Model(Base):
    """LLM model to test."""
    __tablename__ = "models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_id = Column(String(255), nullable=False, unique=True)  # e.g., "qwen/qwen3-30b"
    created_at = Column(DateTime, default=datetime.utcnow)

    responses = relationship("Response", back_populates="model")


class Response(Base):
    """Raw LLM output for a question."""
    __tablename__ = "responses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    model_id = Column(String(36), ForeignKey("models.id"), nullable=False)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
    response_text = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    error = Column(Text, nullable=True)
    source_file = Column(String(255), nullable=True)  # Which results.json it came from
    created_at = Column(DateTime, default=datetime.utcnow)

    model = relationship("Model", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    evaluations = relationship("Evaluation", back_populates="response")


class EvaluationRun(Base):
    """Tracks each evaluation pass."""
    __tablename__ = "evaluation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)  # The evaluation prompt used
    evaluator_model = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluations = relationship("Evaluation", back_populates="evaluation_run")


class Evaluation(Base):
    """Judgment result for a response."""
    __tablename__ = "evaluations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    response_id = Column(String(36), ForeignKey("responses.id"), nullable=False)
    evaluation_run_id = Column(String(36), ForeignKey("evaluation_runs.id"), nullable=False)
    verdict = Column(String(100), nullable=False)  # Free-form verdict
    reasoning = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    response = relationship("Response", back_populates="evaluations")
    evaluation_run = relationship("EvaluationRun", back_populates="evaluations")


# ============================================================================
# Setup Functions
# ============================================================================

def get_base_dir() -> Path:
    """Get the base directory (where this script is located)."""
    return Path(__file__).parent


def create_folders():
    """Create the required folder structure."""
    base = get_base_dir()
    folders = ["questions", "model-list", "promptfoo", "output"]
    
    for folder in folders:
        folder_path = base / folder
        folder_path.mkdir(exist_ok=True)
        print(f"✓ Created folder: {folder}/")


def create_database():
    """Initialize the SQLite database with schema."""
    base = get_base_dir()
    db_path = base / "output" / "experiment.db"
    
    # Remove existing database if present
    if db_path.exists():
        db_path.unlink()
        print(f"✓ Removed existing database")
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    print(f"✓ Created database: output/experiment.db")
    print(f"  Tables: questions, models, responses, evaluation_runs, evaluations")


def create_sample_files():
    """Create sample model-list.csv."""
    base = get_base_dir()
    
    # Sample model-list.csv
    model_list_path = base / "model-list" / "model-list.csv"
    if not model_list_path.exists():
        model_list_path.write_text("model_id\nqwen/qwen3-30b\n")
        print(f"✓ Created sample: model-list/model-list.csv")
    else:
        print(f"  Skipped: model-list/model-list.csv (already exists)")


def main():
    """Run the setup process."""
    print("=" * 50)
    print("Benchmark V2 Pipeline Setup")
    print("=" * 50)
    print()
    
    create_folders()
    create_database()
    create_sample_files()
    
    print()
    print("=" * 50)
    print("Setup complete!")
    print()
    print("Next steps:")
    print("1. Add question CSV files to questions/")
    print("2. Edit model-list/model-list.csv with your models")
    print("3. Run: python build_foo.py")
    print("=" * 50)


if __name__ == "__main__":
    main()



