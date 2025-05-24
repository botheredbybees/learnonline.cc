"""
Auth Router - Manages user authentication and authorization.

This module provides endpoints for:
- User registration
- User login and token generation
- Password reset and recovery
- Token validation and refresh
- Managing authentication sessions

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import Dict, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uuid
from uuid import UUID
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os

from models.tables import User, Role
from models.schemas import UserRegisterSchema, UserLoginSchema, PasswordResetRequestSchema, PasswordResetSchema
from db.database import get_db
from auth.auth_handler import sign_jwt, decode_jwt

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_password_hash(password: str) -> str:
    """Generate password hash from plain text password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Convert SQLAlchemy Column to regular string value
    password_hash_str = str(user.password_hash)
    
    if not verify_password(password, password_hash_str):
        return None
        
    return user


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def register_user(
    user_data: UserRegisterSchema,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Parameters:
    - **user_data**: User data including email, password, first_name, last_name
    
    Returns:
    - New user object with token
    
    Raises:
    - 400: Validation error
    - 409: User with this email already exists
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Get default role (usually 'student' or similar)
    default_role = db.query(Role).filter(Role.name == "student").first()
    if not default_role:
        # Create basic role if none exists
        default_role = Role(name="student", description="Basic user role")
        db.add(default_role)
        db.commit()
        db.refresh(default_role)
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    new_user = User(
        id=uuid.uuid4(),
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name or "",
        last_name=user_data.last_name or "",
        role_id=default_role.id,
        is_active=True,
        last_login=datetime.now()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create JWT token
    token = sign_jwt(str(new_user.id))
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "token": token
    }


@router.post("/login", response_model=Dict[str, Any])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return a JWT token.
    
    Parameters:
    - **username**: Email of the user (sent as 'username' in form)
    - **password**: Password of the user
    
    Returns:
    - User object with access token
    
    Raises:
    - 401: Invalid credentials
    - 403: User account is inactive
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user account is active by converting SQLAlchemy Column to bool
    is_active_value = bool(getattr(user, "is_active"))
    if not is_active_value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login timestamp
    setattr(user, "last_login", datetime.now())
    db.commit()
    
    # Generate token
    token = sign_jwt(str(user.id))
    
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "access_token": token["access_token"],
        "token_type": token["token_type"]
    }


@router.post("/reset-password-request")
async def request_password_reset(
    reset_data: PasswordResetRequestSchema,
    db: Session = Depends(get_db)
):
    """
    Request a password reset for a user account.
    
    Parameters:
    - **email**: Email address of the user
    
    Returns:
    - Success message (to prevent email enumeration attacks)
    """
    # Always return a success message even if user not found
    # This prevents email enumeration attacks
    
    user = get_user_by_email(db, reset_data.email)
    if user:
        # In a real implementation, generate a token and send an email
        # For now, we just return a success message
        pass
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetSchema,
    db: Session = Depends(get_db)
):
    """
    Reset a user's password with a valid reset token.
    
    Parameters:
    - **token**: Reset token received by email
    - **new_password**: New password to set
    
    Returns:
    - Success message
    
    Raises:
    - 400: Invalid or expired token
    """
    # Decode the token
    # This is a simplified example. In production, use a separate token system for password resets
    payload = decode_jwt(reset_data.token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Update password
    setattr(user, "password_hash", get_password_hash(reset_data.new_password))
    db.commit()
    
    return {"message": "Password has been reset successfully"}


@router.post("/verify-token")
async def verify_token(
    token: str = Body(..., embed=True)
):
    """
    Verify the validity of a JWT token.
    
    Parameters:
    - **token**: JWT token to verify
    
    Returns:
    - Decoded token payload if valid
    
    Raises:
    - 401: Invalid or expired token
    """
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return payload
