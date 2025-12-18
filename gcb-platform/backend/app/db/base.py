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

# Create engine with connection pooling
# Using shorter timeout to fail fast during healthchecks
# Disable pool_pre_ping to prevent connection attempts at startup
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=False,  # Disabled to prevent startup connection attempts
    pool_recycle=300,     # Recycle connections after 5 minutes
    pool_size=5,          # Smaller pool size
    max_overflow=10,      # Allow some overflow
    connect_args={"connect_timeout": 3}  # 3 second connection timeout (reduced from 5)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

logger.info("Database configuration complete (engine created, no connection attempted)")


def get_engine_safe():
    """Get engine for health checks - returns the engine without making a connection.
    
    The actual connection test should be wrapped in a try/except by the caller.
    """
    return engine
