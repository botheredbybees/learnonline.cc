import os
import time
from typing import Dict, Optional, List
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from passlib.context import CryptContext

from db.database import get_db
from models.tables import User, Role, Permission, RolePermission

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # Default 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # Default 7 days

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Role-based permission levels
ROLE_PERMISSIONS = {
    "admin": ["full_access", "user_management", "aqtf_sync", "content_creation", "team_management"],
    "mentor": ["content_creation", "team_management", "content_access", "assessments"],
    "player": ["content_access", "assessments"],
    "guest": ["limited_browsing"]
}

def get_password_hash(password: str) -> str:
    """Generate password hash from plain text password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored hash"""
    return pwd_context.verify(plain_password, hashed_password)

def token_response(access_token: str, refresh_token: str = None):
    """Format token response"""
    response = {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    if refresh_token:
        response["refresh_token"] = refresh_token
    return response

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create a new JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def sign_jwt(user_id: str, role_name: str = None, permissions: List[str] = None) -> Dict[str, str]:
    """
    Create new JWT tokens for a user with role and permissions
    """
    payload = {
        "user_id": user_id,
        "role": role_name,
        "permissions": permissions or []
    }
    
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token({"user_id": user_id})
    
    return token_response(access_token, refresh_token)

def decode_jwt(token: str) -> Optional[Dict]:
    """
    Decode and validate a JWT token
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        if decoded_token["exp"] >= time.time():
            return decoded_token
        
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def refresh_access_token(refresh_token: str, db: Session) -> Optional[Dict[str, str]]:
    """
    Generate new access token from refresh token
    """
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            return None
            
        # Check if token is expired
        if payload["exp"] < time.time():
            return None
            
        user_id = payload.get("user_id")
        if not user_id:
            return None
            
        # Get user and role information
        user = get_user_with_role(db, user_id)
        if not user:
            return None
            
        # Get user permissions
        permissions = get_user_permissions(db, user.role.name if user.role else "guest")
        
        # Create new access token
        new_payload = {
            "user_id": user_id,
            "role": user.role.name if user.role else "guest",
            "permissions": permissions
        }
        
        access_token = create_access_token(new_payload)
        return token_response(access_token)
        
    except jwt.InvalidTokenError:
        return None

def get_user_with_role(db: Session, user_id: str) -> Optional[User]:
    """Get user with role information"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_permissions(db: Session, role_name: str) -> List[str]:
    """Get permissions for a role"""
    # First check predefined role permissions
    if role_name in ROLE_PERMISSIONS:
        return ROLE_PERMISSIONS[role_name]
    
    # Then check database for custom permissions
    stmt = text("""
        SELECT p.name 
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        JOIN roles r ON r.id = rp.role_id
        WHERE r.name = :role_name
    """)
    
    result = db.execute(stmt, {"role_name": role_name})
    permissions = [row[0] for row in result.fetchall()]
    
    return permissions

def get_user_role_by_experience(experience_points: int) -> str:
    """Determine user role based on experience points"""
    if experience_points >= 1001:
        return "mentor"
    elif experience_points >= 101:
        return "player"
    else:
        return "guest"

def check_permission(required_permission: str, user_permissions: List[str]) -> bool:
    """Check if user has required permission"""
    return required_permission in user_permissions or "full_access" in user_permissions

def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)) -> User:
    """
    Get the current user from the JWT token with role and permission validation
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
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

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(token: str = Depends(lambda: None), db: Session = Depends(get_db)) -> User:
        user = get_current_user(token, db)
        
        # Get user permissions
        role_name = user.role.name if user.role else "guest"
        user_permissions = get_user_permissions(db, role_name)
        
        if not check_permission(permission, user_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        
        return user
    
    return permission_checker

def require_role(role: str):
    """Decorator to require specific role"""
    def role_checker(token: str = Depends(lambda: None), db: Session = Depends(get_db)) -> User:
        user = get_current_user(token, db)
        
        user_role = user.role.name if user.role else "guest"
        if user_role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {role}, Current: {user_role}"
            )
        
        return user
    
    return role_checker

def require_admin():
    """Decorator to require admin role"""
    return require_role("admin")

def require_mentor_or_admin():
    """Decorator to require mentor or admin role"""
    def role_checker(token: str = Depends(lambda: None), db: Session = Depends(get_db)) -> User:
        user = get_current_user(token, db)
        
        user_role = user.role.name if user.role else "guest"
        if user_role not in ["admin", "mentor"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: admin or mentor, Current: {user_role}"
            )
        
        return user
    
    return role_checker
