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

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str
    email: str
    is_admin: bool

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
            id, email, username, password_hash, full_name, disabled, is_admin
        ) VALUES (
            :id, :email, :username, :password_hash, :full_name, false, false
        )
    """)
    
    db.execute(stmt, {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "password_hash": password_hash.decode('utf-8'),
        "full_name": user.full_name
    })
    
    db.commit()
    
    # Generate token
    return sign_jwt(user_id)

@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    # Get user by username
    stmt = text("""
        SELECT id, email, username, password_hash, is_admin
        FROM users
        WHERE username = :username AND disabled = false
    """)
    
    result = db.execute(stmt, {"username": form_data.username})
    user = result.fetchone()
    
    # Check if user exists and password is correct
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
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
