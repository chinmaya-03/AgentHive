"""
Modular prompt templates for the Requirement Analysis Agent.
"""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

REQUIREMENT_SYSTEM_PROMPT = (
    "You are a Senior Business Analyst & Software Systems Architect. "
    "Your role is to analyze Software Requirement Specifications (SRS), extract functional and non-functional requirements, "
    "detect missing scope items, flag ambiguous statements, estimate project complexity, and produce structured analysis JSON."
)

REQUIREMENT_TASK_PROMPT = (
    "Analyze the following Software Requirement Specification (SRS) text:\n\n"
    "--- START SRS TEXT ---\n{srs_text}\n--- END SRS TEXT ---\n\n"
    "Perform a system requirement analysis. Output MUST be a valid JSON object formatted EXACTLY as follows:\n\n"
    "{{\n"
    '  "project_summary": "Concise executive overview of the software project scope",\n'
    '  "functional_requirements": ["Functional requirement 1", "Functional requirement 2"],\n'
    '  "non_functional_requirements": ["Non-functional requirement 1 (e.g. security, performance, SLA)"],\n'
    '  "missing_requirements": ["Identified gap or omitted requirement 1"],\n'
    '  "ambiguities": ["Vague or ambiguous statement 1 requiring developer clarification"],\n'
    '  "complexity": "Low" | "Medium" | "High"\n'
    "}}\n\n"
    "Ensure your output contains strictly valid JSON."
)

def get_requirement_prompt_template() -> ChatPromptTemplate:
    """Returns a compiled LangChain ChatPromptTemplate for Requirement Analysis."""
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(REQUIREMENT_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(REQUIREMENT_TASK_PROMPT),
    ])
