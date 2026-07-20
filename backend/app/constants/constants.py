"""
Global constants and configuration boundaries for AgentHive.
Avoids magic strings across the application.
"""

# Default LLM Parameters
DEFAULT_LLM_TEMPERATURE = 0.2
DEFAULT_LLM_MAX_RETRIES = 3
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"

# File Upload Boundaries
ALLOWED_REQUIREMENT_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_REQUIREMENT_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

# Task Breakdown Categories
TASK_CATEGORIES = [
    "Backend",
    "Frontend",
    "Database",
    "Testing",
    "DevOps",
]

# Task Difficulty Levels
DIFFICULTY_LEVELS = [
    "Easy",
    "Medium",
    "Hard",
]

# Sprint Defaults
DEFAULT_SPRINT_DURATION_WEEKS = 2
MAX_DEFAULT_SPRINTS = 4
