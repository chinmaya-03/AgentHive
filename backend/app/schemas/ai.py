"""
Pydantic Schemas for AI Agent outputs, request payloads, and structured LLM responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Requirement Analysis Schemas ---
class RequirementAnalysisResult(BaseModel):
    project_summary: str = Field(..., description="Concise executive summary of the software project")
    functional_requirements: List[str] = Field(default_factory=list, description="Identified functional requirements")
    non_functional_requirements: List[str] = Field(default_factory=list, description="Identified non-functional requirements")
    missing_requirements: List[str] = Field(default_factory=list, description="Identified missing or omitted requirement items")
    ambiguities: List[str] = Field(default_factory=list, description="Identified vague or ambiguous statements needing clarification")
    complexity: str = Field(..., description="Project complexity rating: Low, Medium, or High")


class FunctionalRequirement(BaseModel):
    id: str = Field(..., description="Unique identifier (e.g. REQ-1)")
    title: str = Field(..., description="Short descriptive title of requirement")
    module: str = Field(..., description="Parent module name")
    description: str = Field(..., description="Detailed functional requirement scope")
    priority: str = Field(..., description="High, Medium, or Low")


class RequirementModule(BaseModel):
    name: str = Field(..., description="Module name")
    description: str = Field(..., description="Module functionality summary")
    dependencies: List[str] = Field(default_factory=list, description="Names of prerequisite modules")


class RequirementAnalysisOutput(BaseModel):
    project_complexity: str = Field(..., description="Low, Medium, or High")
    complexity_reasoning: str = Field(..., description="Justification for complexity rating")
    modules: List[RequirementModule] = Field(default_factory=list)
    requirements: List[FunctionalRequirement] = Field(default_factory=list)


# --- Task Breakdown Schemas ---
class TechnicalTask(BaseModel):
    title: str = Field(..., description="Short descriptive title of technical task")
    description: str = Field(..., description="Actionable engineering implementation details")
    story_points: int = Field(..., description="Fibonacci story points (1, 2, 3, 5, 8, 13)")
    priority: str = Field(..., description="Task priority: High, Medium, or Low")
    dependencies: List[str] = Field(default_factory=list, description="List of prerequisite task titles")


class TaskBreakdownResult(BaseModel):
    epics: List[str] = Field(default_factory=list, description="High-level Epics grouping feature areas")
    user_stories: List[str] = Field(default_factory=list, description="User stories representing feature scope")
    technical_tasks: List[TechnicalTask] = Field(default_factory=list, description="Detailed actionable technical engineering tasks")


class TaskItem(BaseModel):
    id: str = Field(..., description="Unique task ID (e.g. TASK-1)")
    title: str = Field(..., description="Short task title")
    description: str = Field(..., description="Actionable implementation instructions")
    category: str = Field(..., description="Backend, Frontend, Database, Testing, or DevOps")
    estimated_hours: float = Field(..., description="Estimated hours (e.g., 4.0)")
    difficulty: str = Field(..., description="Easy, Medium, or Hard")
    module: str = Field(..., description="Parent module name")
    dependencies: List[str] = Field(default_factory=list, description="IDs of dependent task titles")


class TaskBreakdownOutput(BaseModel):
    tasks: List[TaskItem] = Field(default_factory=list)


# --- Skill Matching Schemas ---
class DeveloperAssignment(BaseModel):
    task_title: str = Field(..., description="Engineering task title")
    developer_role: str = Field(..., description="Assigned role e.g. Backend Developer, Frontend Developer")
    experience_level: str = Field(..., description="Required experience level e.g. Junior, Mid, Senior, Lead")
    skills: List[str] = Field(default_factory=list, description="Required technical skills e.g. FastAPI, React")
    recommended_tools: List[str] = Field(default_factory=list, description="Recommended development tools e.g. Postman, Docker")
    reason: str = Field(..., description="Justification for role and experience level selection")


class SkillMatchingResult(BaseModel):
    assignments: List[DeveloperAssignment] = Field(default_factory=list, description="List of task developer skill assignments")


class TaskAssignment(BaseModel):
    task_id: str = Field(..., description="Task ID")
    task_title: str = Field(..., description="Task title")
    assigned_member_id: str = Field(..., description="Assigned team member ID")
    assigned_member_name: str = Field(..., description="Assigned team member name")
    reasoning: str = Field(..., description="Justification for skill and workload fit")


class SkillMatchOutput(BaseModel):
    assignments: List[TaskAssignment] = Field(default_factory=list)


# --- Sprint Planning Schemas ---
class SprintTask(BaseModel):
    task_title: str = Field(..., description="Engineering task title")
    assigned_role: str = Field(..., description="Developer role assigned to the task")
    story_points: int = Field(..., description="Fibonacci story points assigned to the task")


class Sprint(BaseModel):
    sprint_name: str = Field(..., description="Sprint name (e.g. Sprint 1)")
    goal: str = Field(..., description="Primary technical or business goal for this sprint")
    total_story_points: int = Field(..., description="Total story points allocated to this sprint")
    tasks: List[SprintTask] = Field(default_factory=list, description="List of tasks scheduled in this sprint")


class SprintPlanResult(BaseModel):
    sprints: List[Sprint] = Field(default_factory=list, description="List of planned sprints")


# --- Risk Analysis Schemas ---
class RiskItem(BaseModel):
    title: str = Field(..., description="Short title of the identified risk")
    severity: str = Field(..., description="Risk severity level: Low, Medium, High, or Critical")
    description: str = Field(..., description="Detailed description of the identified risk")
    affected_sprint: str = Field(..., description="Sprint affected by the risk (e.g. Sprint 1 or Global)")
    recommendation: str = Field(..., description="Actionable mitigation recommendation")


class RiskAnalysisResult(BaseModel):
    overall_risk: str = Field(..., description="Overall project risk rating: Low, Medium, High, or Critical")
    risks: List[RiskItem] = Field(default_factory=list, description="List of identified project execution risks")
    summary: str = Field(..., description="Executive summary of overall project risk assessment")


# --- Schema Aliases for Agent Compatibility ---
SkillMatchingOutput = SkillMatchOutput
SprintPlanningOutput = SprintPlanResult
RiskAnalysisOutput = RiskAnalysisResult

