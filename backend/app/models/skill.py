"""
SQLAlchemy database model for Skills.
"""

from typing import Any
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class Skill(Base):
    __tablename__ = "skills"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Any = Column(String(100), unique=True, index=True, nullable=False)
    category: Any = Column(String(50), nullable=False)  # Frontend, Backend, Database, DevOps, Testing, etc.
    
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    team_member_associations = relationship("TeamMemberSkill", back_populates="skill", cascade="all, delete-orphan")
