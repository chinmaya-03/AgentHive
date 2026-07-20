"""
Service layer orchestrating the Requirement Analysis Agent execution.
Fetches SRS document from DB, invokes CrewAI analysis agent, parses/validates structured JSON output.
"""

import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models.requirement import RequirementDocument
from app.repositories.project import project_repo
from app.repositories.requirement import requirement_repo
from app.agents.requirement_agent import run_requirement_analysis
from app.schemas.ai import RequirementAnalysisResult
from app.utils.helpers import extract_json_from_llm_output
from app.core.config import settings
from app.core.exceptions import FileParsingError, AgentExecutionError

logger = logging.getLogger(__name__)


class RequirementAnalysisService:
    @staticmethod
    def analyze_requirement(
        db: Session, *, requirement_id: str, owner_id: str
    ) -> RequirementAnalysisResult:
        """
        Executes requirement analysis on an uploaded document ID.
        
        1. Fetches RequirementDocument from DB.
        2. Validates extracted_text is present.
        3. Invokes CrewAI Requirement Analysis Agent.
        4. Parses and validates response against RequirementAnalysisResult.
        """
        # Step 1: Fetch requirement document from DB
        doc = requirement_repo.get(db, id=requirement_id)
        if not doc:
            raise ValueError(f"Requirement document with ID '{requirement_id}' not found.")

        # Verify project ownership
        project = project_repo.get(db, id=doc.project_id)
        if not project or project.owner_id != owner_id:
            raise ValueError("Unauthorized access to requirement document.")

        # Step 2: Validate extracted_text exists
        srs_text = doc.extracted_text
        if not srs_text or not srs_text.strip() or srs_text.startswith("Parsing Error:"):
            raise FileParsingError(
                f"Document '{doc.original_filename}' has no valid extracted text to analyze."
            )

        logger.info(
            f"Requirement Analysis Started: Document ID={requirement_id}, "
            f"Model={settings.GROQ_MODEL}, File='{doc.original_filename}', Length={len(srs_text)} chars"
        )

        # Step 3: Run Requirement Analysis Agent via CrewAI
        try:
            raw_response = run_requirement_analysis(srs_text)
        except Exception as e:
            logger.error(f"Requirement Analysis Failed during agent execution: {str(e)}")
            raise AgentExecutionError(
                agent_name="Requirement Analysis Agent",
                reason=f"LLM execution error: {str(e)}"
            )

        # Step 4: Extract and parse JSON response
        try:
            json_dict = extract_json_from_llm_output(raw_response)
        except ValueError as ve:
            logger.error(f"JSON Parsing Failure for document ID={requirement_id}: {str(ve)}")
            raise AgentExecutionError(
                agent_name="Requirement Analysis Agent",
                reason=f"Failed to parse valid JSON response from AI model: {str(ve)}"
            )

        # Step 5: Validate with Pydantic Schema
        try:
            validated_output = RequirementAnalysisResult(**json_dict)
            logger.info(
                f"Requirement Analysis Completed: Document ID={requirement_id}, "
                f"Complexity={validated_output.complexity}, "
                f"Functional Req Count={len(validated_output.functional_requirements)}"
            )
            
            # Update requirement document status in database
            doc.processing_status = "Analyzed"
            db.add(doc)
            db.commit()
            db.refresh(doc)
            
            return validated_output

        except Exception as schema_err:
            logger.error(f"Requirement Analysis Schema Validation Failed: {str(schema_err)}")
            raise AgentExecutionError(
                agent_name="Requirement Analysis Agent",
                reason=f"AI output failed schema validation: {str(schema_err)}"
            )


requirement_analysis_service = RequirementAnalysisService()
