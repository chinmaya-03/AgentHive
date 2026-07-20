"""
CrewAI Sprint Planning Agent definition and task builder.
Consumes TaskBreakdownResult and SkillMatchingResult to organize engineering tasks into balanced, dependency-aware Agile sprints.
"""

import logging
from crewai import Agent, Task, Crew, Process
from app.services.ai_service import get_llm
from app.prompts.sprint_prompt import SPRINT_SYSTEM_PROMPT, SPRINT_PLANNING_PROMPT
from app.schemas.ai import SprintPlanResult

logger = logging.getLogger(__name__)


def create_sprint_planning_agent(llm=None) -> Agent:
    """
    Instantiates the CrewAI Sprint Planning Agent using the centralized LLM instance.
    """
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Agile Project Manager & Sprint Planning Specialist",
        goal="Organize engineering tasks into balanced, dependency-aware Agile sprints respecting developer roles, story points, and dependency chains.",
        backstory=SPRINT_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )


def create_sprint_planning_task(agent: Agent, assigned_tasks_json: str) -> Task:
    """
    Builds the CrewAI Task for Sprint Planning expecting structured output matching SprintPlanResult.
    """
    prompt_description = SPRINT_PLANNING_PROMPT.format(assigned_tasks_json=assigned_tasks_json)
    prompt_description += (
        "\n\nCRITICAL CONSTRAINTS FOR SPRINT PLANNING:\n"
        "1. Never violate dependencies: A task MUST NOT be scheduled in an earlier sprint than its prerequisite dependencies.\n"
        "2. Prefer backend and database setup tasks in Sprint 1 before frontend integration tasks in later sprints.\n"
        "3. Schedule authentication and security endpoints before protected API endpoints.\n"
        "4. Target balanced sprint sizes of roughly 15-25 total story points per sprint.\n"
        "5. Ensure every task retains its assigned developer role.\n"
        "6. Generate a clear business/technical goal for each sprint."
    )

    return Task(
        description=prompt_description,
        expected_output=(
            "A structured JSON object with key 'sprints', containing sprint_name, goal, total_story_points, "
            "and tasks (with task_title, assigned_role, story_points) for each sprint."
        ),
        agent=agent,
        output_json=SprintPlanResult
    )


def run_sprint_planning(assigned_tasks_json: str) -> str:
    """
    Executes the CrewAI Sprint Planning Task and returns the raw agent result string.
    """
    logger.info("Initializing Sprint Planning Agent and Crew execution...")
    agent = create_sprint_planning_agent()
    task = create_sprint_planning_task(agent, assigned_tasks_json)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    logger.info("Sprint Planning Agent execution completed.")
    return str(result)
