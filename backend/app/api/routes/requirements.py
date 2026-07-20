"""
API Endpoints for Software Requirement Specification (SRS) document upload, retrieval, deletion, AI requirement analysis, task breakdown, and skill matching.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.requirement import RequirementResponse
from app.schemas.ai import RequirementAnalysisResult, TaskBreakdownResult, SkillMatchingResult, SprintPlanResult, RiskAnalysisResult
from app.schemas.orchestrator import ProjectPlanningResult
from app.services.requirement import requirement_service
from app.services.requirement_analysis_service import requirement_analysis_service
from app.services.task_breakdown_service import task_breakdown_service
from app.services.skill_matching_service import skill_matching_service
from app.services.sprint_planning_service import sprint_planning_service
from app.services.risk_analysis_service import risk_analysis_service
from app.services.orchestrator_service import orchestrator_service
from app.core.exceptions import FileParsingError, AgentExecutionError, AgentHiveException

router = APIRouter()


@router.post("/requirements/upload", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED, tags=["Requirements"])
def upload_requirement_standalone(
    project_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> RequirementResponse:
    """
    Upload a Software Requirement Specification (SRS) document with project_id passed in form data.
    """
    try:
        doc = requirement_service.upload_requirement(
            db, project_id=project_id, file=file, owner_id=current_user.id
        )
        return doc
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and upload document: {str(e)}"
        )


@router.post("/projects/{project_id}/requirements/upload", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED, tags=["Requirements"])
@router.post("/projects/{project_id}/requirements", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED, tags=["Requirements"])
def upload_requirement(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
) -> RequirementResponse:
    """
    Upload a Software Requirement Specification (SRS) document (PDF, DOCX, TXT) for a specific project.
    Validates file size (max 10MB), extension, and MIME type.
    Extracts text automatically using file_parser and stores result in database.
    """
    try:
        doc = requirement_service.upload_requirement(
            db, project_id=project_id, file=file, owner_id=current_user.id
        )
        return doc
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and upload document: {str(e)}"
        )


@router.post("/requirements/{requirement_id}/analyze", response_model=RequirementAnalysisResult, tags=["Requirements", "AI Requirement Analysis"])
def analyze_requirement(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> RequirementAnalysisResult:
    """
    Executes the CrewAI Requirement Analysis Agent on an uploaded SRS document ID.
    Reads extracted_text from database, performs structural AI analysis, and returns structured JSON.
    """
    try:
        analysis_result = requirement_analysis_service.analyze_requirement(
            db, requirement_id=requirement_id, owner_id=current_user.id
        )
        return analysis_result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except AgentExecutionError as aee:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(aee)
        )
    except TimeoutError as te:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM request timed out during analysis: {str(te)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during requirement analysis: {str(e)}"
        )


@router.post("/requirements/{requirement_id}/tasks", response_model=TaskBreakdownResult, tags=["Requirements", "AI Task Breakdown"])
def generate_requirement_tasks(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> TaskBreakdownResult:
    """
    Executes the CrewAI Task Breakdown Agent on an uploaded SRS document ID.
    Obtains structured Requirement Analysis, breaks down requirement into Epics, User Stories,
    and actionable Technical Engineering Tasks (with Fibonacci story points, priority, and dependencies).
    """
    try:
        tasks_result = task_breakdown_service.breakdown_requirement_tasks(
            db, requirement_id=requirement_id, owner_id=current_user.id
        )
        return tasks_result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except AgentExecutionError as aee:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(aee)
        )
    except TimeoutError as te:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM request timed out during task breakdown: {str(te)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during task breakdown generation: {str(e)}"
        )


@router.post("/requirements/{requirement_id}/skill-matching", response_model=SkillMatchingResult, tags=["Requirements", "AI Skill Matching"])
def match_requirement_skills(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> SkillMatchingResult:
    """
    Executes the CrewAI Skill Matching Agent on an uploaded SRS document ID.
    Executes pipeline (Requirement Analysis -> Task Breakdown -> Skill Matching),
    assigning suitable developer role, required technical skills, experience level, recommended tools, and reason for each task.
    """
    try:
        matching_result = skill_matching_service.match_requirement_skills(
            db, requirement_id=requirement_id, owner_id=current_user.id
        )
        return matching_result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except AgentExecutionError as aee:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(aee)
        )
    except TimeoutError as te:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM request timed out during skill matching: {str(te)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during skill matching generation: {str(e)}"
        )


@router.post("/requirements/{requirement_id}/sprint-plan", response_model=SprintPlanResult, tags=["Requirements", "AI Sprint Planning"])
def plan_requirement_sprints(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> SprintPlanResult:
    """
    Executes the CrewAI Sprint Planning Agent on an uploaded SRS document ID.
    Pipeline: Requirement -> Requirement Analysis -> Task Breakdown -> Skill Matching -> Sprint Planning -> Return SprintPlanResult.
    Consumes ONLY TaskBreakdownResult and SkillMatchingResult.
    """
    try:
        sprint_plan_result = sprint_planning_service.plan_sprints(
            db, requirement_id=requirement_id, owner_id=current_user.id
        )
        return sprint_plan_result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except AgentExecutionError as aee:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(aee)
        )
    except TimeoutError as te:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM request timed out during sprint planning: {str(te)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during sprint planning generation: {str(e)}"
        )


@router.post("/requirements/{requirement_id}/risk-analysis", response_model=RiskAnalysisResult, tags=["Requirements", "AI Risk Analysis"])
def analyze_requirement_risks(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> RiskAnalysisResult:
    """
    Executes the CrewAI Risk Analysis Agent on an uploaded SRS document ID.
    Pipeline: Requirement -> Requirement Analysis -> Task Breakdown -> Skill Matching -> Sprint Planning -> Risk Analysis -> Return RiskAnalysisResult.
    Consumes ONLY SprintPlanResult, SkillMatchingResult, and TaskBreakdownResult.
    """
    try:
        risk_result = risk_analysis_service.analyze_requirement_risks(
            db, requirement_id=requirement_id, owner_id=current_user.id
        )
        return risk_result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except AgentExecutionError as aee:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(aee)
        )
    except TimeoutError as te:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM request timed out during risk analysis: {str(te)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during risk analysis generation: {str(e)}"
        )


@router.post("/requirements/{requirement_id}/generate-plan", response_model=ProjectPlanningResult, tags=["Requirements", "AI Orchestrator"])
def generate_project_plan(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> ProjectPlanningResult:
    """
    Executes the Multi-Agent Crew Orchestrator pipeline end-to-end:
    Requirement Upload -> Requirement Analysis -> Task Breakdown -> Skill Matching -> Sprint Planning -> Risk Analysis -> ProjectPlanningResult.
    Performs single-pass execution, monitors duration per phase, and returns structured project plan & metrics.
    """
    try:
        plan_result = orchestrator_service.generate_full_project_plan(
            db, requirement_id=requirement_id, owner_id=current_user.id
        )
        return plan_result
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve)
        )
    except FileParsingError as fpe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(fpe)
        )
    except AgentExecutionError as aee:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(aee)
        )
    except TimeoutError as te:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM request timed out during orchestration: {str(te)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during project plan generation: {str(e)}"
        )


@router.get("/requirements", response_model=List[RequirementResponse], tags=["Requirements"])
def get_user_requirements(
    project_id: Optional[str] = Query(None, description="Optional project ID filter"),
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> List[RequirementResponse]:
    """Retrieve all requirements owned by the authenticated user, optionally filtered by project_id."""
    return requirement_service.get_all_user_requirements(
        db, owner_id=current_user.id, project_id=project_id
    )


@router.get("/projects/{project_id}/requirements", response_model=List[RequirementResponse], tags=["Requirements"])
def get_project_requirements(
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> List[RequirementResponse]:
    """Retrieve all requirements uploaded for a specific project."""
    return requirement_service.get_project_requirements(
        db, project_id=project_id, owner_id=current_user.id
    )


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse, tags=["Requirements"])
def get_requirement_by_id(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> RequirementResponse:
    """Retrieve a specific requirement document by ID."""
    doc = requirement_service.get_requirement(
        db, requirement_id=requirement_id, owner_id=current_user.id
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement document not found or unauthorized access."
        )
    return doc


@router.delete("/requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Requirements"])
@router.delete("/projects/{project_id}/requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Requirements"])
def delete_requirement(
    requirement_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Delete a requirement document by ID, removing its file from disk and database."""
    success = requirement_service.delete_requirement(
        db, requirement_id=requirement_id, owner_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement document not found or unauthorized access."
        )
    return None
