"""
Modular prompt templates for the Sprint Planning Agent.
"""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

SPRINT_SYSTEM_PROMPT = (
    "Structure assigned tasks into balanced sprints (Sprint 1, Sprint 2, Sprint 3, etc.), "
    "respecting task dependency chains, balancing total team sprint capacity, and setting sprint goals."
)

SPRINT_PLANNING_PROMPT = (
    "Review the list of assigned engineering tasks and their dependencies:\n\n"
    "{assigned_tasks_json}\n\n"
    "Structure the tasks into a sprint plan consisting of Sprint 1, Sprint 2, and Sprint 3 (and Sprint 4 if necessary).\n"
    "Ensure that:\n"
    "- Tasks that depend on others are scheduled after their dependencies (e.g., Database tasks or core APIs in Sprint 1, frontend integrations in Sprint 2).\n"
    "- Total effort in hours is balanced across sprints based on team capacity.\n"
    "- Each sprint has a clear goal summarizing its business/technical objective."
)

def get_sprint_prompt_template() -> ChatPromptTemplate:
    """Returns a compiled LangChain ChatPromptTemplate for Sprint Planning."""
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SPRINT_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(SPRINT_PLANNING_PROMPT),
    ])
