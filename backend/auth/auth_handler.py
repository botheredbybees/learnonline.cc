import os
import time
from typing import Dict, Optional
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.database import get_db
from models.user import User

# Load environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))  # Default 1 hour

def token_response(token: str):
    return {
        "access_token": token,
        "token_type": "bearer"
    }

def sign_jwt(user_id: str) -> Dict[str, str]:
    """
    Create a new JWT token for a user
    """
    payload = {
        "user_id": user_id,
        "exp": time.time() + TOKEN_EXPIRE_MINUTES * 60,
        "iat": time.time()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return token_response(token)

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
    except:
        return None

def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)) -> User:
    """
    Get the current user from the JWT token
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
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    stmt = text("""
        SELECT * FROM users WHERE id = :user_id
    """)
    
    result = db.execute(stmt, {"user_id": payload["user_id"]})
    user = result.fetchone()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Convert to User model
    return User(**dict(user))
