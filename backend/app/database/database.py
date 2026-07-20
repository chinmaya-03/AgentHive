"""
SQLAlchemy database engine configuration.
Supports SQLite and PostgreSQL connection pools.
"""

from sqlalchemy import create_engine
from app.core.config import settings

# Thread settings for SQLite. Ignored by PostgreSQL.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Initialize declarative database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True  # Detect and recover from stale connections
)
