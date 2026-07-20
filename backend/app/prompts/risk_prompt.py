"""
Modular prompt templates for the Risk Analysis Agent.
"""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

RISK_SYSTEM_PROMPT = (
    "Audit sprint plans, assignments, and workloads for potential blockers, overloaded developers, skill gaps, "
    "sprint overflow risks, and compile actionable mitigation recommendations."
)

RISK_ANALYSIS_PROMPT = (
    "Critically audit the finalized sprint plan and allocations:\n\n"
    "{sprint_plan_json}\n\n"
    "Identify potential risks that could derail this project. Focus on:\n"
    "- Overloaded developers (developers assigned too many hours in a single sprint)\n"
    "- Skill gaps (tasks assigned to developers lacking relevant skill tags)\n"
    "- Sprint overload (sprints with too much load)\n"
    "- Dependency conflicts (tasks planned before their parent dependency tasks)\n"
    "- Missing resources or high-risk architectural tasks\n\n"
    "For each risk, provide its category/type, a detailed explanation, severity level (Low, Medium, High), "
    "and a concrete mitigation recommendation."
)

def get_risk_prompt_template() -> ChatPromptTemplate:
    """Returns a compiled LangChain ChatPromptTemplate for Risk Analysis."""
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(RISK_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(RISK_ANALYSIS_PROMPT),
    ])
