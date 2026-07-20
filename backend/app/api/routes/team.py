"""
API Endpoints for Team Member and Skill Assignment management.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.team import TeamMemberCreate, TeamMemberUpdate, TeamMemberResponse
from app.services.team import team_service

router = APIRouter()


@router.get("/", response_model=List[TeamMemberResponse])
def get_team_members(
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> Any:
    """Retrieve all team members assigned to a project."""
    members = team_service.get_team_members(db, project_id=project_id, owner_id=current_user.id)
    return members


@router.post("/", response_model=TeamMemberResponse, status_code=status.HTTP_201_CREATED)
def add_team_member(
    *,
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    member_in: TeamMemberCreate
) -> TeamMemberResponse:
    """Add a new developer/member to a project and associate their skills."""
    member = team_service.add_team_member(
        db, project_id=project_id, member_in=member_in, owner_id=current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or unauthorized access."
        )
    return member


@router.put("/{member_id}", response_model=TeamMemberResponse)
def update_team_member(
    *,
    project_id: str,
    member_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    member_in: TeamMemberUpdate
) -> TeamMemberResponse:
    """Update a team member's metadata and technology skills."""
    member = team_service.update_team_member(
        db, project_id=project_id, member_id=member_id, member_in=member_in, owner_id=current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member or Project not found, or unauthorized access."
        )
    return member


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team_member(
    *,
    project_id: str,
    member_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Remove a team member from a project."""
    success = team_service.delete_team_member(
        db, project_id=project_id, member_id=member_id, owner_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team member or Project not found, or unauthorized access."
        )
    return None
