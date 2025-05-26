"""
Achievements Router - Manages achievement records and user achievements.

This module provides endpoints for:
- Creating, retrieving, updating, and deleting achievements
- Managing user achievement records
- Awarding achievements to users
- Retrieving user achievement statistics

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import uuid
from uuid import UUID
from datetime import datetime

from models.tables import Achievement, UserAchievement
from models.schemas import AchievementSchema, UserAchievementSchema, AchievementCreateSchema, AchievementUpdateSchema, UserAchievementCreateSchema
from db.database import get_db

router = APIRouter(
    prefix="/achievements",
    tags=["achievements"],
    responses={404: {"description": "Achievement not found"}},
)


@router.get("/", response_model=List[AchievementSchema])
async def get_all_achievements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all achievements with pagination support.
    
    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    
    Returns:
    - List of achievement objects with their details
    """
    achievements = db.query(Achievement).offset(skip).limit(limit).all()
    return achievements


@router.get("/{achievement_id}", response_model=AchievementSchema)
async def get_achievement_by_id(
    achievement_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific achievement by its ID.
    
    Parameters:
    - **achievement_id**: The unique identifier of the achievement
    
    Returns:
    - Achievement object with full details
    
    Raises:
    - 404: Achievement not found
    """
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if achievement is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    return achievement


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AchievementSchema)
async def create_achievement(
    achievement_data: AchievementCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new achievement.
    
    Parameters:
    - **achievement_data**: Achievement data including title, description, icon_url, and experience_points
    
    Returns:
    - Newly created achievement object
    
    Raises:
    - 400: Validation error
    """
    new_achievement = Achievement(**achievement_data.model_dump())
    db.add(new_achievement)
    db.commit()
    db.refresh(new_achievement)
    
    return new_achievement


@router.put("/{achievement_id}", response_model=AchievementSchema)
async def update_achievement(
    achievement_id: int,
    achievement_data: AchievementUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update an existing achievement.
    
    Parameters:
    - **achievement_id**: The ID of the achievement to update
    - **achievement_data**: Updated achievement data
    
    Returns:
    - Updated achievement object
    
    Raises:
    - 404: Achievement not found
    - 400: Validation error
    """
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if achievement is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Convert Pydantic model to dict
    achievement_data_dict = achievement_data.model_dump(exclude_unset=True)
    for key, value in achievement_data_dict.items():
        setattr(achievement, key, value)
    
    db.commit()
    db.refresh(achievement)
    
    return achievement


@router.delete("/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_achievement(
    achievement_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an achievement.
    
    Parameters:
    - **achievement_id**: The ID of the achievement to delete
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Achievement not found
    """
    achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
    if achievement is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    db.delete(achievement)
    db.commit()
    
    return None


# User Achievement Endpoints
@router.get("/user/{user_id}", response_model=List[UserAchievementSchema])
async def get_user_achievements(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve all achievements for a specific user.
    
    Parameters:
    - **user_id**: The UUID of the user
    
    Returns:
    - List of user achievement objects with achievement details
    """
    user_achievements = db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    
    result = []
    for ua in user_achievements:
        achievement = db.query(Achievement).filter(Achievement.id == ua.achievement_id).first()
        if achievement:
            # Create a UserAchievementSchema with the achievement included
            ua.achievement = achievement
            result.append(ua)
    
    return result


@router.post("/award", status_code=status.HTTP_201_CREATED, response_model=UserAchievementSchema)
async def award_achievement(
    user_achievement_data: UserAchievementCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Award an achievement to a user.
    
    Parameters:
    - **user_achievement_data**: Data including user_id and achievement_id
    
    Returns:
    - Newly created user achievement record
    
    Raises:
    - 400: Validation error
    - 404: Achievement not found
    - 409: User already has this achievement
    """
    # Check if achievement exists
    achievement = db.query(Achievement).filter(Achievement.id == user_achievement_data.achievement_id).first()
    if achievement is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    # Check if user already has this achievement
    existing = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_achievement_data.user_id,
        UserAchievement.achievement_id == user_achievement_data.achievement_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already has this achievement"
        )
    
    # Create a dict from the Pydantic model
    user_achievement_dict = user_achievement_data.model_dump()
    
    # Set awarded_at if not provided
    if user_achievement_dict.get("awarded_at") is None:
        user_achievement_dict["awarded_at"] = datetime.now()
    
    new_user_achievement = UserAchievement(**user_achievement_dict)
    db.add(new_user_achievement)
    db.commit()
    db.refresh(new_user_achievement)
    
    return new_user_achievement


@router.delete("/user/{user_id}/achievement/{achievement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_achievement(
    user_id: uuid.UUID,
    achievement_id: int,
    db: Session = Depends(get_db)
):
    """
    Revoke an achievement from a user.
    
    Parameters:
    - **user_id**: The UUID of the user
    - **achievement_id**: The ID of the achievement to revoke
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: User achievement record not found
    """
    user_achievement = db.query(UserAchievement).filter(
        UserAchievement.user_id == user_id,
        UserAchievement.achievement_id == achievement_id
    ).first()
    
    if user_achievement is None:
        raise HTTPException(status_code=404, detail="User achievement record not found")
    
    db.delete(user_achievement)
    db.commit()
    
    return None
