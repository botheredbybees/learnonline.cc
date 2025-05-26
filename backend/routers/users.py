"""
Users Router - Manages user accounts and profiles.

This module provides endpoints for:
- User account management (create, update, delete)
- User profile management
- User role assignments and permissions
- User data retrieval and filtering

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import uuid
from uuid import UUID

from models.tables import User, UserProfile, Role
from models.schemas import UserSchema, UserProfileSchema, UserUpdateSchema, UserProfileUpdateSchema
from db.database import get_db
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "User not found"}},
)


@router.get("/", response_model=List[UserSchema], dependencies=[Depends(JWTBearer())])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all users with pagination and filtering support.
    
    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **role_id**: Filter users by role ID
    - **is_active**: Filter users by active status
    
    Returns:
    - List of user objects with their details
    
    Requires:
    - Valid JWT token with administrative privileges
    """
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to list all users")
    
    query = db.query(User)
    
    if role_id is not None:
        query = query.filter(User.role_id == role_id)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserSchema, dependencies=[Depends(JWTBearer())])
async def get_user_by_id(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific user by ID.
    
    Parameters:
    - **user_id**: User UUID
    
    Returns:
    - User object with full details
    
    Raises:
    - 404: User not found
    - 403: Not authorized to view this user
    
    Requires:
    - Valid JWT token with appropriate permissions
    """
    # Users can view their own profile, admins can view any profile
    if str(current_user.id) != str(user_id) and (not hasattr(current_user, "role") or current_user.role.name != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to view this user")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.put("/{user_id}", response_model=UserSchema, dependencies=[Depends(JWTBearer())])
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user information.
    
    Parameters:
    - **user_id**: User UUID
    - **user_data**: Updated user data with fields that can be modified
    
    Returns:
    - Updated user object
    
    Raises:
    - 404: User not found
    - 403: Not authorized to update this user
    
    Requires:
    - Valid JWT token with appropriate permissions
    """
    # Users can update their own profile, admins can update any profile
    if str(current_user.id) != str(user_id) and (not hasattr(current_user, "role") or current_user.role.name != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert Pydantic model to dict, excluding password_hash
    user_data_dict = user_data.model_dump(exclude={"password_hash"})
    
    # Don't allow users to change their own role
    if str(current_user.id) == str(user_id) and "role_id" in user_data_dict:
        del user_data_dict["role_id"]
    
    for key, value in user_data_dict.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(JWTBearer())])
async def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete or deactivate a user account.
    
    Parameters:
    - **user_id**: User UUID
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: User not found
    - 403: Not authorized to delete this user
    
    Requires:
    - Valid JWT token with administrative privileges
    """
    # Only admins can delete users
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete users")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # In many systems, we don't actually delete users, just deactivate them
    setattr(user, "is_active", False)
    db.commit()
    
    # Or if we want to actually delete:
    # db.delete(user)
    # db.commit()
    
    return None


@router.get("/{user_id}/profile", response_model=UserProfileSchema, dependencies=[Depends(JWTBearer())])
async def get_user_profile(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a user's profile information.
    
    Parameters:
    - **user_id**: User UUID
    
    Returns:
    - User profile object
    
    Raises:
    - 404: User or profile not found
    - 403: Not authorized to view this profile
    
    Requires:
    - Valid JWT token with appropriate permissions
    """
    # Users can view their own profile, admins can view any profile
    if str(current_user.id) != str(user_id) and (not hasattr(current_user, "role") or current_user.role.name != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to view this profile")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return profile


@router.put("/{user_id}/profile", response_model=UserProfileSchema, dependencies=[Depends(JWTBearer())])
async def update_user_profile(
    user_id: uuid.UUID,
    profile_data: UserProfileUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user's profile information.
    
    Parameters:
    - **user_id**: User UUID
    - **profile_data**: Updated profile data with fields that can be modified
    
    Returns:
    - Updated profile object
    
    Raises:
    - 404: User or profile not found
    - 403: Not authorized to update this profile
    
    Requires:
    - Valid JWT token with appropriate permissions
    """
    # Users can update their own profile, admins can update any profile
    if str(current_user.id) != str(user_id) and (not hasattr(current_user, "role") or current_user.role.name != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        # Create profile if it doesn't exist
        profile_data_dict = profile_data.model_dump()
        profile_data_dict["user_id"] = user_id
        new_profile = UserProfile(**profile_data_dict)
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile
    
    # Convert Pydantic model to dict
    profile_data_dict = profile_data.model_dump()
    for key, value in profile_data_dict.items():
        setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    
    return profile
