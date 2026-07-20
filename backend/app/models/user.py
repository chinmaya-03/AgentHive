"""
SQLAlchemy database model for platform Users.
"""

from typing import Any
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class User(Base):
    __tablename__ = "users"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Any = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Any = Column(String(255), nullable=False)
    name: Any = Column(String(255), nullable=False)
    role: Any = Column(String(50), default="pm")  # pm, admin
    
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
