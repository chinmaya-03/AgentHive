"""
Agent definition and Task configurations for the Sprint Planning Agent.
"""

from crewai import Agent, Task
from app.schemas import ai as schemas
from app.prompts.sprint_prompt import SPRINT_SYSTEM_PROMPT, SPRINT_PLANNING_PROMPT


from app.services.ai_service import get_llm


def create_sprint_planning_agent(llm=None) -> Agent:
    """Instantiate the Sprint Planning Agent."""
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Agile Project Scrum Master",
        goal="Structure assigned tasks into balanced sprints respecting dependency chains.",
        backstory=SPRINT_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )



def create_sprint_planning_task(agent: Agent, assigned_tasks_json: str) -> Task:
    """Build the Task configuration for Sprint Planning."""
    return Task(
        description=SPRINT_PLANNING_PROMPT.format(assigned_tasks_json=assigned_tasks_json),
        expected_output="A structured JSON array representing sprints, their goals, grouped tasks, and total effort.",
        agent=agent,
        output_json=schemas.SprintPlanningOutput
    )
