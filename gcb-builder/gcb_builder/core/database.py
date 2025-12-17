"""
Database connection and session management for GCB Builder.

This module provides:
- Database initialization
- Session management via context manager
- Path configuration for the SQLite database
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from gcb_builder.core.models import Base

# Default database location
DEFAULT_DB_DIR = Path(__file__).parent.parent.parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "gcb_builder.db"


def get_database_path() -> Path:
    """
    Get the path to the database file.
    
    Can be overridden with the GCB_BUILDER_DB environment variable.
    """
    env_path = os.environ.get("GCB_BUILDER_DB")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


def get_database_url() -> str:
    """Get the SQLAlchemy database URL."""
    db_path = get_database_path()
    return f"sqlite:///{db_path}"


# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign keys for SQLite connections."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Global engine and session factory (lazily initialized)
_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_engine() -> Engine:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        db_url = get_database_url()
        _engine = create_engine(
            db_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False},  # SQLite specific
        )
    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
    return _SessionLocal


def init_db(reset: bool = False) -> None:
    """
    Initialize the database.
    
    Creates all tables if they don't exist. If reset=True, drops all
    tables first (use with caution!).
    
    Args:
        reset: If True, drop all tables before creating (destructive!)
    """
    # Ensure the data directory exists
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    engine = get_engine()
    
    if reset:
        Base.metadata.drop_all(bind=engine)
    
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Usage:
        with get_db() as db:
            db.add(some_object)
            db.commit()
    
    Automatically handles rollback on exceptions and session cleanup.
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session() -> Session:
    """
    Get a new database session (caller must manage lifecycle).
    
    For most use cases, prefer the get_db() context manager.
    """
    SessionLocal = get_session_factory()
    return SessionLocal()


# Convenience function for testing/scripts
def reset_database() -> None:
    """Reset the database (drops and recreates all tables). USE WITH CAUTION!"""
    init_db(reset=True)
