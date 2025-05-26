"""
Badges Router - Manages badge records and user badges.

This module provides endpoints for:
- Creating, retrieving, updating, and deleting badges
- Managing user badge records
- Awarding badges to users
- Retrieving user badge statistics

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import uuid
from uuid import UUID
from datetime import datetime

from models.tables import Badge, UserBadge
from models.schemas import BadgeSchema, UserBadgeSchema, BadgeCreateSchema, BadgeUpdateSchema, UserBadgeCreateSchema
from db.database import get_db

router = APIRouter(
    prefix="/badges",
    tags=["badges"],
    responses={404: {"description": "Badge not found"}},
)


@router.get("/", response_model=List[BadgeSchema])
async def get_all_badges(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all badges with pagination support.
    
    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    
    Returns:
    - List of badge objects with their details
    """
    badges = db.query(Badge).offset(skip).limit(limit).all()
    return badges


@router.get("/{badge_id}", response_model=BadgeSchema)
async def get_badge_by_id(
    badge_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific badge by its ID.
    
    Parameters:
    - **badge_id**: The unique identifier of the badge
    
    Returns:
    - Badge object with full details
    
    Raises:
    - 404: Badge not found
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if badge is None:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    return badge


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BadgeSchema)
async def create_badge(
    badge_data: BadgeCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new badge.
    
    Parameters:
    - **badge_data**: Badge data including title, description, and icon_url
    
    Returns:
    - Newly created badge object
    
    Raises:
    - 400: Validation error
    """
    new_badge = Badge(**badge_data.model_dump())
    db.add(new_badge)
    db.commit()
    db.refresh(new_badge)
    
    return new_badge


@router.put("/{badge_id}", response_model=BadgeSchema)
async def update_badge(
    badge_id: int,
    badge_data: BadgeUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update an existing badge.
    
    Parameters:
    - **badge_id**: The ID of the badge to update
    - **badge_data**: Updated badge data
    
    Returns:
    - Updated badge object
    
    Raises:
    - 404: Badge not found
    - 400: Validation error
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if badge is None:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    # Convert Pydantic model to dict
    badge_data_dict = badge_data.model_dump(exclude_unset=True)
    for key, value in badge_data_dict.items():
        setattr(badge, key, value)
    
    db.commit()
    db.refresh(badge)
    
    return badge


@router.delete("/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_badge(
    badge_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a badge.
    
    Parameters:
    - **badge_id**: The ID of the badge to delete
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Badge not found
    """
    badge = db.query(Badge).filter(Badge.id == badge_id).first()
    if badge is None:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    db.delete(badge)
    db.commit()
    
    return None


# User Badge Endpoints
@router.get("/user/{user_id}", response_model=List[UserBadgeSchema])
async def get_user_badges(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve all badges for a specific user.
    
    Parameters:
    - **user_id**: The UUID of the user
    
    Returns:
    - List of user badge objects with badge details
    """
    user_badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    
    result = []
    for ub in user_badges:
        badge = db.query(Badge).filter(Badge.id == ub.badge_id).first()
        if badge:
            # Create a UserBadgeSchema with the badge included
            ub.badge = badge
            result.append(ub)
    
    return result


@router.post("/award", status_code=status.HTTP_201_CREATED, response_model=UserBadgeSchema)
async def award_badge(
    user_badge_data: UserBadgeCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Award a badge to a user.
    
    Parameters:
    - **user_badge_data**: Data including user_id and badge_id
    
    Returns:
    - Newly created user badge record
    
    Raises:
    - 400: Validation error
    - 404: Badge not found
    - 409: User already has this badge
    """
    # Check if badge exists
    badge = db.query(Badge).filter(Badge.id == user_badge_data.badge_id).first()
    if badge is None:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    # Check if user already has this badge
    existing = db.query(UserBadge).filter(
        UserBadge.user_id == user_badge_data.user_id,
        UserBadge.badge_id == user_badge_data.badge_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User already has this badge"
        )
    
    # Create a dict from the Pydantic model
    user_badge_dict = user_badge_data.model_dump()
    
    # Set awarded_at if not provided
    if user_badge_dict.get("awarded_at") is None:
        user_badge_dict["awarded_at"] = datetime.now()
    
    new_user_badge = UserBadge(**user_badge_dict)
    db.add(new_user_badge)
    db.commit()
    db.refresh(new_user_badge)
    
    return new_user_badge


@router.delete("/user/{user_id}/badge/{badge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_badge(
    user_id: uuid.UUID,
    badge_id: int,
    db: Session = Depends(get_db)
):
    """
    Revoke a badge from a user.
    
    Parameters:
    - **user_id**: The UUID of the user
    - **badge_id**: The ID of the badge to revoke
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: User badge record not found
    """
    user_badge = db.query(UserBadge).filter(
        UserBadge.user_id == user_id,
        UserBadge.badge_id == badge_id
    ).first()
    
    if user_badge is None:
        raise HTTPException(status_code=404, detail="User badge record not found")
    
    db.delete(user_badge)
    db.commit()
    
    return None
