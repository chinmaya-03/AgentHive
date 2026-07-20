"""
Pydantic Schemas for Multi-Agent Crew Orchestrator results and execution metrics.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.schemas.ai import (
    RequirementAnalysisResult,
    TaskBreakdownResult,
    SkillMatchingResult,
    SprintPlanResult,
    RiskAnalysisResult,
)


class ProjectPlanningSummary(BaseModel):
    total_tasks: int = Field(..., description="Total count of engineering tasks")
    total_story_points: int = Field(..., description="Total sum of story points")
    number_of_sprints: int = Field(..., description="Total planned sprint iterations")
    overall_risk: str = Field(..., description="Overall project risk rating (Low, Medium, High, Critical)")
    suggested_team_size: int = Field(..., description="Recommended engineering team size based on developer role assignments")
    estimated_duration: str = Field(..., description="Estimated overall project duration e.g. '6 weeks'")


class ExecutionMetrics(BaseModel):
    start_time: str = Field(..., description="ISO timestamp of pipeline execution start")
    end_time: str = Field(..., description="ISO timestamp of pipeline execution end")
    total_execution_time_seconds: float = Field(..., description="Total pipeline execution time in seconds")
    successful_phase_count: int = Field(..., description="Number of successfully completed agent phases")
    failed_phase: Optional[str] = Field(None, description="Name of failed phase if pipeline halted prematurely")
    error_message: Optional[str] = Field(None, description="Error details if pipeline encountered failure")
    phase_durations: Dict[str, float] = Field(default_factory=dict, description="Execution time in seconds per phase")


class ProjectPlanningResult(BaseModel):
    requirement_analysis: Optional[RequirementAnalysisResult] = Field(None, description="Phase 3 Requirement Analysis result")
    task_breakdown: Optional[TaskBreakdownResult] = Field(None, description="Phase 4 Task Breakdown result")
    skill_matching: Optional[SkillMatchingResult] = Field(None, description="Phase 5 Skill Matching result")
    sprint_plan: Optional[SprintPlanResult] = Field(None, description="Phase 6 Sprint Planning result")
    risk_analysis: Optional[RiskAnalysisResult] = Field(None, description="Phase 7 Risk Analysis result")
    summary: Optional[ProjectPlanningSummary] = Field(None, description="Aggregated planning metrics summary")
    execution_metrics: ExecutionMetrics = Field(..., description="Execution monitoring metrics and duration logs")
