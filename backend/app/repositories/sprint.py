"""
Repository for Sprint database CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.sprint import Sprint
from app.models.task import SprintTask
from app.repositories.base import CRUDBase


class CRUDSprint(CRUDBase[Sprint, BaseModel, BaseModel]):
    def get_by_project(self, db: Session, project_id: str) -> List[Sprint]:
        """Fetch all sprints scheduled for a project."""
        return db.query(self.model).filter(self.model.project_id == project_id).all()

    def get_sprint_tasks(self, db: Session, sprint_id: str) -> List[SprintTask]:
        """Fetch all sprint task mapping relations."""
        return db.query(SprintTask).filter(SprintTask.sprint_id == sprint_id).all()


sprint_repo = CRUDSprint(Sprint)
