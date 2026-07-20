"""
API Endpoints for global Skills Registry.
"""

from typing import List, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import deps
from app.schemas.skill import SkillCreate, SkillResponse
from app.services.team import team_service

router = APIRouter()


@router.get("/", response_model=List[SkillResponse])
def get_skills(
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> Any:
    """Retrieve all technical skills in the registry."""
    return team_service.get_skills(db)


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user),
    skill_in: SkillCreate
) -> Any:
    """Create a new technology skill in the global registry."""
    return team_service.create_skill(db, skill_in=skill_in)
