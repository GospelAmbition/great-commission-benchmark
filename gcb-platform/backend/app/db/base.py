"""Database base configuration"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional

from app.core.config import settings

# Create engine with connection pooling
# Using shorter timeout to fail fast during healthchecks
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections after 5 minutes
    connect_args={"connect_timeout": 5}  # 5 second connection timeout (reduced from 10)
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_engine_safe():
    """Get engine for health checks - returns the engine without making a connection.
    
    The actual connection test should be wrapped in a try/except by the caller.
    """
    return engine
