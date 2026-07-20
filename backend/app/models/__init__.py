"""
Import all models to register them with SQLAlchemy Base.
"""

from app.database.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.skill import Skill
from app.models.team import TeamMember, TeamMemberSkill
from app.models.requirement import RequirementDocument
from app.models.sprint import Sprint
from app.models.task import Task, TaskAssignment, SprintTask
from app.models.logs import AgentExecutionLog, AIRecommendation

__all__ = [
    "Base",
    "User",
    "Project",
    "Skill",
    "TeamMember",
    "TeamMemberSkill",
    "RequirementDocument",
    "Sprint",
    "Task",
    "TaskAssignment",
    "SprintTask",
    "AgentExecutionLog",
    "AIRecommendation"
]
