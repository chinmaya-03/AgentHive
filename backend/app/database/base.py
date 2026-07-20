from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def utcnow() -> datetime:
    """Return a timezone-naive UTC datetime representing the current time."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
