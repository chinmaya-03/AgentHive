"""
Custom exception hierarchy for the AgentHive application.
Provides domain-specific exceptions for AI configuration, document parsing, and agent execution.
"""

class AgentHiveException(Exception):
    """Base exception for all AgentHive domain errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class AIConfigurationError(AgentHiveException):
    """Raised when AI settings or API keys are missing or invalid."""
    def __init__(self, message: str = "Invalid or missing AI configuration."):
        super().__init__(message=message, code="AI_CONFIG_ERROR")


class FileParsingError(AgentHiveException):
    """Raised when document extraction (PDF, DOCX, TXT) fails."""
    def __init__(self, message: str = "Failed to parse document content."):
        super().__init__(message=message, code="FILE_PARSING_ERROR")


class AgentExecutionError(AgentHiveException):
    """Raised when an AI Agent fails during task execution."""
    def __init__(self, agent_name: str, reason: str):
        message = f"Agent '{agent_name}' failed to complete task: {reason}"
        super().__init__(message=message, code="AGENT_EXECUTION_ERROR")
        self.agent_name = agent_name
        self.reason = reason
