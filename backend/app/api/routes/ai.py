"""
API Router for AI Sprint Plan Generation, Logs, and Recommendations.
Enforces Service Layer encapsulation.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import deps
from app.services.ai import ai_service
from app.services.sprint import sprint_service

router = APIRouter()


@router.post("/projects/{project_id}/generate", status_code=status.HTTP_202_ACCEPTED)
def generate_sprint_plan(
    project_id: str,
    background_tasks: BackgroundTasks,
    requirement_id: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Trigger the multi-agent AI pipeline in the background.
    Delegates validation, log initialization, and worker thread setup to AIService.
    """
    try:
        res = ai_service.trigger_sprint_plan_generation(
            db, project_id=project_id, owner_id=current_user.id, background_tasks=background_tasks, requirement_id=requirement_id
        )
        if res is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found or unauthorized access."
            )
        return res
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )


@router.get("/projects/{project_id}/logs")
def get_generation_logs(
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Fetch execution logs for all 5 agents used to render the visual AI Control Center workflow.
    """
    logs = ai_service.get_generation_logs(db, project_id=project_id, owner_id=current_user.id)
    if logs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized access."
        )
    return logs


@router.get("/projects/{project_id}/plan")
def get_sprint_plan(
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Fetch the complete compiled sprint plan (tasks, assignments, sprints, and risks).
    """
    plan = sprint_service.get_sprint_plan_data(db, project_id=project_id, owner_id=current_user.id)
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized access."
        )
    return plan
