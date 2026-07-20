"""
Status enums for execution logs, requirement processing, projects, and risks.
"""

from enum import Enum


class AgentExecutionStatus(str, Enum):
    """Execution state for background AI agents."""
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class RequirementDocStatus(str, Enum):
    """Processing state for uploaded requirement documents."""
    UPLOADED = "Uploaded"
    PROCESSING = "Processing"
    PROCESSED = "Processed"
    FAILED = "Failed"


class ProjectStatus(str, Enum):
    """Overall project workflow state."""
    DRAFT = "Draft"
    ANALYSIS_IN_PROGRESS = "Analysis In Progress"
    SPRINT_PLANNED = "Sprint Planned"
    ACTIVE = "Active"
    COMPLETED = "Completed"


class RiskSeverity(str, Enum):
    """Risk severity levels identified by the Risk Analysis Agent."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
