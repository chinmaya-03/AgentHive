"""
Aggregates and mounts all modular sub-routers for the AgentHive API.
"""

from fastapi import APIRouter
from app.api.routes import auth, projects, team, requirements, skills, ai, analytics

api_router = APIRouter()

# Include all route blueprints
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(requirements.router, tags=["Requirements"])  # Has internal prefix "/projects"
api_router.include_router(team.router, prefix="/team", tags=["Team Members"])
api_router.include_router(skills.router, prefix="/skills", tags=["Skills"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Sprint Planner"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
