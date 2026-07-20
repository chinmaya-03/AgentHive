"""
Pydantic schemas for Team Members and their associated Skills.
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class TeamMemberSkillBase(BaseModel):
    skill_id: str
    proficiency_level: str  # Junior, Mid, Senior


class TeamMemberSkillCreate(TeamMemberSkillBase):
    pass


class TeamMemberSkillResponse(TeamMemberSkillBase):
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)


class TeamMemberBase(BaseModel):
    name: str
    email: EmailStr
    role: str  # Frontend, Backend, QA, DevOps, Database, Fullstack, etc.


class TeamMemberCreate(TeamMemberBase):
    skills: List[TeamMemberSkillCreate] = []


class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    skills: Optional[List[TeamMemberSkillCreate]] = None


class TeamMemberResponse(TeamMemberBase):
    id: str
    project_id: str
    skills: List[TeamMemberSkillResponse] = []

    model_config = ConfigDict(from_attributes=True)
