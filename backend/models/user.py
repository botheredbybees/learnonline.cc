from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class UserLevel(str, Enum):
    GUEST = "guest"
    PLAYER = "player" 
    MENTOR = "mentor"

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    disabled: bool = False
    is_admin: bool = False
    experience_points: int = 0
    level: UserLevel = UserLevel.GUEST
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

class UserInDB(User):
    password_hash: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpassword123",
                "full_name": "John Doe"
            }
        }

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_admin: Optional[bool] = None
    experience_points: Optional[int] = None
    level: Optional[UserLevel] = None
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "username": "newusername",
                "full_name": "Updated Name",
                "experience_points": 150,
                "level": "player"
            }
        }

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    disabled: bool
    is_admin: bool
    experience_points: int
    level: UserLevel
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
