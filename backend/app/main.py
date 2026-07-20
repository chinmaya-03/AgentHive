"""
Main FastAPI application entry point.
Initializes database tables, configures CORS, and registers API routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.database import engine
from app.models import Base
from app.api.routes import api_router
from app.core.logging import setup_logging

# Setup application logging formatters
setup_logging()

# Create database tables automatically if they do not exist
# This ensures a smooth out-of-the-box local developer experience
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AgentHive - Multi-Agent AI Sprint Planning Assistant API"
)

# CORS Configuration
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

from app.database.session import SessionLocal
from app.services.team import team_service

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        team_service.prepopulate_default_skills(db)
    finally:
        db.close()


@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "api_prefix": settings.API_V1_STR
    }
