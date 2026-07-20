"""
Repository for Task database CRUD operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.task import Task, TaskAssignment
from app.repositories.base import CRUDBase


class CRUDTask(CRUDBase[Task, BaseModel, BaseModel]):
    def get_by_project(self, db: Session, project_id: str) -> List[Task]:
        """Fetch all tasks for a specific project."""
        return db.query(self.model).filter(self.model.project_id == project_id).all()

    def get_task_assignments(self, db: Session, task_id: str) -> List[TaskAssignment]:
        """Fetch all assignments for a task."""
        return db.query(TaskAssignment).filter(TaskAssignment.task_id == task_id).all()


task_repo = CRUDTask(Task)
