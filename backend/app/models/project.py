"""
SQLAlchemy database model for Projects.
"""

from typing import Any
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class Project(Base):
    __tablename__ = "projects"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Any = Column(String(255), nullable=False)
    description: Any = Column(String(1000), nullable=True)
    owner_id: Any = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Any = Column(String(50), default="active")  # active, completed, archived
    
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects")
    team_members = relationship("TeamMember", back_populates="project", cascade="all, delete-orphan")
    requirements = relationship("RequirementDocument", back_populates="project", cascade="all, delete-orphan")
    sprints = relationship("Sprint", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    agent_logs = relationship("AgentExecutionLog", back_populates="project", cascade="all, delete-orphan")
    recommendations = relationship("AIRecommendation", back_populates="project", cascade="all, delete-orphan")
