"""
API Router for Dashboard Analytics and Sprint Statistics.
Provides data aggregation for Recharts widgets (workloads, task splits, and risks).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.api import deps
from app.services.project import project_service
from app.models.task import Task
from app.models.sprint import Sprint
from app.models.team import TeamMember
from app.models.logs import AIRecommendation

router = APIRouter()


@router.get("/projects/{project_id}/dashboard-metrics")
def get_dashboard_metrics(
    project_id: str,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
) -> Dict[str, Any]:
    """
    Aggregate metrics and data series for project analytics charts.
    """
    project = project_service.get_project(db, project_id=project_id, owner_id=current_user.id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or unauthorized access."
        )

    # 1. Base counts
    total_members = db.query(TeamMember).filter(TeamMember.project_id == project_id).count()
    total_tasks = db.query(Task).filter(Task.project_id == project_id).count()
    total_sprints = db.query(Sprint).filter(Sprint.project_id == project_id).count()
    total_risks = db.query(AIRecommendation).filter(AIRecommendation.project_id == project_id).count()

    # 2. Task distribution by category
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    categories_count = {"Backend": 0, "Frontend": 0, "Database": 0, "Testing": 0, "DevOps": 0}
    for t in tasks:
        cat = str(t.category)
        if cat in categories_count:
            categories_count[cat] += 1
        else:
            categories_count[cat] = categories_count.get(cat, 0) + 1

    category_data = [{"name": k, "value": v} for k, v in categories_count.items() if v > 0]

    # 3. Developer Workloads
    members = db.query(TeamMember).filter(TeamMember.project_id == project_id).all()
    workload_data = []
    for m in members:
        total_hours = 0
        assigned_tasks_count = 0
        for assoc in m.task_assignments:
            if assoc.task:
                total_hours += assoc.task.estimated_hours
                assigned_tasks_count += 1
        
        workload_data.append({
            "name": m.name,
            "role": m.role,
            "hours": total_hours,
            "tasks": assigned_tasks_count
        })

    # 4. Sprints statistics
    sprints = db.query(Sprint).filter(Sprint.project_id == project_id).all()
    sprints_data = []
    for s in sprints:
        sprint_hours = sum(rel.task.estimated_hours for rel in s.sprint_tasks if rel.task)
        sprints_data.append({
            "name": s.name,
            "hours": sprint_hours,
            "tasks": len(s.sprint_tasks)  # type: ignore
        })

    # 5. Risks severity counts
    risks = db.query(AIRecommendation).filter(AIRecommendation.project_id == project_id).all()
    risk_severities = {"High": 0, "Medium": 0, "Low": 0}
    for r in risks:
        sev = str(r.severity)
        if sev in risk_severities:
            risk_severities[sev] += 1

    risk_summary = {
        "total": total_risks,
        "high": risk_severities["High"],
        "medium": risk_severities["Medium"],
        "low": risk_severities["Low"],
        "items": [
            {
                "id": r.id,
                "risk_type": r.risk_type,
                "severity": r.severity,
                "description": r.description
            }
            for r in risks
        ]
    }

    return {
        "summary": {
            "total_team_members": total_members,
            "total_tasks": total_tasks,
            "total_sprints": total_sprints,
            "total_risks": total_risks
        },
        "tasks_by_category": category_data,
        "developer_workloads": workload_data,
        "sprint_statistics": sprints_data,
        "risks": risk_summary
    }
