"""
Repository layer for Requirement Documents database operations.
Encapsulates all SQLAlchemy queries for requirement objects.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.requirement import RequirementDocument
from app.schemas.requirement import RequirementCreate, RequirementUpdate
from app.repositories.base import CRUDBase


class CRUDRequirement(CRUDBase[RequirementDocument, RequirementCreate, RequirementUpdate]):
    def get_by_project(self, db: Session, *, project_id: str) -> List[RequirementDocument]:
        """Fetch all requirement documents associated with a specific project."""
        return (
            db.query(RequirementDocument)
            .filter(RequirementDocument.project_id == project_id)
            .order_by(RequirementDocument.upload_timestamp.desc())
            .all()
        )

    def get_by_id_and_project(
        self, db: Session, *, requirement_id: str, project_id: str
    ) -> Optional[RequirementDocument]:
        """Fetch a specific requirement document for a project."""
        return (
            db.query(RequirementDocument)
            .filter(
                RequirementDocument.id == requirement_id,
                RequirementDocument.project_id == project_id
            )
            .first()
        )

    def create_with_metadata(
        self, db: Session, *, obj_in_data: dict
    ) -> RequirementDocument:
        """Creates a requirement document record from a dictionary of metadata."""
        db_obj = RequirementDocument(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


requirement_repo = CRUDRequirement(RequirementDocument)
