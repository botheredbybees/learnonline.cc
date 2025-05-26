"""
Auth Router - Manages user authentication and authorization.

This module provides endpoints for:
- User registration with email verification
- User login and token generation
- Password reset and recovery
- Token validation and refresh
- Managing authentication sessions
- Role-based access control

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import Dict, Optional, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uuid
from uuid import UUID
from datetime import datetime, timedelta
import os
import secrets

# Optional email imports for development/testing environments
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    print("Email functionality not available - running in test mode")

from models.tables import User, Role, UserProfile
from models.schemas import (
    UserRegisterSchema, UserLoginSchema, PasswordResetRequestSchema, 
    PasswordResetSchema, UserSchema, UserProfileSchema
)
from db.database import get_db
from auth.auth_handler import (
    sign_jwt, decode_jwt, get_password_hash, verify_password, 
    refresh_access_token, get_user_permissions,
    get_user_role_by_experience, get_user_with_role
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@learnonline.cc")

# Store password reset tokens (in production, use Redis or database)
password_reset_tokens = {}

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
        
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Get the current user from the JWT token with role and permission validation
    """
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database with role information
    user = get_user_with_role(db, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

def send_email(to_email: str, subject: str, body: str):
    """Send email (simplified implementation)"""
    try:
        if not EMAIL_AVAILABLE or not SMTP_USERNAME:  # Skip email sending in development/testing
            print(f"Email would be sent to {to_email}: {subject}")
            return True
            
        msg = MimeMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MimeText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(FROM_EMAIL, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def create_user_profile(db: Session, user_id: UUID) -> UserProfile:
    """Create default user profile"""
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=user_id,
        experience_points=0,
        level=1
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_user_role_by_experience(db: Session, user: User):
    """Update user role based on experience points"""
    if user.profile:
        experience_points = user.profile.experience_points
        new_role_name = get_user_role_by_experience(experience_points)
        
        # Get the role from database
        new_role = db.query(Role).filter(Role.name == new_role_name).first()
        if new_role and user.role_id != new_role.id:
            user.role_id = new_role.id
            db.commit()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def register_user(
    user_data: UserRegisterSchema,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Register a new user account with email verification.
    
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
    
    # Get default role (guest for new users)
    default_role = db.query(Role).filter(Role.name == "guest").first()
    if not default_role:
        # Create basic roles if none exist
        roles_to_create = [
            ("admin", "Administrator with full access"),
            ("mentor", "Mentor with content creation and team management"),
            ("player", "Player with content access and assessments"),
            ("guest", "Guest with limited browsing")
        ]
        
        for role_name, role_desc in roles_to_create:
            role = Role(name=role_name, description=role_desc)
            db.add(role)
        
        db.commit()
        default_role = db.query(Role).filter(Role.name == "guest").first()
    
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
    
    # Create user profile
    create_user_profile(db, new_user.id)
    
    # Get user permissions
    permissions = get_user_permissions(db, default_role.name)
    
    # Create JWT token with role and permissions
    token = sign_jwt(str(new_user.id), default_role.name, permissions)
    
    # Send welcome email (background task)
    background_tasks.add_task(
        send_email,
        new_user.email,
        "Welcome to LearnOnline.cc",
        f"<h1>Welcome {new_user.first_name}!</h1><p>Your account has been created successfully.</p>"
    )
    
    return {
        "id": str(new_user.id),
        "email": new_user.email,
        "username": new_user.email,  # Added username field using email
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "role": default_role.name,
        "permissions": permissions,
        "access_token": token["access_token"],
        "refresh_token": token["refresh_token"],
        "token_type": token["token_type"],
        "expires_in": token["expires_in"]
    }


@router.post("/login", response_model=Dict[str, Any])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return JWT tokens.
    
    Parameters:
    - **username**: Email of the user (sent as 'username' in form)
    - **password**: Password of the user
    
    Returns:
    - User object with access and refresh tokens
    
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
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login timestamp
    user.last_login = datetime.now()
    db.commit()
    
    # Update user role based on experience points
    update_user_role_by_experience(db, user)
    
    # Get user role and permissions
    role_name = user.role.name if user.role else "guest"
    permissions = get_user_permissions(db, role_name)
    
    # Generate tokens
    token = sign_jwt(str(user.id), role_name, permissions)
    
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role_name,
        "permissions": permissions,
        "access_token": token["access_token"],
        "refresh_token": token["refresh_token"],
        "token_type": token["token_type"],
        "expires_in": token["expires_in"]
    }


@router.post("/refresh-token", response_model=Dict[str, Any])
async def refresh_token(
    token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Parameters:
    - **token**: Valid refresh token
    
    Returns:
    - New access token
    
    Raises:
    - 401: Invalid or expired refresh token
    """
    token_data = refresh_access_token(token, db)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return token_data


@router.post("/reset-password-request")
async def request_password_reset(
    reset_data: PasswordResetRequestSchema,
    background_tasks: BackgroundTasks,
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
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        password_reset_tokens[reset_token] = {
            "user_id": str(user.id),
            "expires": datetime.now() + timedelta(hours=1)
        }
        
        # Send reset email (background task)
        reset_link = f"https://learnonline.cc/reset-password?token={reset_token}"
        background_tasks.add_task(
            send_email,
            user.email,
            "Password Reset Request",
            f"<h1>Password Reset</h1><p>Click <a href='{reset_link}'>here</a> to reset your password. This link expires in 1 hour.</p>"
        )
    
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
    # Check if token exists and is valid
    token_data = password_reset_tokens.get(reset_data.token)
    if not token_data or token_data["expires"] < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user_id = token_data["user_id"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Update password
    user.password_hash = get_password_hash(reset_data.new_password)
    db.commit()
    
    # Remove used token
    del password_reset_tokens[reset_data.token]
    
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


@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user information.
    
    Returns:
    - Current user data with role and permissions
    
    Raises:
    - 401: Not authenticated
    """
    # Get user role and permissions
    role_name = current_user.role.name if current_user.role else "guest"
    permissions = get_user_permissions(db, role_name)
    
    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": role_name,
        "permissions": permissions,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
        "profile": {
            "experience_points": profile.experience_points if profile else 0,
            "level": profile.level if profile else 1,
            "bio": profile.bio if profile else None,
            "avatar_url": profile.avatar_url if profile else None
        } if profile else None
    }


@router.post("/logout")
async def logout():
    """
    Logout user (client should remove tokens).
    
    Returns:
    - Success message
    """
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    password_data: Dict[str, str] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Parameters:
    - **current_password**: Current password
    - **new_password**: New password
    
    Returns:
    - Success message
    
    Raises:
    - 400: Invalid current password
    - 401: Not authenticated
    """
    current_password = password_data.get("current_password")
    new_password = password_data.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both current_password and new_password are required"
        )
    
    # Verify current password
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
