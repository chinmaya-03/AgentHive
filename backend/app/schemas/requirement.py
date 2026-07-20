"""
Pydantic schemas for Requirement Document upload and response payloads.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, computed_field


class RequirementCreate(BaseModel):
    project_id: str
    original_filename: str
    stored_filename: str
    file_extension: str
    mime_type: str
    file_size: int
    extracted_text: Optional[str] = None
    processing_status: str = "Pending"
    uploaded_by: Optional[str] = None


class RequirementUpdate(BaseModel):
    extracted_text: Optional[str] = None
    processing_status: Optional[str] = None


class RequirementResponse(BaseModel):
    id: str
    project_id: str
    original_filename: str
    stored_filename: str
    file_extension: str
    mime_type: str
    file_size: int
    extracted_text: Optional[str] = None
    processing_status: str
    uploaded_by: Optional[str] = None
    upload_timestamp: datetime

    @computed_field
    def filename(self) -> str:
        return self.original_filename

    @computed_field
    def file_type(self) -> str:
        return self.file_extension.replace(".", "").upper() if self.file_extension else "TXT"

    @computed_field
    def status(self) -> str:
        return self.processing_status

    @computed_field
    def created_at(self) -> datetime:
        return self.upload_timestamp

    model_config = ConfigDict(from_attributes=True)
