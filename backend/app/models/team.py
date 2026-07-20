"""
SQLAlchemy database models for Team Members and their associated Skills.
"""

from typing import Any
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class TeamMemberSkill(Base):
    __tablename__ = "team_member_skills"

    team_member_id: Any = Column(String(36), ForeignKey("team_members.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Any = Column(String(36), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    proficiency_level: Any = Column(String(50), default="Mid")  # Junior, Mid, Senior
    
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    team_member = relationship("TeamMember", back_populates="skills_associations")
    skill = relationship("Skill", back_populates="team_member_associations")


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Any = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Any = Column(String(255), nullable=False)
    email: Any = Column(String(255), nullable=False)
    role: Any = Column(String(100), nullable=False)  # Frontend Developer, Backend Developer, QA, etc.
    
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="team_members")
    skills_associations = relationship("TeamMemberSkill", back_populates="team_member", cascade="all, delete-orphan")
    task_assignments = relationship("TaskAssignment", back_populates="team_member", cascade="all, delete-orphan")

    @property
    def skills(self):
        """Dynamic helper for Pydantic serialization mapping."""
        return [
            {
                "skill_id": assoc.skill_id,
                "proficiency_level": assoc.proficiency_level,
                "name": assoc.skill.name if assoc.skill else "",
                "category": assoc.skill.category if assoc.skill else ""
            }
            for assoc in self.skills_associations
        ]
