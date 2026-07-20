"""
Modular prompt templates for the Task Breakdown Agent.
"""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

TASK_SYSTEM_PROMPT = (
    "You are a Senior Technical Lead & Agile Software Architect. "
    "Your role is to analyze structured requirement analysis outputs and break them down into high-level Epics, "
    "User Stories, and actionable technical engineering tasks with story points, priority ratings, and task dependencies."
)

TASK_BREAKDOWN_PROMPT = (
    "Review the following Requirement Analysis output:\n\n"
    "--- START REQUIREMENT ANALYSIS ---\n{requirement_analysis_json}\n--- END REQUIREMENT ANALYSIS ---\n\n"
    "Perform a comprehensive technical task breakdown. Output MUST be a valid JSON object formatted EXACTLY as follows:\n\n"
    "{{\n"
    '  "epics": ["Epic 1: System Authentication & User Authorization", "Epic 2: Requirement Document Management"],\n'
    '  "user_stories": ["As a user, I want to upload SRS files so that requirements are parsed automatically", "..."],\n'
    '  "technical_tasks": [\n'
    '    {{\n'
    '      "title": "Build File Parser Utility for PDF/DOCX/TXT",\n'
    '      "description": "Implement PyMuPDF and python-docx text extraction functions in app/utils/file_parser.py",\n'
    '      "story_points": 5,\n'
    '      "priority": "High",\n'
    '      "dependencies": []\n'
    '    }}\n'
    '  ]\n'
    "}}\n\n"
    "Rules for technical_tasks:\n"
    "1. story_points must be a standard Fibonacci number: 1, 2, 3, 5, 8, or 13.\n"
    "2. priority must be 'High', 'Medium', or 'Low'.\n"
    "3. dependencies must list task titles of prerequisite tasks that must be built first.\n"
    "Ensure your output contains strictly valid JSON."
)

def get_task_prompt_template() -> ChatPromptTemplate:
    """Returns a compiled LangChain ChatPromptTemplate for Task Breakdown."""
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(TASK_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(TASK_BREAKDOWN_PROMPT),
    ])
