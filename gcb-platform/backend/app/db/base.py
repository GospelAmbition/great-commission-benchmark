"""Database base configuration"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional

from app.core.config import settings

# Create engine with connection pooling and lazy connection
# pool_pre_ping=True will verify connections before using them
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,    # Recycle connections after 5 minutes
    connect_args={"connect_timeout": 10}  # 10 second connection timeout
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
