"""
Authentication Service managing user credential verification.
"""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user import user_repo
from app.core.security import verify_password


class AuthService:
    @staticmethod
    def authenticate(
        db: Session, *, email: str, password: str
    ) -> Optional[User]:
        """
        Verify credentials of a user logging in.
        Returns the User object if successful, None otherwise.
        """
        user = user_repo.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, str(user.hashed_password)):
            return None
        return user


auth_service = AuthService()
