"""
Agent definition and Task configurations for the Risk Analysis Agent.
"""

from crewai import Agent, Task
from app.schemas import ai as schemas
from app.prompts.risk_prompt import RISK_SYSTEM_PROMPT, RISK_ANALYSIS_PROMPT


from app.services.ai_service import get_llm


def create_risk_analysis_agent(llm=None) -> Agent:
    """Instantiate the Risk Analysis Agent."""
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Risk Assessor & Solutions Architect",
        goal="Audit sprint plans, assignments, and workloads for potential blockers, overloaded developers, or skill gaps.",
        backstory=RISK_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )



def create_risk_analysis_task(agent: Agent, sprint_plan_json: str) -> Task:
    """Build the Task configuration for Risk Analysis."""
    return Task(
        description=RISK_ANALYSIS_PROMPT.format(sprint_plan_json=sprint_plan_json),
        expected_output="A structured JSON array containing identified risk categories, descriptions, severity, and mitigations.",
        agent=agent,
        output_json=schemas.RiskAnalysisOutput
    )
