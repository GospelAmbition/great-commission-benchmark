"""Database base configuration"""
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

logger.info("Initializing database configuration...")

# Connection pool sized for a single uvicorn worker. Overflow exists for
# brief bursts; pool_timeout fails fast so exhausted pools cannot stall
# every in-flight request for the SQLAlchemy default of 30s.
# statement_timeout / lock_timeout keep one slow query from holding a
# checked-out connection indefinitely (Oct 2026 crawler hang: CPU and
# Postgres were idle while workers waited on Redis/pool).
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # Check connections before using them (reconnects if stale)
    pool_recycle=300,     # Recycle connections after 5 minutes
    pool_size=5,
    max_overflow=10,
    pool_timeout=5,
    connect_args={
        "connect_timeout": 5,
        "options": "-c statement_timeout=15000 -c lock_timeout=5000",
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

logger.info("Database configuration complete (engine created, no connection attempted)")


def get_engine_safe():
    """Get engine for health checks - returns the engine without making a connection.
    
    The actual connection test should be wrapped in a try/except by the caller.
    """
    return engine
