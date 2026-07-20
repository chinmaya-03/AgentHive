"""
API Integration tests using FastAPI TestClient and Pytest.
Covers authentication and project management lifecycle.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.models import Base

# Setup file-based SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module", autouse=True)
def init_test_db():
    """Initializes database tables for the test module."""
    # Ensure a fresh db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    import os
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except Exception:
            pass


def override_get_db():
    """DB dependency override pointing to test session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Bind the dependency override
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_auth_register_and_login():
    # 1. Register a new user
    register_payload = {
        "email": "test_pm@company.com",
        "name": "Alex ProjectManager",
        "password": "securepassword123",
        "role": "pm"
    }
    response = client.post("/api/v1/auth/register", json=register_payload)
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test_pm@company.com"
    assert "id" in user_data

    # 2. Login with correct credentials
    login_payload = {
        "email": "test_pm@company.com",
        "password": "securepassword123"
    }
    login_response = client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # 3. Retrieve user profile using JWT token
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["name"] == "Alex ProjectManager"


def test_project_lifecycle():
    # 1. Register user and login to get auth token
    register_payload = {
        "email": "lifecycle_pm@company.com",
        "name": "Lifecycle PM",
        "password": "password123",
        "role": "pm"
    }
    client.post("/api/v1/auth/register", json=register_payload)
    
    login_response = client.post("/api/v1/auth/login", json={
        "email": "lifecycle_pm@company.com",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Project
    project_payload = {
        "name": "Test Application Development",
        "description": "Building a custom mobile app for clients.",
        "status": "active"
    }
    create_res = client.post("/api/v1/projects/", json=project_payload, headers=headers)
    assert create_res.status_code == 201
    project_data = create_res.json()
    assert project_data["name"] == "Test Application Development"
    project_id = project_data["id"]

    # 3. Fetch Projects list
    list_res = client.get("/api/v1/projects/", headers=headers)
    assert list_res.status_code == 200
    projects_list = list_res.json()
    assert len(projects_list) >= 1
    assert any(p["id"] == project_id for p in projects_list)

    # 4. Fetch specific Project details
    details_res = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert details_res.status_code == 200
    assert details_res.json()["name"] == "Test Application Development"

    # 5. Update Project
    update_payload = {"name": "Test Application v2", "status": "completed"}
    update_res = client.put(f"/api/v1/projects/{project_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Test Application v2"
    assert update_res.json()["status"] == "completed"

    # 6. Delete Project
    delete_res = client.delete(f"/api/v1/projects/{project_id}", headers=headers)
    assert delete_res.status_code == 204

    # Verify project is gone
    check_res = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert check_res.status_code == 404
