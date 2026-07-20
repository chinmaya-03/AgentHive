"""
CrewAI Skill Matching Agent definition and task builder.
Analyzes TaskBreakdownResult to determine required developer role, experience level, required skills, recommended tools, and assignment reasoning.
"""

import logging
from crewai import Agent, Task, Crew, Process
from app.services.ai_service import get_llm
from app.prompts.skill_prompt import SKILL_SYSTEM_PROMPT, SKILL_ROLE_MATCHING_PROMPT
from app.schemas.ai import SkillMatchingResult

logger = logging.getLogger(__name__)


def create_skill_matching_agent(llm=None) -> Agent:
    """
    Instantiates the CrewAI Skill Matching Agent using the centralized LLM instance.
    """
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Engineering Manager & Technical Skill Architect",
        goal="Determine developer roles, required technical skills, experience levels, and recommended tools for each engineering task.",
        backstory=SKILL_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )


def create_skill_matching_task(agent: Agent, task_breakdown_json: str) -> Task:
    """
    Builds the CrewAI Task for skill matching expecting structured output matching SkillMatchingResult.
    """
    return Task(
        description=SKILL_ROLE_MATCHING_PROMPT.format(task_breakdown_json=task_breakdown_json),
        expected_output=(
            "A structured JSON object with key 'assignments', containing task_title, developer_role, "
            "experience_level, skills, recommended_tools, and reason for every engineering task."
        ),
        agent=agent,
        output_json=SkillMatchingResult
    )


def run_skill_matching(task_breakdown_json: str) -> str:
    """
    Executes the CrewAI Skill Matching Task and returns the raw agent result string.
    """
    logger.info("Initializing Skill Matching Agent and Crew execution...")
    agent = create_skill_matching_agent()
    task = create_skill_matching_task(agent, task_breakdown_json)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    logger.info("Skill Matching Agent execution completed.")
    return str(result)
