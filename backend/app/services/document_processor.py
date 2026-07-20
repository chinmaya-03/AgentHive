"""
Document Processor Service using PyMuPDF (fitz) and python-docx.
Extracts raw text content from PDF, DOCX, and TXT requirement documents.
"""

import os
import fitz  # PyMuPDF
import docx
from fastapi import UploadFile


class DocumentProcessor:
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """
        Extract text from a file based on its file type (PDF, DOCX, TXT).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")

        file_type = file_type.upper()

        if file_type == "PDF":
            return DocumentProcessor._extract_pdf(file_path)
        elif file_type in ("DOCX", "DOC"):
            return DocumentProcessor._extract_docx(file_path)
        elif file_type == "TXT":
            return DocumentProcessor._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_type}")

    @staticmethod
    def _extract_pdf(file_path: str) -> str:
        """Extract text from a PDF file using PyMuPDF."""
        text: list[str] = []
        try:
            # Open PDF file
            doc = fitz.open(file_path)
            for page in doc:
                text.append(str(page.get_text()))
            doc.close()
        except Exception as e:
            raise RuntimeError(f"Error reading PDF file: {str(e)}")
            
        return "\n".join(text)

    @staticmethod
    def _extract_docx(file_path: str) -> str:
        """Extract text from a DOCX file using python-docx."""
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text)
        except Exception as e:
            raise RuntimeError(f"Error reading DOCX file: {str(e)}")

    @staticmethod
    def _extract_txt(file_path: str) -> str:
        """Extract text from a plain TXT file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Error reading TXT file: {str(e)}")


document_processor = DocumentProcessor()
