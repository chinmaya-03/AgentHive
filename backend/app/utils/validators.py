"""
Validation helper utilities for AgentHive backend.
"""

from pathlib import Path

from app.constants.constants import ALLOWED_REQUIREMENT_EXTENSIONS, MAX_REQUIREMENT_FILE_SIZE_BYTES
from app.core.exceptions import FileParsingError, AIConfigurationError


def validate_file_extension(filename: str) -> None:
    """
    Validates that an uploaded file has a supported extension (.pdf, .docx, .txt).
    
    :raises FileParsingError: If file extension is unsupported
    """
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_REQUIREMENT_EXTENSIONS:
        supported = ", ".join(sorted(ALLOWED_REQUIREMENT_EXTENSIONS))
        raise FileParsingError(
            f"File format '{ext}' is not supported. Allowed extensions: {supported}"
        )


def validate_file_size(size_bytes: int) -> None:
    """
    Validates that an uploaded file does not exceed the maximum allowed size (10MB).
    
    :raises FileParsingError: If file size exceeds limit
    """
    if size_bytes > MAX_REQUIREMENT_FILE_SIZE_BYTES:
        max_mb = MAX_REQUIREMENT_FILE_SIZE_BYTES // (1024 * 1024)
        raise FileParsingError(f"File size exceeds maximum allowed limit of {max_mb} MB.")


def validate_groq_api_key_format(api_key: str) -> None:
    """
    Validates the format of a Groq API Key string.
    
    :raises AIConfigurationError: If API key is missing or improperly formatted
    """
    if not api_key or not isinstance(api_key, str) or not api_key.strip():
        raise AIConfigurationError("GROQ_API_KEY is missing or empty.")
    
    clean_key = api_key.strip()
    if not clean_key.startswith("gsk_"):
        raise AIConfigurationError(
            "Invalid GROQ_API_KEY format. Groq API keys must begin with 'gsk_' prefix."
        )


def validate_extracted_text(text: str) -> str:
    """
    Validates that extracted text content is non-empty and meets minimum requirements.
    
    :raises FileParsingError: If text is empty or contains insufficient content
    """
    if not text or not text.strip():
        raise FileParsingError("Extracted text content is completely empty.")
    
    cleaned = text.strip()
    if len(cleaned) < 20:
        raise FileParsingError("Extracted requirement text is too short to perform meaningful AI analysis.")
        
    return cleaned
