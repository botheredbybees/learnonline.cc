from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
import bcrypt

from db.database import get_db
from auth.auth_handler import sign_jwt
from models.user import UserCreate

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    stmt = text("""
        SELECT id FROM users WHERE email = :email
    """)
    result = db.execute(stmt, {"email": user.email})
    if result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    stmt = text("""
        SELECT id FROM users WHERE username = :username
    """)
    result = db.execute(stmt, {"username": user.username})
    if result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Hash password
    password_hash = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user
    user_id = str(uuid.uuid4())
    stmt = text("""
        INSERT INTO users (
            id, username, email, password, full_name, level, disabled, is_admin
        ) VALUES (
            :id, :username, :email, :password_hash, :full_name, 'player', false, false
        )
        RETURNING id
    """)
    
    result = db.execute(
        stmt,
        {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "password_hash": password_hash.decode('utf-8'),
            "full_name": user.full_name or ""
        }
    )
    db.commit()
    
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    # Special case for admin user
    if form_data.username == 'admin@example.com' and form_data.password == 'Ex14://learnonline':
        # Generate a token for admin
        admin_id = str(uuid.uuid4())
        token_data = sign_jwt(admin_id)
        
        return {
            "access_token": token_data["access_token"],
            "token_type": token_data["token_type"],
            "user_id": admin_id,
            "username": "admin",
            "email": "admin@example.com",
            "is_admin": True
        }
    
    # Normal user login process
    # Get user by username or email
    stmt = text("""
        SELECT id, email, username, password, is_admin
        FROM users
        WHERE (username = :username OR email = :username) AND (disabled IS NULL OR disabled = false)
    """)
    
    result = db.execute(stmt, {"username": form_data.username})
    user = result.fetchone()
    
    # Check if user exists and password is correct
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate token
    token_data = sign_jwt(str(user.id))
    
    # Return token and user data
    return {
        "access_token": token_data["access_token"],
        "token_type": token_data["token_type"],
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }
