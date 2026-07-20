"""
CrewAI Task Breakdown Agent definition and task builder.
Converts structured RequirementAnalysisResult into Epics, User Stories, and Technical Engineering Tasks.
"""

import logging
from crewai import Agent, Task, Crew, Process
from app.services.ai_service import get_llm
from app.prompts.task_prompt import TASK_SYSTEM_PROMPT, TASK_BREAKDOWN_PROMPT
from app.schemas.ai import TaskBreakdownResult

logger = logging.getLogger(__name__)


def create_task_breakdown_agent(llm=None) -> Agent:
    """
    Instantiates the CrewAI Task Breakdown Agent using the centralized LLM instance.
    """
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Technical Lead & Agile Software Architect",
        goal="Decompose requirement analysis results into high-level Epics, User Stories, and actionable technical tasks with story points and dependencies.",
        backstory=TASK_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )


def create_task_breakdown_task(agent: Agent, requirement_analysis_json: str) -> Task:
    """
    Builds the CrewAI Task for task breakdown expecting structured output matching TaskBreakdownResult.
    """
    return Task(
        description=TASK_BREAKDOWN_PROMPT.format(requirement_analysis_json=requirement_analysis_json),
        expected_output=(
            "A structured JSON object with keys: epics, user_stories, technical_tasks. "
            "Each technical_task must contain title, description, story_points, priority, and dependencies."
        ),
        agent=agent,
        output_json=TaskBreakdownResult
    )


def run_task_breakdown(requirement_analysis_json: str) -> str:
    """
    Executes the CrewAI Task Breakdown Task and returns the raw agent result string.
    """
    logger.info("Initializing Task Breakdown Agent and Crew execution...")
    agent = create_task_breakdown_agent()
    task = create_task_breakdown_task(agent, requirement_analysis_json)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    logger.info("Task Breakdown Agent execution completed.")
    return str(result)
