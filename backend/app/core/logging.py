"""
Logging setup for the AgentHive FastAPI application.
Configures handlers, levels, and formatters for debugging and auditing.
"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Initializes global logging formatters and stream handlers.
    Sets levels for FastAPI, CrewAI, and SQL libraries.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Standard format containing timestamps, module logger names, levels, and messages
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console output handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Root Logger initialization
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Ensure handlers are not duplicated on server reload
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
    else:
        # Re-apply formatters to existing handlers
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)
            handler.setLevel(log_level)
            
    # Quiet down external noisy packages (e.g. databases, HTTP clients)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


# Expose modular audit loggers
auth_logger = logging.getLogger("agenthive.auth")
ai_logger = logging.getLogger("agenthive.ai")
db_logger = logging.getLogger("agenthive.db")
