"""
Role enums and constant definitions for AgentHive agents and team members.
"""

from enum import Enum


class AgentRole(str, Enum):
    """Enums for AgentHive AI Agent roles."""
    REQUIREMENT_ANALYZER = "Requirement Analysis Agent"
    TASK_BREAKDOWN_ENGINEER = "Task Breakdown Agent"
    SKILL_MATCHING_ENGINEER = "Skill Matching Agent"
    SPRINT_PLANNER = "Sprint Planning Agent"
    RISK_ANALYZER = "Risk Analysis Agent"
    COORDINATOR = "Coordinator Agent"


class TeamMemberRole(str, Enum):
    """Enums for human team member technical roles."""
    BACKEND_DEVELOPER = "Backend Developer"
    FRONTEND_DEVELOPER = "Frontend Developer"
    FULLSTACK_DEVELOPER = "Fullstack Developer"
    DATABASE_ENGINEER = "Database Engineer"
    DEVOPS_ENGINEER = "DevOps Engineer"
    QA_ENGINEER = "QA / Testing Engineer"
    PROJECT_MANAGER = "Project Manager"
