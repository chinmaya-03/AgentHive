"""
Database session configurations and dependencies.
Exposes database session maker and yielder dependencies.
"""

from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from app.database.database import engine

# Setup thread-local session maker bound to engine
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding a transactional session and ensuring it is
    properly closed after request execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
