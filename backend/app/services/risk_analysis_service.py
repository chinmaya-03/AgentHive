"""
Service layer orchestrating the Risk Analysis Agent execution.
Consumes SprintPlanResult, SkillMatchingResult, TaskBreakdownResult, invokes Risk Analysis Agent, validates output schema.
"""

import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.repositories.requirement import requirement_repo
from app.repositories.project import project_repo
from app.services.task_breakdown_service import task_breakdown_service
from app.services.skill_matching_service import skill_matching_service
from app.services.sprint_planning_service import sprint_planning_service
from app.agents.risk_analysis_agent import run_risk_analysis
from app.schemas.ai import (
    TaskBreakdownResult,
    SkillMatchingResult,
    SprintPlanResult,
    RiskAnalysisResult,
)
from app.utils.helpers import extract_json_from_llm_output
from app.core.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class RiskAnalysisService:
    @staticmethod
    def analyze_requirement_risks(
        db: Session, *, requirement_id: str, owner_id: str
    ) -> RiskAnalysisResult:
        """
        Executes Risk Analysis pipeline for a requirement document ID.
        
        Pipeline:
        Requirement -> Requirement Analysis -> Task Breakdown -> Skill Matching -> Sprint Planning -> Risk Analysis
        """
        # Step 1: Verify document & project ownership
        doc = requirement_repo.get(db, id=requirement_id)
        if not doc:
            raise ValueError(f"Requirement document with ID '{requirement_id}' not found.")

        project = project_repo.get(db, id=doc.project_id)
        if not project or project.owner_id != owner_id:
            raise ValueError("Unauthorized access to requirement document.")

        # Step 2: Execute Task Breakdown (Phase 4)
        logger.info(f"Obtaining Task Breakdown for Document ID={requirement_id}...")
        task_breakdown_result = task_breakdown_service.breakdown_requirement_tasks(
            db, requirement_id=requirement_id, owner_id=owner_id
        )

        if not task_breakdown_result.technical_tasks:
            raise ValueError("Task breakdown produced no technical tasks for risk analysis.")

        # Step 3: Execute Skill Matching (Phase 5)
        logger.info(f"Obtaining Skill Matching for Document ID={requirement_id}...")
        skill_matching_result = skill_matching_service.match_requirement_skills(
            db, requirement_id=requirement_id, owner_id=owner_id
        )

        if not skill_matching_result.assignments:
            raise ValueError("Skill matching produced no role assignments for risk analysis.")

        # Step 4: Execute Sprint Planning (Phase 6)
        logger.info(f"Obtaining Sprint Plan for Document ID={requirement_id}...")
        sprint_plan_result = sprint_planning_service.plan_sprints(
            db, requirement_id=requirement_id, owner_id=owner_id
        )

        if not sprint_plan_result.sprints:
            raise ValueError("Sprint planning produced no sprints for risk analysis.")

        # Aggregate inputs (SprintPlanResult + SkillMatchingResult + TaskBreakdownResult) into context payload
        context_payload = {
            "sprint_plan": sprint_plan_result.model_dump(),
            "skill_assignments": skill_matching_result.model_dump(),
            "task_breakdown": task_breakdown_result.model_dump(),
        }

        sprint_plan_json = json.dumps(context_payload, indent=2)
        sprint_count = len(sprint_plan_result.sprints)

        # Structured Log: Risk analysis started
        logger.info(
            f"Risk Analysis Started: Document ID={requirement_id} | "
            f"Number of Sprints={sprint_count}"
        )

        # Step 5: Run Risk Analysis Agent via CrewAI
        try:
            raw_response = run_risk_analysis(sprint_plan_json)
        except Exception as e:
            logger.error(f"Risk Analysis AI failure during agent execution: {str(e)}")
            raise AgentExecutionError(
                agent_name="Risk Analysis Agent",
                reason=f"LLM risk analysis execution failed: {str(e)}"
            )

        # Step 6: Extract and parse JSON response
        try:
            json_dict = extract_json_from_llm_output(raw_response)
        except ValueError as ve:
            logger.error(f"Risk Analysis AI failure during JSON parsing: {str(ve)}")
            raise AgentExecutionError(
                agent_name="Risk Analysis Agent",
                reason=f"Failed to parse valid JSON from Risk Analysis Agent response: {str(ve)}"
            )

        # Step 7: Validate output schema using Pydantic
        try:
            validated_output = RiskAnalysisResult(**json_dict)

            # Structured Log: Risk metrics
            risk_count = len(validated_output.risks)
            overall_risk = validated_output.overall_risk

            logger.info(
                f"Risk Analysis Completed: Document ID={requirement_id} | "
                f"Number of Sprints={sprint_count} | Number of Risks={risk_count} | "
                f"Overall Risk Level={overall_risk}"
            )
            return validated_output

        except Exception as schema_err:
            logger.error(f"Risk Analysis Validation Failure: {str(schema_err)}")
            raise AgentExecutionError(
                agent_name="Risk Analysis Agent",
                reason=f"Risk Analysis AI output failed schema validation: {str(schema_err)}"
            )


risk_analysis_service = RiskAnalysisService()
