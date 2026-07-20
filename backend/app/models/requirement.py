"""
SQLAlchemy database model for Requirement Documents.
Stores metadata for uploaded SRS documents (PDF, DOCX, TXT) and extracted text.
"""

import uuid
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database.base import Base, utcnow


class RequirementDocument(Base):
    __tablename__ = "requirement_documents"

    id: Any = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Any = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Metadata fields requested in Phase 2
    original_filename: Any = Column(String(255), nullable=False)
    stored_filename: Any = Column(String(255), nullable=False)
    file_extension: Any = Column(String(10), nullable=False)
    mime_type: Any = Column(String(100), nullable=False)
    file_size: Any = Column(Integer, nullable=False, default=0)
    
    extracted_text: Any = Column(Text, nullable=True)
    processing_status: Any = Column(String(50), default="Pending", nullable=False)  # Pending, Processed, Failed
    uploaded_by: Any = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    upload_timestamp: Any = Column(DateTime, default=utcnow, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="requirements")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    # Backward compatibility properties
    @property
    def filename(self) -> str:
        return self.original_filename

    @property
    def file_path(self) -> str:
        import os
        return os.path.join("uploads", self.stored_filename)

    @property
    def file_type(self) -> str:
        return self.file_extension.replace(".", "").upper()

    @property
    def status(self) -> str:
        return self.processing_status

    @property
    def created_at(self) -> datetime:
        return self.upload_timestamp
