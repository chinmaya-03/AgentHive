"""
Agent definition and Task configurations for the Skill Matching Agent.
"""

from crewai import Agent, Task
from app.schemas import ai as schemas
from app.prompts.skill_prompt import COORDINATOR_SKILL_SYSTEM_PROMPT, SKILL_MEMBER_MATCHING_PROMPT


from app.services.ai_service import get_llm


def create_skill_matching_agent(llm=None) -> Agent:
    """Instantiate the Skill Matching Agent."""
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Engineering Resource Manager",
        goal="Assign engineering tasks to available team members based on skills, roles, and capacity.",
        backstory=COORDINATOR_SKILL_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )



def create_skill_matching_task(agent: Agent, tasks_json: str, team_members_json: str = "") -> Task:
    """Build the Task configuration for Skill Matching."""
    return Task(
        description=SKILL_MEMBER_MATCHING_PROMPT.format(
            task_breakdown_json=tasks_json,
            team_members_json=team_members_json
        ),
        expected_output="A structured JSON mapping of task assignments to developer IDs and names with matching rationale.",
        agent=agent,
        output_json=schemas.SkillMatchingOutput
    )

