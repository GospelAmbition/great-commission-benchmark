#!/usr/bin/env python3
"""
Setup script for Benchmark V2 Pipeline.

Installs requirements, creates folder structure, initializes database, and creates sample files.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Import SQLAlchemy components (lazy import to handle missing dependencies during setup)
try:
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
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    # Create dummy classes for when SQLAlchemy is not available
    class DeclarativeBase:
        pass
    class Column:
        pass
    class String:
        pass
    class Text:
        pass
    class DateTime:
        pass
    class Integer:
        pass
    class Float:
        pass
    class ForeignKey:
        pass
    def relationship(*args, **kwargs):
        pass


# Define models at module level so they can be imported by other scripts
if SQLALCHEMY_AVAILABLE:
    class Base(DeclarativeBase):
        pass
    
    def generate_uuid() -> str:
        return str(uuid.uuid4())
    
    class Question(Base):
        __tablename__ = "questions"
        id = Column(String(36), primary_key=True, default=generate_uuid)
        text = Column(Text, nullable=False)
        acceptance_level = Column(String(50), nullable=False)
        prompt_type = Column(String(50), nullable=False, default="direct")
        tags = Column(Text, default="[]")
        notes = Column(Text, nullable=True)
        source_file = Column(String(255), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        responses = relationship("Response", back_populates="question")

    class Model(Base):
        __tablename__ = "models"
        id = Column(String(36), primary_key=True, default=generate_uuid)
        model_id = Column(String(255), nullable=False, unique=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        responses = relationship("Response", back_populates="model")

    class Response(Base):
        __tablename__ = "responses"
        id = Column(String(36), primary_key=True, default=generate_uuid)
        model_id = Column(String(36), ForeignKey("models.id"), nullable=False)
        question_id = Column(String(36), ForeignKey("questions.id"), nullable=False)
        response_text = Column(Text, nullable=True)
        latency_ms = Column(Integer, nullable=True)
        token_count = Column(Integer, nullable=True)
        error = Column(Text, nullable=True)
        source_file = Column(String(255), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        model = relationship("Model", back_populates="responses")
        question = relationship("Question", back_populates="responses")
        evaluations = relationship("Evaluation", back_populates="response")

    class EvaluationRun(Base):
        __tablename__ = "evaluation_runs"
        id = Column(String(36), primary_key=True, default=generate_uuid)
        name = Column(String(255), nullable=False)
        prompt = Column(Text, nullable=False)
        evaluator_model = Column(String(255), nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        evaluations = relationship("Evaluation", back_populates="evaluation_run")

    class Evaluation(Base):
        __tablename__ = "evaluations"
        id = Column(String(36), primary_key=True, default=generate_uuid)
        response_id = Column(String(36), ForeignKey("responses.id"), nullable=False)
        evaluation_run_id = Column(String(36), ForeignKey("evaluation_runs.id"), nullable=False)
        verdict = Column(String(100), nullable=False)
        reasoning = Column(Text, nullable=True)
        confidence = Column(Float, nullable=True)
        created_at = Column(DateTime, default=datetime.utcnow)
        response = relationship("Response", back_populates="evaluations")
        evaluation_run = relationship("EvaluationRun", back_populates="evaluations")
else:
    # Dummy classes when SQLAlchemy is not available
    Base = None
    Question = None
    Model = None
    Response = None
    EvaluationRun = None
    Evaluation = None


def get_base_dir() -> Path:
    """Get the base directory (where this script is located)."""
    return Path(__file__).parent


def install_requirements():
    """Install Python dependencies from requirements.txt."""
    base = get_base_dir()
    requirements_path = base / "requirements.txt"
    
    if not requirements_path.exists():
        print("  Warning: requirements.txt not found")
        return False
    
    print("Installing Python dependencies...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_path), "-q"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✓ Installed dependencies from requirements.txt")
            return True
        else:
            print(f"  Warning: pip install failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  Warning: Could not install requirements: {e}")
        return False


def install_promptfoo():
    """Install promptfoo via npx (ensures it's available for 3_run_foo.py)."""
    print("Installing promptfoo...")
    try:
        # Use --yes to auto-accept installation prompt
        result = subprocess.run(
            ["npx", "--yes", "promptfoo@latest", "--version"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            version = result.stdout.strip() if result.stdout else "installed"
            print(f"✓ promptfoo is available ({version})")
            return True
        else:
            print("  Warning: Could not verify promptfoo installation")
            return False
    except FileNotFoundError:
        print("  Warning: npx not found. Please install Node.js and npm.")
        print("    Visit: https://nodejs.org/")
        return False
    except subprocess.TimeoutExpired:
        print("  Warning: promptfoo installation timed out")
        return False
    except Exception as e:
        print(f"  Warning: Could not install promptfoo: {e}")
        return False


def create_folders():
    """Create the required folder structure."""
    base = get_base_dir()
    folders = ["_1_questions", "_2_model-list", "_3_promptfoo", "_4_output"]
    
    for folder in folders:
        folder_path = base / folder
        folder_path.mkdir(exist_ok=True)
        print(f"✓ Created folder: {folder}/")


def create_database():
    """Initialize the SQLite database with schema."""
    if not SQLALCHEMY_AVAILABLE:
        raise ImportError("SQLAlchemy is not available. Please install requirements first.")
    
    # Create database
    base = get_base_dir()
    db_path = base / "_4_output" / "experiment.db"
    
    if db_path.exists():
        db_path.unlink()
        print("✓ Removed existing database")
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    print("✓ Created database: _4_output/experiment.db")
    print("  Tables: questions, models, responses, evaluation_runs, evaluations")


def create_sample_files():
    """Create sample model-list.csv."""
    base = get_base_dir()
    
    model_list_path = base / "_2_model-list" / "model-list.csv"
    if not model_list_path.exists():
        model_list_path.write_text("model_id\nqwen/qwen3-30b\n")
        print("✓ Created sample: _2_model-list/model-list.csv")
    else:
        print("  Skipped: _2_model-list/model-list.csv (already exists)")


def main():
    """Run the setup process."""
    print("=" * 50)
    print("Benchmark V2 Pipeline Setup")
    print("=" * 50)
    print()
    
    # Install requirements first
    install_requirements()
    print()
    
    # Install promptfoo
    install_promptfoo()
    print()
    
    # Create folders (needed before database)
    create_folders()
    
    # Create database (requires sqlalchemy from requirements)
    create_database()
    
    # Create sample files
    create_sample_files()
    
    print()
    print("=" * 50)
    print("Setup complete!")
    print()
    print("Next steps:")
    print("1. Add question CSV files to _1_questions/")
    print("2. Edit _2_model-list/model-list.csv with your models")
    print("3. Run: python 2_build_foo.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
