"""
SQLAlchemy database model for Sprints.
"""

from typing import Any
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class Sprint(Base):
    __tablename__ = "sprints"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Any = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Any = Column(String(100), nullable=False)  # Sprint 1, Sprint 2
    goal: Any = Column(String(1000), nullable=True)
    start_date: Any = Column(DateTime, nullable=True)
    end_date: Any = Column(DateTime, nullable=True)
    status: Any = Column(String(50), default="Planned")  # Planned, Active, Completed
    
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="sprints")
    sprint_tasks = relationship("SprintTask", back_populates="sprint", cascade="all, delete-orphan")
