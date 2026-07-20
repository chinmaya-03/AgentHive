"""
Service layer for AI Generation logic, Crew background scheduling, and execution telemetry.
"""

from typing import List, Dict, Any, Optional
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.repositories.project import project_repo
from app.repositories.team import team_repo
from app.models.requirement import RequirementDocument
from app.models.logs import AgentExecutionLog
from app.agents.coordinator import CoordinatorAgent


class AIService:
    def trigger_sprint_plan_generation(
        self, db: Session, project_id: str, owner_id: str, background_tasks: BackgroundTasks, requirement_id: Optional[str] = None
    ) -> Optional[Dict[str, str]]:
        """
        Retrieves project contexts, writes placeholder pending steps,
        and launches the CrewAI pipeline as a background task.
        """
        # Validate project ownership
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            return None

        # Fetch processed SRS requirements document
        if requirement_id:
            req_doc = (
                db.query(RequirementDocument)
                .filter(
                    RequirementDocument.id == requirement_id,
                    RequirementDocument.project_id == project_id,
                    RequirementDocument.processing_status == "Processed"
                )
                .first()
            )
            if not req_doc:
                raise ValueError("Selected Requirement Document not found or not processed.")
        else:
            req_doc = (
                db.query(RequirementDocument)
                .filter(
                    RequirementDocument.project_id == project_id,
                    RequirementDocument.processing_status == "Processed"
                )
                .order_by(RequirementDocument.upload_timestamp.desc())
                .first()
            )
        if not req_doc or not req_doc.extracted_text:
            raise ValueError("No processed Requirement Document (SRS) found. Please upload one first.")

        # Fetch team members
        team_members = team_repo.get_by_project(db, project_id=project_id)
        if not team_members:
            raise ValueError("No team members found for this project. Please add team members first.")

        # Serialize members + skills
        team_members_data = []
        for member in team_members:
            member_data = {
                "id": member.id,
                "name": member.name,
                "role": member.role,
                "skills": [
                    {
                        "name": assoc.skill.name if assoc.skill else "",
                        "proficiency_level": assoc.proficiency_level
                    }
                    for assoc in member.skills_associations
                ]
            }
            team_members_data.append(member_data)

        # Write/update placeholder execution logs
        agents = [
            "Requirement Analysis Agent",
            "Task Breakdown Agent",
            "Skill Matching Agent",
            "Sprint Planning Agent",
            "Risk Analysis Agent"
        ]
        for agent_name in agents:
            existing = (
                db.query(AgentExecutionLog)
                .filter(
                    AgentExecutionLog.project_id == project_id,
                    AgentExecutionLog.agent_name == agent_name
                )
                .first()
            )
            if existing:
                existing.status = "Pending"
                existing.input_data = None
                existing.output_data = None
                existing.execution_time = 0.0
                existing.logs = "Waiting to start..."
            else:
                new_log = AgentExecutionLog(
                    project_id=project_id,
                    agent_name=agent_name,
                    status="Pending",
                    logs="Waiting to start..."
                )
                db.add(new_log)
        db.commit()

        # Add runner as background task
        background_tasks.add_task(
            self._run_sprint_planner_background,
            project_id=project_id,
            srs_text=req_doc.extracted_text,
            team_members_data=team_members_data
        )

        return {"message": "Sprint plan generation started in the background."}

    def get_generation_logs(self, db: Session, project_id: str, owner_id: str) -> Optional[List[AgentExecutionLog]]:
        """Fetch all execution logs for the project."""
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            return None

        return (
            db.query(AgentExecutionLog)
            .filter(AgentExecutionLog.project_id == project_id)
            .all()
        )

    def _run_sprint_planner_background(
        self, project_id: str, srs_text: str, team_members_data: List[Dict[str, Any]]
    ) -> None:
        """Isolated session execution wrapper for CrewAI thread."""
        from app.database.session import SessionLocal
        db = SessionLocal()
        try:
            coordinator = CoordinatorAgent(
                db=db,
                project_id=project_id,
                srs_text=srs_text,
                team_members_data=team_members_data
            )
            coordinator.execute_pipeline()
        except Exception as e:
            import traceback
            print(f"Background sprint planning failed for project {project_id}: {str(e)}")
            traceback.print_exc()
        finally:
            db.close()


ai_service = AIService()
