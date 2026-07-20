"""
API Endpoints for Project management (CRUD).
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project import project_service

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Retrieve all projects for the logged-in user."""
    return project_service.get_projects(db, owner_id=current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    project_in: ProjectCreate
) -> ProjectResponse:
    """Create a new project."""
    return project_service.create_project(db, project_in=project_in, owner_id=current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    *,
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> ProjectResponse:
    """Retrieve a specific project's details."""
    project = project_service.get_project(db, project_id=project_id, owner_id=current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you do not have permission to view it."
        )
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    *,
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    project_in: ProjectUpdate
) -> ProjectResponse:
    """Update an existing project's metadata."""
    project = project_service.update_project(
        db, project_id=project_id, project_in=project_in, owner_id=current_user.id
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you do not have permission to edit it."
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    *,
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Delete a project and its associated requirements, tasks, team members, and logs."""
    success = project_service.delete_project(db, project_id=project_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you do not have permission to delete it."
        )
