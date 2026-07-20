"""
API Endpoints for Authentication (registration, login, and profile fetching).
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.repositories.user import user_repo
from app.services.auth import auth_service

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate
) -> UserResponse:
    """
    Register a new project manager/user account.
    """
    user = user_repo.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )
    user = user_repo.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
def login(
    *,
    db: Session = Depends(deps.get_db),
    credentials: UserLogin
) -> Token:
    """
    Login with email and password to receive a JWT access token.
    """
    user = auth_service.authenticate(
        db, email=credentials.email, password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user = Depends(deps.get_current_user)
) -> UserResponse:
    """
    Retrieve the current logged-in user profile.
    """
    return current_user
