"""
Coordinator Agent orchestrating the sequential execution of the 5 specialized AI agents.
Performs data passing, logging, and database committing.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from crewai import Crew

from app.core.config import settings
from app.core.logging import ai_logger
from app.agents.requirement_agent import create_requirement_agent, create_requirement_task
from app.agents.task_agent import create_task_breakdown_agent, create_task_breakdown_task
from app.agents.skill_agent import create_skill_matching_agent, create_skill_matching_task
from app.agents.sprint_agent import create_sprint_planning_agent, create_sprint_planning_task
from app.agents.risk_agent import create_risk_analysis_agent, create_risk_analysis_task

from app.models.logs import AgentExecutionLog, AIRecommendation
from app.models.task import Task as DBTask, TaskAssignment, SprintTask
from app.models.sprint import Sprint as DBSprint

from app.services.ai_service import get_llm

logger = logging.getLogger("agenthive.agents")

MAX_RETRIES = 4
BASE_BACKOFF = 15  # seconds



class CoordinatorAgent:
    def __init__(self, db: Session, project_id: str, srs_text: str, team_members_data: List[Dict[str, Any]]):
        self.db = db
        self.project_id = project_id
        self.srs_text = srs_text
        self.team_members_data = team_members_data
        
        # Initialize LLM
        self.llm = get_llm()

    def _log_agent_step(
        self, agent_name: str, status: str, input_data: Any, output_data: Any, execution_time: float, logs: str
    ) -> AgentExecutionLog:
        """Helper to create and commit an execution log for an agent."""
        input_str = json.dumps(input_data, indent=2) if isinstance(input_data, (dict, list)) else str(input_data)
        output_str = json.dumps(output_data, indent=2) if isinstance(output_data, (dict, list)) else str(output_data)
        
        existing_log = (
            self.db.query(AgentExecutionLog)
            .filter(
                AgentExecutionLog.project_id == self.project_id,
                AgentExecutionLog.agent_name == agent_name
            )
            .first()
        )
        
        if existing_log:
            existing_log.status = status
            existing_log.input_data = input_str
            existing_log.output_data = output_str
            existing_log.execution_time = execution_time
            existing_log.logs = logs
            db_log = existing_log
        else:
            db_log = AgentExecutionLog(
                project_id=self.project_id,
                agent_name=agent_name,
                status=status,
                input_data=input_str,
                output_data=output_str,
                execution_time=execution_time,
                logs=logs
            )
            self.db.add(db_log)
            
        self.db.commit()
        self.db.refresh(db_log)
        return db_log

    def _run_crew_with_retry(self, crew: "Crew") -> Any:
        """
        Runs a CrewAI crew with exponential backoff retry on RateLimitError.
        Waits up to BASE_BACKOFF * 2^attempt seconds between retries.
        """
        import litellm
        last_exc = None
        for attempt in range(MAX_RETRIES):
            try:
                return crew.kickoff()
            except litellm.exceptions.RateLimitError as e:
                last_exc = e
                wait = BASE_BACKOFF * (2 ** attempt)  # 15s, 30s, 60s, 120s
                logger.warning(
                    f"RateLimitError on attempt {attempt + 1}/{MAX_RETRIES}. "
                    f"Waiting {wait}s before retry... ({str(e)[:120]})"
                )
                time.sleep(wait)
            except Exception as e:
                raise e
        raise last_exc

    def execute_pipeline(self) -> Dict[str, Any]:
        """
        Runs the 5-agent CrewAI pipeline sequentially.
        """
        ai_logger.info(f"CoordinatorAgent starting planning pipeline for project {self.project_id}")
        
        # Format team members for LLM context
        team_members_formatted = [
            {
                "id": m["id"],
                "name": m["name"],
                "role": m["role"],
                "skills": [
                    {"name": s["name"], "proficiency_level": s["proficiency_level"]}
                    for s in m.get("skills", [])
                ]
            }
            for m in self.team_members_data
        ]
        team_members_json_str = json.dumps(team_members_formatted, indent=2)

        # ----------------------------------------------------
        # AGENT 1: Requirement Analysis
        # ----------------------------------------------------
        agent_name_1 = "Requirement Analysis Agent"
        self._log_agent_step(agent_name_1, "Running", self.srs_text, None, 0.0, "Requirement Analysis Agent deconstructing spec...")
        
        start_time = time.time()
        try:
            agent = create_requirement_agent(self.llm)
            task = create_requirement_task(agent, self.srs_text)
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            
            crew_output = self._run_crew_with_retry(crew)
            elapsed = time.time() - start_time
            
            output_data = self._parse_json_result(crew_output)
            self._log_agent_step(agent_name_1, "Completed", self.srs_text, output_data, elapsed, "SRS text analyzed successfully.")
        except Exception as e:
            elapsed = time.time() - start_time
            self._log_agent_step(agent_name_1, "Failed", self.srs_text, None, elapsed, f"Error: {str(e)}")
            raise e

        # ----------------------------------------------------
        # AGENT 2: Task Breakdown
        # ----------------------------------------------------
        agent_name_2 = "Task Breakdown Agent"
        self._log_agent_step(agent_name_2, "Running", output_data, None, 0.0, "Task Breakdown Agent decomposing requirements...")
        
        start_time = time.time()
        try:
            agent = create_task_breakdown_agent(self.llm)
            task = create_task_breakdown_task(agent, json.dumps(output_data, indent=2))
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            
            crew_output = self._run_crew_with_retry(crew)
            elapsed = time.time() - start_time
            
            output_data_2 = self._parse_json_result(crew_output)
            self._log_agent_step(agent_name_2, "Completed", output_data, output_data_2, elapsed, "Engineering tasks generated successfully.")
        except Exception as e:
            elapsed = time.time() - start_time
            self._log_agent_step(agent_name_2, "Failed", output_data, None, elapsed, f"Error: {str(e)}")
            raise e

        # ----------------------------------------------------
        # AGENT 3: Skill Matching
        # ----------------------------------------------------
        agent_name_3 = "Skill Matching Agent"
        skill_matching_input = {
            "tasks": output_data_2.get("tasks", []),
            "team_members": team_members_formatted
        }
        self._log_agent_step(agent_name_3, "Running", skill_matching_input, None, 0.0, "Skill Matching Agent mapping developers...")
        
        start_time = time.time()
        try:
            agent = create_skill_matching_agent(self.llm)
            task = create_skill_matching_task(agent, json.dumps(output_data_2, indent=2), team_members_json_str)
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            
            crew_output = self._run_crew_with_retry(crew)
            elapsed = time.time() - start_time
            
            output_data_3 = self._parse_json_result(crew_output)
            self._log_agent_step(agent_name_3, "Completed", skill_matching_input, output_data_3, elapsed, "Developer assignments completed.")
        except Exception as e:
            elapsed = time.time() - start_time
            self._log_agent_step(agent_name_3, "Failed", skill_matching_input, None, elapsed, f"Error: {str(e)}")
            raise e

        # ----------------------------------------------------
        # AGENT 4: Sprint Planning
        # ----------------------------------------------------
        agent_name_4 = "Sprint Planning Agent"
        sprint_plan_input = {
            "tasks": output_data_2.get("tasks", []),
            "assignments": output_data_3.get("assignments", [])
        }
        self._log_agent_step(agent_name_4, "Running", sprint_plan_input, None, 0.0, "Sprint Planning Agent organizing roadmap...")
        
        start_time = time.time()
        try:
            assigned_tasks = self._combine_tasks_and_assignments(
                output_data_2.get("tasks", []),
                output_data_3.get("assignments", [])
            )
            
            agent = create_sprint_planning_agent(self.llm)
            task = create_sprint_planning_task(agent, json.dumps(assigned_tasks, indent=2))
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            
            crew_output = self._run_crew_with_retry(crew)
            elapsed = time.time() - start_time
            
            output_data_4 = self._parse_json_result(crew_output)
            self._log_agent_step(agent_name_4, "Completed", sprint_plan_input, output_data_4, elapsed, "Sprints grouped and balanced.")
        except Exception as e:
            elapsed = time.time() - start_time
            self._log_agent_step(agent_name_4, "Failed", sprint_plan_input, None, elapsed, f"Error: {str(e)}")
            raise e

        # ----------------------------------------------------
        # AGENT 5: Risk Analysis
        # ----------------------------------------------------
        agent_name_5 = "Risk Analysis Agent"
        self._log_agent_step(agent_name_5, "Running", output_data_4, None, 0.0, "Risk Analysis Agent auditing schedule...")
        
        start_time = time.time()
        try:
            agent = create_risk_analysis_agent(self.llm)
            task = create_risk_analysis_task(agent, json.dumps(output_data_4, indent=2))
            crew = Crew(agents=[agent], tasks=[task], verbose=True)
            
            crew_output = self._run_crew_with_retry(crew)
            elapsed = time.time() - start_time
            
            output_data_5 = self._parse_json_result(crew_output)
            self._log_agent_step(agent_name_5, "Completed", output_data_4, output_data_5, elapsed, "Sprints risk audit finished.")
        except Exception as e:
            elapsed = time.time() - start_time
            self._log_agent_step(agent_name_5, "Failed", output_data_4, None, elapsed, f"Error: {str(e)}")
            raise e

        # ----------------------------------------------------
        # PERSIST FINAL OUTPUTS TO DATABASE
        # ----------------------------------------------------
        self._save_to_database(
            tasks_list=output_data_2.get("tasks", []),
            assignments_list=output_data_3.get("assignments", []),
            sprints_list=output_data_4.get("sprints", []),
            risks_list=output_data_5.get("risks", [])
        )
        
        ai_logger.info(f"CoordinatorAgent successfully finished planning project {self.project_id}")
        return {
            "requirement_analysis": output_data,
            "tasks": output_data_2,
            "assignments": output_data_3,
            "sprints": output_data_4,
            "risks": output_data_5
        }

    def _parse_json_result(self, crew_output: Any) -> Dict[str, Any]:
        """Ensures the string output from CrewAI is formatted into dictionary."""
        output_str = str(crew_output).strip()
        
        # Clean markdown code blocks
        if output_str.startswith("```json"):
            output_str = output_str[7:]
        elif output_str.startswith("```"):
            output_str = output_str[3:]
        if output_str.endswith("```"):
            output_str = output_str[:-3]
        output_str = output_str.strip()
        
        try:
            return json.loads(output_str)
        except Exception as e:
            # Fallback to python ast literal evaluation if the LLM output single quotes (Python representation)
            try:
                import ast
                val = ast.literal_eval(output_str)
                if isinstance(val, dict):
                    return val
            except Exception:
                pass
            
            # Additional fallback: replace single quotes with double quotes (basic JSON format fix)
            try:
                cleaned_str = output_str.replace("'", '"')
                return json.loads(cleaned_str)
            except Exception:
                pass
                
            logger.error(f"Failed parsing structured LLM output: {str(e)}")
            return {"raw_output": output_str}

    def _combine_tasks_and_assignments(self, tasks: List[Dict[str, Any]], assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine task metadata with assigned team member IDs."""
        assignments_map = {a["task_title"]: a for a in assignments}
        combined = []
        for t in tasks:
            task_title = t.get("title")
            assign_info = assignments_map.get(task_title, {})
            t_copy = dict(t)
            t_copy["assigned_member_id"] = assign_info.get("assigned_member_id")
            t_copy["assigned_member_name"] = assign_info.get("assigned_member_name")
            t_copy["assignment_reasoning"] = assign_info.get("reasoning")
            combined.append(t_copy)
        return combined

    def _save_to_database(
        self, tasks_list: List[Dict[str, Any]], assignments_list: List[Dict[str, Any]],
        sprints_list: List[Dict[str, Any]], risks_list: List[Dict[str, Any]]
    ):
        """Clears previous iterations and saves the new plan configurations."""
        self.db.query(DBSprint).filter(DBSprint.project_id == self.project_id).delete()
        self.db.query(DBTask).filter(DBTask.project_id == self.project_id).delete()
        self.db.query(AIRecommendation).filter(AIRecommendation.project_id == self.project_id).delete()
        self.db.flush()

        sprint_id_map: Dict[str, str] = {}
        for s in sprints_list:
            db_sprint = DBSprint(
                project_id=self.project_id,
                name=s.get("sprint_name"),
                goal=s.get("goal"),
                status="Planned"
            )
            self.db.add(db_sprint)
            self.db.flush()
            sprint_id_map[str(db_sprint.name)] = str(db_sprint.id)

        task_title_map: Dict[str, str] = {}
        task_title_map_normalized: Dict[str, str] = {}
        for t in tasks_list:
            db_task = DBTask(
                project_id=self.project_id,
                title=t.get("title"),
                description=t.get("description"),
                category=t.get("category", "Backend"),
                estimated_hours=t.get("estimated_hours", 4),
                difficulty=t.get("difficulty", "Medium"),
                status="Todo"
            )
            self.db.add(db_task)
            self.db.flush()
            title_str = str(db_task.title)
            task_title_map[title_str] = str(db_task.id)
            task_title_map_normalized[title_str.strip().lower()] = str(db_task.id)

        for assoc in assignments_list:
            task_title = assoc.get("task_title")
            if isinstance(task_title, str):
                task_id = task_title_map.get(task_title) or task_title_map_normalized.get(task_title.strip().lower())
                member_id = assoc.get("assigned_member_id") or assoc.get("team_member_id")
                
                # Ensure member_id is a valid UUID/ID from the project's team members
                valid_member_ids = {tm.get("id") for tm in self.team_members_data}
                if member_id not in valid_member_ids:
                    member_id = None

                if not member_id and assoc.get("assigned_member_name"):
                    member_name = str(assoc.get("assigned_member_name")).strip().lower()
                    for tm in self.team_members_data:
                        if str(tm.get("name", "")).strip().lower() == member_name:
                            member_id = tm.get("id")
                            break
                if not member_id and self.team_members_data:
                    member_id = self.team_members_data[0].get("id")

                if task_id and member_id:
                    db_assignment = TaskAssignment(
                        task_id=task_id,
                        team_member_id=member_id,
                        reasoning=assoc.get("reasoning")
                    )
                    self.db.add(db_assignment)

        for s in sprints_list:
            sprint_name = s.get("sprint_name") or s.get("name")
            if isinstance(sprint_name, str):
                sprint_id = sprint_id_map.get(sprint_name)
                if sprint_id:
                    raw_tasks = s.get("tasks", []) or s.get("task_titles", [])
                    for item in raw_tasks:
                        task_title = None
                        if isinstance(item, str):
                            task_title = item
                        elif isinstance(item, dict):
                            task_title = item.get("task_title") or item.get("title")

                        if isinstance(task_title, str):
                            task_id = task_title_map.get(task_title) or task_title_map_normalized.get(task_title.strip().lower())
                            if task_id:
                                db_sprint_task = SprintTask(
                                    sprint_id=sprint_id,
                                    task_id=task_id
                                )
                                self.db.add(db_sprint_task)

        for r in risks_list:
            db_rec = AIRecommendation(
                project_id=self.project_id,
                risk_type=r.get("risk_type") or r.get("title") or r.get("risk_title") or r.get("type") or "General Risk",
                description=r.get("description") or r.get("details") or "No description provided.",
                severity=r.get("severity", "Medium"),
                recommendation=r.get("recommendation") or r.get("mitigation") or "No mitigation suggested."
            )
            self.db.add(db_rec)

        self.db.commit()
