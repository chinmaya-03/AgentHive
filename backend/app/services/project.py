"""
Project Service implementing business logic for project ownership and operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.repositories.project import project_repo


class ProjectService:
    @staticmethod
    def get_projects(
        db: Session, *, owner_id: str, skip: int = 0, limit: int = 100
    ) -> List[Project]:
        """Get all projects belonging to the current user."""
        return project_repo.get_multi_by_owner(db, owner_id=owner_id, skip=skip, limit=limit)

    @staticmethod
    def get_project(db: Session, *, project_id: str, owner_id: str) -> Optional[Project]:
        """Fetch a project, validating that it belongs to the requesting user."""
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            return None
        return project

    @staticmethod
    def create_project(db: Session, *, project_in: ProjectCreate, owner_id: str) -> Project:
        """Create a new project associated with the owner user ID."""
        db_obj = Project(
            name=project_in.name,
            description=project_in.description,
            status=project_in.status,
            owner_id=owner_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update_project(
        db: Session, *, project_id: str, project_in: ProjectUpdate, owner_id: str
    ) -> Optional[Project]:
        """Update project details after verifying ownership."""
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            return None
        return project_repo.update(db, db_obj=project, obj_in=project_in)

    @staticmethod
    def delete_project(db: Session, *, project_id: str, owner_id: str) -> bool:
        """Delete a project after verifying ownership. Returns True if successful."""
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            return False
        project_repo.remove(db, id=project_id)
        return True


project_service = ProjectService()
