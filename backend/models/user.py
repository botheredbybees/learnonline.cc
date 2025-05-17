from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserBase):
    id: UUID
    password: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
