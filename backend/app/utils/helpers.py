"""
General utility helper functions for AgentHive backend.
"""

import json
import re
from typing import Any, Dict, Union, List


def clean_text(text: str) -> str:
    """
    Sanitizes raw text strings by stripping excess whitespace and normalizing line breaks.
    """
    if not text:
        return ""
    # Normalize multiple blank lines into max 2 newlines
    lines = [line.strip() for line in text.splitlines()]
    result = "\n".join(lines)
    return re.sub(r"\n{3,}", "\n\n", result).strip()


def extract_json_from_llm_output(output_text: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Parses JSON output returned by an LLM agent. Handles Markdown fenced code blocks
    (e.g., ```json ... ```) or plain text JSON strings.
    
    :param output_text: Raw string returned from LLM
    :return: Parsed dictionary or list
    :raises ValueError: If valid JSON cannot be extracted
    """
    if not output_text or not output_text.strip():
        raise ValueError("LLM returned empty output text.")

    cleaned = output_text.strip()

    # Match JSON contained inside ```json ... ``` or ``` ... ``` code blocks
    json_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned, re.IGNORECASE)
    if json_block_match:
        cleaned = json_block_match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as err:
        # Fallback regex search for bare JSON object or list if extra commentary exists
        json_obj_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if json_obj_match:
            try:
                return json.loads(json_obj_match.group(1))
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Failed to parse valid JSON from LLM response: {str(err)}")
