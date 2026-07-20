"""
Service layer for managing Sprint boundaries, plans aggregation, and validation checks.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories.project import project_repo
from app.repositories.sprint import sprint_repo
from app.repositories.task import task_repo
from app.models.logs import AIRecommendation


class SprintService:
    def get_sprint_plan_data(self, db: Session, project_id: str, owner_id: str) -> Optional[Dict[str, Any]]:
        """
        Aggregates sprints, tasks, and recommendations for a project.
        Returns a structured plan payload or None if project is not found/unauthorized.
        """
        # Validate project ownership
        project = project_repo.get(db, id=project_id)
        if not project or project.owner_id != owner_id:
            return None

        # Fetch entities using repositories
        sprints = sprint_repo.get_by_project(db, project_id=project_id)
        tasks = task_repo.get_by_project(db, project_id=project_id)
        risks = db.query(AIRecommendation).filter(AIRecommendation.project_id == project_id).all()

        # Format output structures
        sprint_details = []
        for s in sprints:
            sprint_tasks_relations = s.sprint_tasks
            s_tasks = []
            total_hours = 0
            for rel in sprint_tasks_relations:
                t = rel.task
                if t:
                    assigned_to = None
                    assignment_reasoning = None
                    if t.assignments:
                        assigned_to = {
                            "id": t.assignments[0].team_member.id if t.assignments[0].team_member else "",
                            "name": t.assignments[0].team_member.name if t.assignments[0].team_member else "",
                            "role": t.assignments[0].team_member.role if t.assignments[0].team_member else ""
                        }
                        assignment_reasoning = t.assignments[0].reasoning

                    s_tasks.append({
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "category": t.category,
                        "estimated_hours": t.estimated_hours,
                        "difficulty": t.difficulty,
                        "status": t.status,
                        "assigned_to": assigned_to,
                        "reasoning": assignment_reasoning
                    })
                    total_hours += t.estimated_hours

            sprint_details.append({
                "id": s.id,
                "name": s.name,
                "goal": s.goal,
                "total_hours": total_hours,
                "tasks": s_tasks
            })

        unassigned_tasks = []
        for t in tasks:
            is_mapped = False
            for s in sprints:
                if any(rel.task_id == t.id for rel in s.sprint_tasks):
                    is_mapped = True
                    break
            
            if not is_mapped:
                assigned_to = None
                if t.assignments:
                    assigned_to = {
                        "id": t.assignments[0].team_member.id if t.assignments[0].team_member else "",
                        "name": t.assignments[0].team_member.name if t.assignments[0].team_member else ""
                    }
                unassigned_tasks.append({
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "category": t.category,
                    "estimated_hours": t.estimated_hours,
                    "difficulty": t.difficulty,
                    "assigned_to": assigned_to
                })

        return {
            "sprints": sprint_details,
            "unassigned_tasks": unassigned_tasks,
            "risks": [
                {
                    "id": r.id,
                    "risk_type": r.risk_type,
                    "description": r.description,
                    "severity": r.severity,
                    "recommendation": r.recommendation
                }
                for r in risks
            ]
        }


sprint_service = SprintService()
