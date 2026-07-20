"""
Multi-Agent Crew Orchestrator Service.
Coordinates sequential execution of AI agents (Phase 3 through Phase 7),
monitors execution timing per phase, handles failures gracefully, and generates project planning metrics.
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Set
from sqlalchemy.orm import Session

from app.repositories.requirement import requirement_repo
from app.repositories.project import project_repo
from app.agents.requirement_agent import run_requirement_analysis
from app.agents.task_breakdown_agent import run_task_breakdown
from app.agents.skill_matching_agent import run_skill_matching
from app.agents.sprint_planning_agent import run_sprint_planning
from app.agents.risk_analysis_agent import run_risk_analysis

from app.schemas.ai import (
    RequirementAnalysisResult,
    TaskBreakdownResult,
    SkillMatchingResult,
    SprintPlanResult,
    RiskAnalysisResult,
)
from app.schemas.orchestrator import (
    ProjectPlanningResult,
    ProjectPlanningSummary,
    ExecutionMetrics,
)
from app.utils.helpers import extract_json_from_llm_output
from app.core.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class OrchestratorService:
    @staticmethod
    def generate_full_project_plan(
        db: Session, *, requirement_id: str, owner_id: str
    ) -> ProjectPlanningResult:
        """
        Executes end-to-end multi-agent orchestration pipeline:
        Requirement Upload -> Requirement Analysis -> Task Breakdown -> Skill Matching -> Sprint Planning -> Risk Analysis.
        
        Single execution per phase; outputs passed directly down the pipeline.
        """
        pipeline_start_time = time.time()
        start_iso = datetime.now(timezone.utc).isoformat()

        # Step 0: Validate requirement & project access
        doc = requirement_repo.get(db, id=requirement_id)
        if not doc:
            raise ValueError(f"Requirement document with ID '{requirement_id}' not found.")

        project = project_repo.get(db, id=doc.project_id)
        if not project or project.owner_id != owner_id:
            raise ValueError("Unauthorized access to requirement document.")

        if not doc.extracted_text or not doc.extracted_text.strip():
            raise ValueError(f"Requirement document ID '{requirement_id}' has no extracted text.")

        phase_durations: Dict[str, float] = {}
        successful_phases = 0
        failed_phase: Optional[str] = None
        error_message: Optional[str] = None

        res_analysis: Optional[RequirementAnalysisResult] = None
        res_tasks: Optional[TaskBreakdownResult] = None
        res_skills: Optional[SkillMatchingResult] = None
        res_sprints: Optional[SprintPlanResult] = None
        res_risks: Optional[RiskAnalysisResult] = None

        logger.info(f"Multi-Agent Orchestration Started for Requirement ID={requirement_id}")

        # --- Phase 3: Requirement Analysis ---
        p_name = "requirement_analysis"
        try:
            t0 = time.time()
            logger.info("Executing Phase 3: Requirement Analysis Agent...")
            raw_req = run_requirement_analysis(doc.extracted_text)
            dict_req = extract_json_from_llm_output(raw_req)
            res_analysis = RequirementAnalysisResult(**dict_req)
            dur = time.time() - t0
            phase_durations[p_name] = round(dur, 3)
            successful_phases += 1
            logger.info(f"Phase 3 Completed in {dur:.2f}s | Complexity={res_analysis.complexity}")
        except Exception as e:
            failed_phase = p_name
            error_message = f"Requirement Analysis Phase failed: {str(e)}"
            logger.error(f"Orchestration Halted at Phase 3: {error_message}")
            return OrchestratorService._build_result(
                start_iso, pipeline_start_time, phase_durations, successful_phases, failed_phase, error_message,
                res_analysis, res_tasks, res_skills, res_sprints, res_risks
            )

        # --- Phase 4: Task Breakdown ---
        p_name = "task_breakdown"
        try:
            t0 = time.time()
            logger.info("Executing Phase 4: Task Breakdown Agent...")
            analysis_json = json.dumps(res_analysis.model_dump(), indent=2)
            raw_tasks = run_task_breakdown(analysis_json)
            dict_tasks = extract_json_from_llm_output(raw_tasks)
            res_tasks = TaskBreakdownResult(**dict_tasks)
            dur = time.time() - t0
            phase_durations[p_name] = round(dur, 3)
            successful_phases += 1
            logger.info(f"Phase 4 Completed in {dur:.2f}s | Tasks={len(res_tasks.technical_tasks)}")
        except Exception as e:
            failed_phase = p_name
            error_message = f"Task Breakdown Phase failed: {str(e)}"
            logger.error(f"Orchestration Halted at Phase 4: {error_message}")
            return OrchestratorService._build_result(
                start_iso, pipeline_start_time, phase_durations, successful_phases, failed_phase, error_message,
                res_analysis, res_tasks, res_skills, res_sprints, res_risks
            )

        # --- Phase 5: Skill Matching ---
        p_name = "skill_matching"
        try:
            t0 = time.time()
            logger.info("Executing Phase 5: Skill Matching Agent...")
            tasks_json = json.dumps(res_tasks.model_dump(), indent=2)
            raw_skills = run_skill_matching(tasks_json)
            dict_skills = extract_json_from_llm_output(raw_skills)
            res_skills = SkillMatchingResult(**dict_skills)
            dur = time.time() - t0
            phase_durations[p_name] = round(dur, 3)
            successful_phases += 1
            logger.info(f"Phase 5 Completed in {dur:.2f}s | Assignments={len(res_skills.assignments)}")
        except Exception as e:
            failed_phase = p_name
            error_message = f"Skill Matching Phase failed: {str(e)}"
            logger.error(f"Orchestration Halted at Phase 5: {error_message}")
            return OrchestratorService._build_result(
                start_iso, pipeline_start_time, phase_durations, successful_phases, failed_phase, error_message,
                res_analysis, res_tasks, res_skills, res_sprints, res_risks
            )

        # --- Phase 6: Sprint Planning ---
        p_name = "sprint_plan"
        try:
            t0 = time.time()
            logger.info("Executing Phase 6: Sprint Planning Agent...")
            assignments_by_title = {a.task_title: a for a in res_skills.assignments}
            combined_tasks = []
            for t in res_tasks.technical_tasks:
                assignment = assignments_by_title.get(t.title)
                combined_tasks.append({
                    "task_title": t.title,
                    "description": t.description,
                    "story_points": t.story_points,
                    "priority": t.priority,
                    "dependencies": t.dependencies,
                    "assigned_role": assignment.developer_role if assignment else "Software Engineer",
                    "required_skills": assignment.skills if assignment else [],
                    "experience_level": assignment.experience_level if assignment else "Mid"
                })

            sprint_input_json = json.dumps(combined_tasks, indent=2)
            raw_sprints = run_sprint_planning(sprint_input_json)
            dict_sprints = extract_json_from_llm_output(raw_sprints)
            res_sprints = SprintPlanResult(**dict_sprints)
            dur = time.time() - t0
            phase_durations[p_name] = round(dur, 3)
            successful_phases += 1
            logger.info(f"Phase 6 Completed in {dur:.2f}s | Sprints={len(res_sprints.sprints)}")
        except Exception as e:
            failed_phase = p_name
            error_message = f"Sprint Planning Phase failed: {str(e)}"
            logger.error(f"Orchestration Halted at Phase 6: {error_message}")
            return OrchestratorService._build_result(
                start_iso, pipeline_start_time, phase_durations, successful_phases, failed_phase, error_message,
                res_analysis, res_tasks, res_skills, res_sprints, res_risks
            )

        # --- Phase 7: Risk Analysis ---
        p_name = "risk_analysis"
        try:
            t0 = time.time()
            logger.info("Executing Phase 7: Risk Analysis Agent...")
            risk_context = {
                "sprint_plan": res_sprints.model_dump(),
                "skill_assignments": res_skills.model_dump(),
                "task_breakdown": res_tasks.model_dump(),
            }
            raw_risks = run_risk_analysis(json.dumps(risk_context, indent=2))
            dict_risks = extract_json_from_llm_output(raw_risks)
            res_risks = RiskAnalysisResult(**dict_risks)
            dur = time.time() - t0
            phase_durations[p_name] = round(dur, 3)
            successful_phases += 1
            logger.info(f"Phase 7 Completed in {dur:.2f}s | Overall Risk={res_risks.overall_risk}")
        except Exception as e:
            failed_phase = p_name
            error_message = f"Risk Analysis Phase failed: {str(e)}"
            logger.error(f"Orchestration Halted at Phase 7: {error_message}")
            return OrchestratorService._build_result(
                start_iso, pipeline_start_time, phase_durations, successful_phases, failed_phase, error_message,
                res_analysis, res_tasks, res_skills, res_sprints, res_risks
            )

        # All 5 phases completed successfully
        logger.info(
            f"Multi-Agent Orchestration Completed Successfully! "
            f"Requirement ID={requirement_id} | Total Time={time.time() - pipeline_start_time:.2f}s"
        )
        return OrchestratorService._build_result(
            start_iso, pipeline_start_time, phase_durations, successful_phases, None, None,
            res_analysis, res_tasks, res_skills, res_sprints, res_risks
        )

    @staticmethod
    def _build_result(
        start_iso: str,
        start_time_seconds: float,
        phase_durations: Dict[str, float],
        successful_phases: int,
        failed_phase: Optional[str],
        error_message: Optional[str],
        res_analysis: Optional[RequirementAnalysisResult],
        res_tasks: Optional[TaskBreakdownResult],
        res_skills: Optional[SkillMatchingResult],
        res_sprints: Optional[SprintPlanResult],
        res_risks: Optional[RiskAnalysisResult],
    ) -> ProjectPlanningResult:
        """Helper to construct ProjectPlanningResult with execution metrics and summary."""
        end_iso = datetime.now(timezone.utc).isoformat()
        total_duration = round(time.time() - start_time_seconds, 3)

        summary: Optional[ProjectPlanningSummary] = None

        if res_tasks and res_skills and res_sprints and res_risks:
            total_tasks = len(res_tasks.technical_tasks)
            total_sp = sum(t.story_points for t in res_tasks.technical_tasks)
            num_sprints = len(res_sprints.sprints)
            overall_risk = res_risks.overall_risk
            unique_roles: Set[str] = {a.developer_role for a in res_skills.assignments}
            suggested_team_size = max(len(unique_roles), 3)
            estimated_duration = f"{num_sprints * 2} weeks"

            summary = ProjectPlanningSummary(
                total_tasks=total_tasks,
                total_story_points=total_sp,
                number_of_sprints=num_sprints,
                overall_risk=overall_risk,
                suggested_team_size=suggested_team_size,
                estimated_duration=estimated_duration,
            )

        metrics = ExecutionMetrics(
            start_time=start_iso,
            end_time=end_iso,
            total_execution_time_seconds=total_duration,
            successful_phase_count=successful_phases,
            failed_phase=failed_phase,
            error_message=error_message,
            phase_durations=phase_durations,
        )

        return ProjectPlanningResult(
            requirement_analysis=res_analysis,
            task_breakdown=res_tasks,
            skill_matching=res_skills,
            sprint_plan=res_sprints,
            risk_analysis=res_risks,
            summary=summary,
            execution_metrics=metrics,
        )


orchestrator_service = OrchestratorService()
