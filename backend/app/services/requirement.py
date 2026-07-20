"""
Service layer managing Requirement Document upload, validation, parsing, and storage lifecycle.
"""

import logging
import os
import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.requirement import RequirementDocument
from app.repositories.project import project_repo
from app.repositories.requirement import requirement_repo
from app.utils.file_parser import parse_document
from app.utils.validators import validate_file_extension, validate_file_size, validate_extracted_text
from app.core.exceptions import FileParsingError

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "application/octet-stream"  # Common fallback for browsers uploading plain/binary streams
}


class RequirementService:
    @staticmethod
    def get_project_requirements(
        db: Session, *, project_id: str, owner_id: str
    ) -> List[RequirementDocument]:
        """Fetch all requirement documents uploaded for a specific project, verifying user ownership."""
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            return []
        return requirement_repo.get_by_project(db, project_id=project_id)

    @staticmethod
    def get_all_user_requirements(
        db: Session, *, owner_id: str, project_id: Optional[str] = None
    ) -> List[RequirementDocument]:
        """Fetch requirements owned by user, optionally filtered by project_id."""
        if project_id:
            return RequirementService.get_project_requirements(db, project_id=project_id, owner_id=owner_id)

        # Get all projects owned by current user
        user_projects = db.query(RequirementDocument).join(
            RequirementDocument.project
        ).filter(
            RequirementDocument.project.has(owner_id=owner_id)
        ).order_by(RequirementDocument.upload_timestamp.desc()).all()

        return user_projects

    @staticmethod
    def get_requirement(
        db: Session, *, requirement_id: str, owner_id: str
    ) -> Optional[RequirementDocument]:
        """Retrieve a requirement document by ID, verifying project ownership."""
        doc = requirement_repo.get(db, id=requirement_id)
        if not doc:
            return None

        project = project_repo.get(db, id=doc.project_id)
        if not project or project.owner_id != owner_id:
            return None

        return doc

    @staticmethod
    def upload_requirement(
        db: Session, *, project_id: str, file: UploadFile, owner_id: str
    ) -> RequirementDocument:
        """
        Processes and stores an uploaded SRS requirement document.
        Validates file metadata, saves file cleanly, extracts raw text via file_parser,
        and records entry in database.
        """
        # Step 1: Verify project ownership
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            raise ValueError("Project not found or user unauthorized to upload requirements.")

        # Step 2: Validate file name and extension
        original_filename = file.filename or "requirement.txt"
        validate_file_extension(original_filename)

        # Step 3: Validate mime type
        mime_type = file.content_type or "application/octet-stream"
        if mime_type.lower() not in ALLOWED_MIME_TYPES:
            raise FileParsingError(
                f"Unsupported MIME type '{mime_type}'. Supported file formats: PDF, DOCX, TXT."
            )

        # Step 4: Read file content and validate size
        file_bytes = file.file.read()
        file_size = len(file_bytes)
        validate_file_size(file_size)

        if file_size == 0:
            raise FileParsingError("Uploaded file is empty (0 bytes).")

        # Step 5: Ensure uploads directory exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Step 6: Generate unique filename (never overwrite existing files)
        file_extension = Path(original_filename).suffix.lower()
        unique_prefix = uuid.uuid4().hex[:12]
        sanitized_base = Path(original_filename).stem.replace(" ", "_")
        stored_filename = f"{unique_prefix}_{sanitized_base}{file_extension}"
        stored_file_path = UPLOAD_DIR / stored_filename

        # Save to disk
        try:
            with open(stored_file_path, "wb") as buffer:
                buffer.write(file_bytes)
            logger.info(f"File uploaded successfully to disk: {stored_file_path}")
        except Exception as e:
            logger.error(f"Failed to write file to disk: {str(e)}")
            raise RuntimeError(f"Could not save file to server storage: {str(e)}")

        # Step 7: Parse document text automatically using file_parser
        extracted_text = None
        processing_status = "Pending"

        try:
            raw_text = parse_document(original_filename, file_bytes)
            extracted_text = validate_extracted_text(raw_text)
            processing_status = "Processed"
            logger.info(f"Extraction completed for document '{original_filename}': {len(extracted_text)} chars extracted.")
        except Exception as e:
            logger.error(f"Extraction failed for document '{original_filename}': {str(e)}")
            processing_status = "Failed"
            extracted_text = f"Parsing Error: {str(e)}"

        # Step 8: Persist to database via repository
        doc_data = {
            "project_id": project_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_extension": file_extension,
            "mime_type": mime_type,
            "file_size": file_size,
            "extracted_text": extracted_text,
            "processing_status": processing_status,
            "uploaded_by": owner_id,
        }

        db_doc = requirement_repo.create_with_metadata(db, obj_in_data=doc_data)
        
        if processing_status == "Failed":
            # If text extraction failed, raise error after recording failure in DB
            raise FileParsingError(f"Document upload failed text extraction: {extracted_text}")

        return db_doc

    @staticmethod
    def delete_requirement(db: Session, *, requirement_id: str, owner_id: str) -> bool:
        """Deletes a requirement document from disk and database."""
        doc = RequirementService.get_requirement(db, requirement_id=requirement_id, owner_id=owner_id)
        if not doc:
            return False

        # Remove physical file from disk
        file_path = UPLOAD_DIR / doc.stored_filename
        if file_path.exists():
            try:
                os.remove(file_path)
                logger.info(f"Deleted physical file from disk: {file_path}")
            except Exception as e:
                logger.warning(f"Could not delete physical file {file_path}: {str(e)}")

        requirement_repo.remove(db, id=requirement_id)
        logger.info(f"Deleted requirement document record ID: {requirement_id}")
        return True


requirement_service = RequirementService()
