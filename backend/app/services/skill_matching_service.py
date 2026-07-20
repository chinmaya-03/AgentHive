"""
Service layer orchestrating the Skill Matching Agent execution.
Consumes structured TaskBreakdownResult, invokes Skill Matching Agent, validates output schema.
"""

import json
import logging
from typing import Dict, Any, Set
from sqlalchemy.orm import Session

from app.repositories.requirement import requirement_repo
from app.repositories.project import project_repo
from app.services.task_breakdown_service import task_breakdown_service
from app.agents.skill_matching_agent import run_skill_matching
from app.schemas.ai import TaskBreakdownResult, SkillMatchingResult
from app.utils.helpers import extract_json_from_llm_output
from app.core.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class SkillMatchingService:
    @staticmethod
    def match_requirement_skills(
        db: Session, *, requirement_id: str, owner_id: str
    ) -> SkillMatchingResult:
        """
        Executes Skill Matching pipeline for a requirement document ID.
        
        1. Loads requirement document from database & verifies ownership.
        2. Obtains TaskBreakdownResult from Phase 4.
        3. Invokes Skill Matching Agent with task breakdown JSON.
        4. Parses & validates output matching SkillMatchingResult.
        """
        # Step 1: Verify document & project ownership
        doc = requirement_repo.get(db, id=requirement_id)
        if not doc:
            raise ValueError(f"Requirement document with ID '{requirement_id}' not found.")

        project = project_repo.get(db, id=doc.project_id)
        if not project or project.owner_id != owner_id:
            raise ValueError("Unauthorized access to requirement document.")

        # Step 2: Obtain Task Breakdown result
        logger.info(f"Obtaining Task Breakdown for Document ID={requirement_id}...")
        task_breakdown_result = task_breakdown_service.breakdown_requirement_tasks(
            db, requirement_id=requirement_id, owner_id=owner_id
        )

        task_count = len(task_breakdown_result.technical_tasks)
        task_breakdown_json = json.dumps(task_breakdown_result.model_dump(), indent=2)

        logger.info(
            f"Skill Matching Started: Document ID={requirement_id}, "
            f"Tasks to Analyze={task_count}"
        )

        # Step 3: Run Skill Matching Agent via CrewAI
        try:
            raw_response = run_skill_matching(task_breakdown_json)
        except Exception as e:
            logger.error(f"Skill Matching Failed during agent execution: {str(e)}")
            raise AgentExecutionError(
                agent_name="Skill Matching Agent",
                reason=f"LLM skill matching execution failed: {str(e)}"
            )

        # Step 4: Extract and parse JSON response
        try:
            json_dict = extract_json_from_llm_output(raw_response)
        except ValueError as ve:
            logger.error(f"JSON Parsing Failure during skill matching: {str(ve)}")
            raise AgentExecutionError(
                agent_name="Skill Matching Agent",
                reason=f"Failed to parse valid JSON from Skill Matching Agent response: {str(ve)}"
            )

        # Step 5: Validate output schema
        try:
            validated_output = SkillMatchingResult(**json_dict)

            # Collect metrics for structured logging
            assigned_roles: Set[str] = {item.developer_role for item in validated_output.assignments}
            all_skills: Set[str] = {skill for item in validated_output.assignments for skill in item.skills}

            logger.info(
                f"Skill Matching Completed: Document ID={requirement_id} | "
                f"Assignments={len(validated_output.assignments)}, "
                f"Roles Assigned={list(assigned_roles)}, "
                f"Total Unique Skills Generated={len(all_skills)}"
            )
            return validated_output

        except Exception as schema_err:
            logger.error(f"Skill Matching Schema Validation Failed: {str(schema_err)}")
            raise AgentExecutionError(
                agent_name="Skill Matching Agent",
                reason=f"Skill Matching AI output failed schema validation: {str(schema_err)}"
            )


skill_matching_service = SkillMatchingService()
