"""
Team Service managing Project team members, skills assignments, and a global skills registry.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.team import TeamMember, TeamMemberSkill
from app.models.skill import Skill
from app.schemas.team import TeamMemberCreate, TeamMemberUpdate
from app.schemas.skill import SkillCreate
from app.services.project import project_service


class TeamService:
    @staticmethod
    def get_team_members(db: Session, *, project_id: str, owner_id: str) -> List[TeamMember]:
        """Fetch all team members associated with a project, verifying project ownership."""
        project = project_service.get_project(db, project_id=project_id, owner_id=owner_id)
        if not project:
            return []
        return db.query(TeamMember).filter(TeamMember.project_id == project_id).all()

    @staticmethod
    def get_team_member(db: Session, *, member_id: str, project_id: str, owner_id: str) -> Optional[TeamMember]:
        """Fetch a specific team member, verifying project ownership."""
        project = project_service.get_project(db, project_id=project_id, owner_id=owner_id)
        if not project:
            return None
        return (
            db.query(TeamMember)
            .filter(TeamMember.id == member_id, TeamMember.project_id == project_id)
            .first()
        )

    @staticmethod
    def add_team_member(
        db: Session, *, project_id: str, member_in: TeamMemberCreate, owner_id: str
    ) -> Optional[TeamMember]:
        """Add a new team member to a project and link their skills."""
        project = project_service.get_project(db, project_id=project_id, owner_id=owner_id)
        if not project:
            return None

        # Create member
        member = TeamMember(
            project_id=project_id,
            name=member_in.name,
            email=member_in.email,
            role=member_in.role
        )
        db.add(member)
        db.flush()  # Generate member.id for associations

        # Add skills associations
        for skill_assoc in member_in.skills:
            skill = db.query(Skill).filter(Skill.id == skill_assoc.skill_id).first()
            if skill:
                assoc = TeamMemberSkill(
                    team_member_id=member.id,
                    skill_id=skill.id,
                    proficiency_level=skill_assoc.proficiency_level
                )
                db.add(assoc)

        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def update_team_member(
        db: Session, *, project_id: str, member_id: str, member_in: TeamMemberUpdate, owner_id: str
    ) -> Optional[TeamMember]:
        """Update a team member's profile and refresh their skills list."""
        member = TeamService.get_team_member(db, member_id=member_id, project_id=project_id, owner_id=owner_id)
        if not member:
            return None

        # Update core fields
        if member_in.name is not None:
            member.name = member_in.name
        if member_in.email is not None:
            member.email = member_in.email
        if member_in.role is not None:
            member.role = member_in.role

        # Update skills if provided
        if member_in.skills is not None:
            # Delete old skills
            db.query(TeamMemberSkill).filter(TeamMemberSkill.team_member_id == member_id).delete()
            
            # Add new skills
            for skill_assoc in member_in.skills:
                skill = db.query(Skill).filter(Skill.id == skill_assoc.skill_id).first()
                if skill:
                    assoc = TeamMemberSkill(
                        team_member_id=member.id,
                        skill_id=skill.id,
                        proficiency_level=skill_assoc.proficiency_level
                    )
                    db.add(assoc)

        db.commit()
        db.refresh(member)
        return member

    @staticmethod
    def delete_team_member(db: Session, *, project_id: str, member_id: str, owner_id: str) -> bool:
        """Remove a team member from a project. Cascade deletes skills and assignments."""
        member = TeamService.get_team_member(db, member_id=member_id, project_id=project_id, owner_id=owner_id)
        if not member:
            return False
        
        db.delete(member)
        db.commit()
        return True

    # Global Skills Registry Management
    @staticmethod
    def get_skills(db: Session) -> List[Skill]:
        """Get all global skills registered in the platform."""
        return db.query(Skill).order_by(Skill.category, Skill.name).all()

    @staticmethod
    def create_skill(db: Session, *, skill_in: SkillCreate) -> Optional[Skill]:
        """Register a new technology skill in the global registry."""
        existing = db.query(Skill).filter(Skill.name.like(skill_in.name)).first()
        if existing:
            return existing
        db_obj = Skill(name=skill_in.name, category=skill_in.category)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def prepopulate_default_skills(db: Session):
        """Pre-populate a default set of industry skills if the database registry is empty."""
        count = db.query(Skill).count()
        if count > 0:
            return

        default_skills = [
            # Frontend
            ("React", "Frontend"),
            ("TypeScript", "Frontend"),
            ("Vue", "Frontend"),
            ("HTML/CSS", "Frontend"),
            ("Tailwind CSS", "Frontend"),
            ("Next.js", "Frontend"),
            
            # Backend
            ("Python", "Backend"),
            ("FastAPI", "Backend"),
            ("Node.js", "Backend"),
            ("Go", "Backend"),
            ("Java", "Backend"),
            ("Spring Boot", "Backend"),
            
            # Database
            ("PostgreSQL", "Database"),
            ("MySQL", "Database"),
            ("MongoDB", "Database"),
            ("Redis", "Database"),
            
            # DevOps
            ("Docker", "DevOps"),
            ("AWS", "DevOps"),
            ("CI/CD Pipelines", "DevOps"),
            ("Kubernetes", "DevOps"),
            
            # Testing
            ("PyTest", "Testing"),
            ("Jest", "Testing"),
            ("Selenium", "Testing"),
            ("Playwright", "Testing"),
        ]

        for name, category in default_skills:
            skill = Skill(name=name, category=category)
            db.add(skill)
        db.commit()


team_service = TeamService()
