"""
Pydantic schemas for Skills.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class SkillBase(BaseModel):
    name: str
    category: str  # Frontend, Backend, Database, DevOps, Testing, etc.


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
