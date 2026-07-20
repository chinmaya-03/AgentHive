"""
Repository for Team Member database CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.team import TeamMember, TeamMemberSkill
from app.schemas.team import TeamMemberCreate, TeamMemberUpdate
from app.repositories.base import CRUDBase


class CRUDTeam(CRUDBase[TeamMember, TeamMemberCreate, TeamMemberUpdate]):
    def get_by_project(self, db: Session, project_id: str) -> List[TeamMember]:
        """Fetch all team members assigned to a project."""
        return db.query(self.model).filter(self.model.project_id == project_id).all()

    def get_by_project_and_id(self, db: Session, project_id: str, member_id: str) -> Optional[TeamMember]:
        """Fetch a specific project team member."""
        return (
            db.query(self.model)
            .filter(self.model.project_id == project_id, self.model.id == member_id)
            .first()
        )


team_repo = CRUDTeam(TeamMember)
