"""
Service layer orchestrating the Task Breakdown Agent execution.
Consumes structured RequirementAnalysisResult, invokes Task Breakdown Agent, validates output schema.
"""

import json
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.repositories.requirement import requirement_repo
from app.repositories.project import project_repo
from app.services.requirement_analysis_service import requirement_analysis_service
from app.agents.task_breakdown_agent import run_task_breakdown
from app.schemas.ai import RequirementAnalysisResult, TaskBreakdownResult
from app.utils.helpers import extract_json_from_llm_output
from app.core.exceptions import AgentExecutionError, FileParsingError

logger = logging.getLogger(__name__)


class TaskBreakdownService:
    @staticmethod
    def breakdown_requirement_tasks(
        db: Session, *, requirement_id: str, owner_id: str
    ) -> TaskBreakdownResult:
        """
        Executes Task Breakdown pipeline for a requirement document ID.
        
        1. Loads requirement from database & verifies ownership.
        2. Obtains RequirementAnalysisResult (running requirement analysis if needed).
        3. Invokes Task Breakdown Agent with structured analysis JSON.
        4. Parses & validates output matching TaskBreakdownResult.
        """
        # Step 1: Load requirement document from database
        doc = requirement_repo.get(db, id=requirement_id)
        if not doc:
            raise ValueError(f"Requirement document with ID '{requirement_id}' not found.")

        project = project_repo.get(db, id=doc.project_id)
        if not project or project.owner_id != owner_id:
            raise ValueError("Unauthorized access to requirement document.")

        # Step 2: Obtain requirement analysis result
        logger.info(f"Obtaining Requirement Analysis for Document ID={requirement_id}...")
        analysis_result = requirement_analysis_service.analyze_requirement(
            db, requirement_id=requirement_id, owner_id=owner_id
        )

        analysis_json = json.dumps(analysis_result.model_dump(), indent=2)

        logger.info(
            f"Task Generation Started: Document ID={requirement_id}, "
            f"Summary='{analysis_result.project_summary[:50]}...'"
        )

        # Step 3: Run Task Breakdown Agent via CrewAI
        try:
            raw_response = run_task_breakdown(analysis_json)
        except Exception as e:
            logger.error(f"Task Generation Failed during agent execution: {str(e)}")
            raise AgentExecutionError(
                agent_name="Task Breakdown Agent",
                reason=f"LLM task generation failed: {str(e)}"
            )

        # Step 4: Extract and parse JSON response
        try:
            json_dict = extract_json_from_llm_output(raw_response)
        except ValueError as ve:
            logger.error(f"JSON Parsing Failure during task breakdown: {str(ve)}")
            raise AgentExecutionError(
                agent_name="Task Breakdown Agent",
                reason=f"Failed to parse valid JSON from Task Breakdown Agent response: {str(ve)}"
            )

        # Step 5: Validate output schema
        try:
            validated_output = TaskBreakdownResult(**json_dict)
            logger.info(
                f"Task Generation Completed: Document ID={requirement_id} | "
                f"Epics={len(validated_output.epics)}, "
                f"User Stories={len(validated_output.user_stories)}, "
                f"Engineering Tasks={len(validated_output.technical_tasks)}"
            )
            return validated_output

        except Exception as schema_err:
            logger.error(f"Task Breakdown Schema Validation Failed: {str(schema_err)}")
            raise AgentExecutionError(
                agent_name="Task Breakdown Agent",
                reason=f"Task Breakdown AI output failed schema validation: {str(schema_err)}"
            )


task_breakdown_service = TaskBreakdownService()
