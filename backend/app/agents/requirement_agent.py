"""
CrewAI Requirement Analysis Agent definition and task builder.
Analyzes SRS text to identify functional/non-functional requirements, missing items, ambiguities, and project complexity.
"""

import logging
from crewai import Agent, Task, Crew, Process
from app.services.ai_service import get_llm
from app.prompts.requirement_prompt import REQUIREMENT_SYSTEM_PROMPT, REQUIREMENT_TASK_PROMPT
from app.schemas.ai import RequirementAnalysisResult

logger = logging.getLogger(__name__)


def create_requirement_agent(llm=None) -> Agent:
    """
    Instantiates the CrewAI Requirement Analysis Agent using the provided LLM instance
    or centralized fallback get_llm().
    """
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Business Analyst & Software Architect",
        goal="Extract project summary, functional/non-functional requirements, missing items, ambiguities, and complexity rating from SRS text.",
        backstory=REQUIREMENT_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )


def create_requirement_task(agent: Agent, srs_text: str) -> Task:
    """
    Builds the CrewAI Task for requirement analysis expecting structured output matching RequirementAnalysisResult.
    """
    return Task(
        description=REQUIREMENT_TASK_PROMPT.format(srs_text=srs_text),
        expected_output=(
            "A structured JSON object with keys: project_summary, functional_requirements, "
            "non_functional_requirements, missing_requirements, ambiguities, complexity."
        ),
        agent=agent,
        output_json=RequirementAnalysisResult
    )


def run_requirement_analysis(srs_text: str) -> str:
    """
    Executes the CrewAI Requirement Analysis Task and returns the raw agent result string.
    """
    logger.info("Initializing Requirement Analysis Agent and Crew execution...")
    agent = create_requirement_agent()
    task = create_requirement_task(agent, srs_text)
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    logger.info("Requirement Analysis Agent execution completed.")
    return str(result)
