"""
CrewAI Risk Analysis Agent definition and task builder.
Consumes SprintPlanResult, SkillMatchingResult, and TaskBreakdownResult to perform software execution risk analysis.
"""

import logging
from crewai import Agent, Task, Crew, Process
from app.services.ai_service import get_llm
from app.prompts.risk_prompt import RISK_SYSTEM_PROMPT, RISK_ANALYSIS_PROMPT
from app.schemas.ai import RiskAnalysisResult

logger = logging.getLogger(__name__)


def create_risk_analysis_agent(llm=None) -> Agent:
    """
    Instantiates the CrewAI Risk Analysis Agent using the centralized LLM instance.
    """
    if llm is None:
        llm = get_llm(temperature=0.2)
    return Agent(
        role="Senior Technical Risk Auditor & Software Quality Architect",
        goal="Audit sprint plans, developer skill assignments, and technical task breakdowns to identify execution risks, bottlenecks, role imbalances, and provide mitigation recommendations.",
        backstory=RISK_SYSTEM_PROMPT,
        verbose=False,
        allow_delegation=False,
        llm=llm
    )


def create_risk_analysis_task(agent: Agent, sprint_plan_json: str) -> Task:
    """
    Builds the CrewAI Task for Risk Analysis expecting structured output matching RiskAnalysisResult.
    """
    prompt_description = RISK_ANALYSIS_PROMPT.format(sprint_plan_json=sprint_plan_json)
    prompt_description += (
        "\n\nCRITICAL AUDIT RULES FOR RISK ANALYSIS:\n"
        "1. Detect Sprint Overload: Sprints with total story points exceeding 25 SP or hours exceeding capacity.\n"
        "2. Detect Dependency & Circular Dependency Conflicts: Tasks scheduled in a sprint prior to their prerequisite task dependencies.\n"
        "3. Detect Missing Developer Expertise: Tasks assigned to developer roles lacking necessary technical skills.\n"
        "4. Detect Task/Role Imbalances: Too many backend tasks or frontend tasks crammed into a single sprint.\n"
        "5. Detect Unrealistic Story Point Allocations & High-Risk Architectural Tasks.\n"
        "6. Detect Sequence Violations: Security/Authentication tasks scheduled too late or testing tasks scheduled after deployment.\n"
        "7. For every detected risk, generate a concrete, actionable mitigation recommendation and specify the affected_sprint."
    )

    return Task(
        description=prompt_description,
        expected_output=(
            "A structured JSON object with keys: overall_risk, risks, summary. "
            "Each item in 'risks' must contain title, severity, description, affected_sprint, and recommendation."
        ),
        agent=agent,
        output_json=RiskAnalysisResult
    )


def run_risk_analysis(sprint_plan_json: str) -> str:
    """
    Executes the CrewAI Risk Analysis Task and returns the raw agent result string.
    """
    logger.info("Initializing Risk Analysis Agent and Crew execution...")
    agent = create_risk_analysis_agent()
    task = create_risk_analysis_task(agent, sprint_plan_json)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    logger.info("Risk Analysis Agent execution completed.")
    return str(result)
