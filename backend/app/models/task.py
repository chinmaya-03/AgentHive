"""
SQLAlchemy database models for Tasks, Task Assignments, and Sprint Tasks mappings.
"""

from typing import Any
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class Task(Base):
    __tablename__ = "tasks"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Any = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Any = Column(String(255), nullable=False)
    description: Any = Column(Text, nullable=True)
    category: Any = Column(String(50), nullable=False)  # Frontend, Backend, Database, Testing, DevOps
    estimated_hours: Any = Column(Integer, default=4)
    difficulty: Any = Column(String(50), default="Medium")  # Easy, Medium, Hard
    status: Any = Column(String(50), default="Todo")  # Todo, In Progress, Done
    
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignments = relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan")
    sprint_associations = relationship("SprintTask", back_populates="task", cascade="all, delete-orphan")


class TaskAssignment(Base):
    __tablename__ = "task_assignments"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id: Any = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    team_member_id: Any = Column(String(36), ForeignKey("team_members.id", ondelete="CASCADE"), nullable=False)
    assigned_at: Any = Column(DateTime, default=utcnow, nullable=False)
    reasoning: Any = Column(Text, nullable=True)  # Explains why the AI assigned this developer

    # Relationships
    task = relationship("Task", back_populates="assignments")
    team_member = relationship("TeamMember", back_populates="task_assignments")


class SprintTask(Base):
    __tablename__ = "sprint_tasks"

    sprint_id: Any = Column(String(36), ForeignKey("sprints.id", ondelete="CASCADE"), primary_key=True)
    task_id: Any = Column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    
    created_at: Any = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    sprint = relationship("Sprint", back_populates="sprint_tasks")
    task = relationship("Task", back_populates="sprint_associations")
