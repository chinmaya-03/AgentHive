"""
Agent definition and Task configurations for the Task Breakdown Agent.
"""

from crewai import Agent, Task
from app.schemas import ai as schemas
from app.prompts.task_prompt import TASK_SYSTEM_PROMPT, TASK_BREAKDOWN_PROMPT


from app.services.ai_service import get_llm


def create_task_breakdown_agent(llm=None) -> Agent:
    """Instantiate the Task Breakdown Agent."""
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Technical Lead",
        goal="Break down functional modules and requirements into specific, detailed engineering tasks.",
        backstory=TASK_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )



def create_task_breakdown_task(agent: Agent, requirement_analysis_json: str) -> Task:
    """Build the Task configuration for Task Breakdown."""
    return Task(
        description=TASK_BREAKDOWN_PROMPT.format(requirement_analysis_json=requirement_analysis_json),
        expected_output="A structured JSON array of broken down engineering tasks.",
        agent=agent,
        output_json=schemas.TaskBreakdownOutput
    )
