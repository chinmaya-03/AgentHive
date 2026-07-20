"""
Service layer orchestrating the Sprint Planning Agent execution.
Consumes TaskBreakdownResult and SkillMatchingResult, invokes Sprint Planning Agent, validates output schema.
"""

import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.repositories.requirement import requirement_repo
from app.repositories.project import project_repo
from app.services.task_breakdown_service import task_breakdown_service
from app.services.skill_matching_service import skill_matching_service
from app.agents.sprint_planning_agent import run_sprint_planning
from app.schemas.ai import TaskBreakdownResult, SkillMatchingResult, SprintPlanResult
from app.utils.helpers import extract_json_from_llm_output
from app.core.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class SprintPlanningService:
    @staticmethod
    def plan_sprints(
        db: Session, *, requirement_id: str, owner_id: str
    ) -> SprintPlanResult:
        """
        Executes Sprint Planning pipeline for a requirement document ID.
        
        Pipeline:
        Requirement -> Requirement Analysis -> Task Breakdown -> Skill Matching -> Sprint Planning
        """
        # Step 1: Verify document & project ownership
        doc = requirement_repo.get(db, id=requirement_id)
        if not doc:
            raise ValueError(f"Requirement document with ID '{requirement_id}' not found.")

        project = project_repo.get(db, id=doc.project_id)
        if not project or project.owner_id != owner_id:
            raise ValueError("Unauthorized access to requirement document.")

        # Step 2: Execute Task Breakdown (Phase 4)
        logger.info(f"Obtaining Task Breakdown for Document ID={requirement_id}...")
        task_breakdown_result = task_breakdown_service.breakdown_requirement_tasks(
            db, requirement_id=requirement_id, owner_id=owner_id
        )

        if not task_breakdown_result.technical_tasks:
            raise ValueError("Task breakdown produced no technical tasks for sprint planning.")

        # Step 3: Execute Skill Matching (Phase 5)
        logger.info(f"Obtaining Skill Matching for Document ID={requirement_id}...")
        skill_matching_result = skill_matching_service.match_requirement_skills(
            db, requirement_id=requirement_id, owner_id=owner_id
        )

        if not skill_matching_result.assignments:
            raise ValueError("Skill matching produced no role assignments for sprint planning.")

        # Combine TaskBreakdownResult & SkillMatchingResult for LLM input
        assignments_by_title = {a.task_title: a for a in skill_matching_result.assignments}
        combined_tasks: List[Dict[str, Any]] = []

        total_story_points = 0
        for task in task_breakdown_result.technical_tasks:
            assignment = assignments_by_title.get(task.title)
            total_story_points += task.story_points
            combined_tasks.append({
                "task_title": task.title,
                "description": task.description,
                "story_points": task.story_points,
                "priority": task.priority,
                "dependencies": task.dependencies,
                "assigned_role": assignment.developer_role if assignment else "Software Engineer",
                "required_skills": assignment.skills if assignment else [],
                "experience_level": assignment.experience_level if assignment else "Mid"
            })

        assigned_tasks_json = json.dumps(combined_tasks, indent=2)
        task_count = len(combined_tasks)

        # Structured Log: Sprint planning started
        logger.info(
            f"Sprint Planning Started: Document ID={requirement_id} | "
            f"Number of Tasks={task_count} | Total Story Points={total_story_points}"
        )

        # Step 4: Run Sprint Planning Agent via CrewAI
        try:
            raw_response = run_sprint_planning(assigned_tasks_json)
        except Exception as e:
            logger.error(f"Sprint Planning AI failure during agent execution: {str(e)}")
            raise AgentExecutionError(
                agent_name="Sprint Planning Agent",
                reason=f"LLM sprint planning execution failed: {str(e)}"
            )

        # Step 5: Extract and parse JSON response
        try:
            json_dict = extract_json_from_llm_output(raw_response)
        except ValueError as ve:
            logger.error(f"Sprint Planning AI failure during JSON parsing: {str(ve)}")
            raise AgentExecutionError(
                agent_name="Sprint Planning Agent",
                reason=f"Failed to parse valid JSON from Sprint Planning Agent response: {str(ve)}"
            )

        # Step 6: Validate output schema using Pydantic
        try:
            validated_output = SprintPlanResult(**json_dict)

            # Structured Log: Sprint metrics
            sprint_count = len(validated_output.sprints)
            sprint_goals = [sprint.goal for sprint in validated_output.sprints]

            logger.info(
                f"Sprint Planning Completed: Document ID={requirement_id} | "
                f"Number of Tasks={task_count} | Total Story Points={total_story_points} | "
                f"Number of Sprints={sprint_count} | Sprint Goals={sprint_goals}"
            )
            return validated_output

        except Exception as schema_err:
            logger.error(f"Sprint Planning AI failure during schema validation: {str(schema_err)}")
            raise AgentExecutionError(
                agent_name="Sprint Planning Agent",
                reason=f"Sprint Planning AI output failed schema validation: {str(schema_err)}"
            )


sprint_planning_service = SprintPlanningService()
