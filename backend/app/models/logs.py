"""
SQLAlchemy database models for Agent Execution Logs and AI Recommendations.
"""

import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class AgentExecutionLog(Base):
    __tablename__ = "agent_execution_logs"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Any = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_name: Any = Column(String(100), nullable=False)
    status: Any = Column(String(50), default="Pending")  # Running, Completed, Failed
    input_data: Any = Column(Text, nullable=True)         # JSON format representation
    output_data: Any = Column(Text, nullable=True)        # JSON format representation
    execution_time: Any = Column(Float, default=0.0)      # Time in seconds
    logs: Any = Column(Text, nullable=True)               # Console / trace logs
    
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="agent_logs")


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    risk_type = Column(String(100), nullable=False)   # Overloaded Developer, Dependency Conflict, etc.
    description = Column(Text, nullable=False)
    severity = Column(String(50), default="Medium")  # Low, Medium, High
    recommendation = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="recommendations")
