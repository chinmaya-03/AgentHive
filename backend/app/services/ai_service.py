"""
AI Service Provider Infrastructure for AgentHive.
Provides centralized, validated instantiation of CrewAI LLM instances.
"""

import os
from typing import Optional
from crewai import LLM

from app.core.config import settings
from app.core.exceptions import AIConfigurationError

import tempfile

# Ensure environment variables for CrewAI, tiktoken, & Windows C-extensions are initialized
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OPENBLAS_MAIN_FREE"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set tiktoken cache directory in backend directory (D drive)
temp_cache = os.path.join(backend_dir, ".tiktoken_cache")
os.makedirs(temp_cache, exist_ok=True)
os.environ["TIKTOKEN_CACHE_DIR"] = temp_cache

# Set CrewAI storage directory in backend directory (D drive)
crewai_storage = os.path.join(backend_dir, ".crewai_storage")
os.makedirs(crewai_storage, exist_ok=True)
os.environ["CREWAI_STORAGE_DIR"] = crewai_storage




if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "NA"


class AIServiceProvider:
    """
    Singleton factory for managing AI Language Model (LLM) instances across AgentHive.
    Enforces global LLM settings and CrewAI compatibility.
    """
    _llm_instance: Optional[LLM] = None

    @classmethod
    def get_llm(cls, temperature: float = 0.2, max_retries: int = 3) -> LLM:
        """
        Validates AI environment configuration and returns a reusable CrewAI LLM instance.
        """
        provider = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else "groq"

        if provider in ("google", "gemini"):
            api_key = settings.GEMINI_API_KEY
            if not api_key or not api_key.strip():
                raise AIConfigurationError(
                    "GEMINI_API_KEY is missing or empty in environment settings. "
                    "Please set GEMINI_API_KEY=... in your backend/.env configuration."
                )
            model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
            if not model_name.startswith("gemini/"):
                model_name = f"gemini/{model_name}"
            
            return LLM(
                model=model_name,
                api_key=api_key,
                temperature=temperature,
                max_retries=max_retries,
            )
        else:
            api_key = settings.GROQ_API_KEY
            if not api_key or not api_key.strip():
                raise AIConfigurationError(
                    "GROQ_API_KEY is missing or empty in environment settings. "
                    "Please set GROQ_API_KEY=gsk_... in your backend/.env configuration."
                )
            model_name = settings.GROQ_MODEL or "llama-3.3-70b-versatile"
            if not model_name.startswith("groq/"):
                model_name = f"groq/{model_name}"

            os.environ["GROQ_API_KEY"] = api_key

            return LLM(
                model=model_name,
                api_key=api_key,
                temperature=temperature,
                max_retries=max_retries,
            )


def get_llm(temperature: float = 0.2, max_retries: int = 3) -> LLM:
    """
    Exposes a reusable, validated CrewAI LLM instance.
    Never initialize LLM directly inside individual agents; always use get_llm().
    """
    return AIServiceProvider.get_llm(temperature=temperature, max_retries=max_retries)

