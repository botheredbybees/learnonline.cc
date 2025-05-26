"""
User Progress Router - Manages user progress tracking for training units.

This module provides endpoints for:
- Retrieving user progress for specific units
- Creating and updating user progress records
- Tracking completion status and percentages
- Generating progress reports and statistics

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import uuid
from uuid import UUID

from models.tables import UserProgress
from models.schemas import UserProgressSchema, UserProgressCreateSchema, UserProgressUpdateSchema
from db.database import get_db

router = APIRouter(
    prefix="/user-progress",
    tags=["user-progress"],
    responses={404: {"description": "Progress record not found"}},
)


@router.get("/user/{user_id}", response_model=List[UserProgressSchema])
async def get_user_progress(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve all progress records for a specific user.
    
    Parameters:
    - **user_id**: The UUID of the user
    
    Returns:
    - List of user progress objects
    """
    progress_records = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    return progress_records


@router.get("/unit/{unit_id}", response_model=List[UserProgressSchema])
async def get_unit_progress(
    unit_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve all progress records for a specific training unit.
    
    Parameters:
    - **unit_id**: The ID of the unit
    
    Returns:
    - List of user progress objects for the specified unit
    """
    progress_records = db.query(UserProgress).filter(UserProgress.unit_id == unit_id).all()
    return progress_records


@router.get("/{progress_id}", response_model=UserProgressSchema)
async def get_progress_by_id(
    progress_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific progress record by its ID.
    
    Parameters:
    - **progress_id**: The unique identifier of the progress record
    
    Returns:
    - Progress record with full details
    
    Raises:
    - 404: Progress record not found
    """
    progress = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    return progress


@router.get("/user/{user_id}/unit/{unit_id}", response_model=UserProgressSchema)
async def get_specific_progress(
    user_id: uuid.UUID,
    unit_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve progress for a specific user and unit combination.
    
    Parameters:
    - **user_id**: The UUID of the user
    - **unit_id**: The ID of the unit
    
    Returns:
    - Progress record if found
    
    Raises:
    - 404: Progress record not found
    """
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.unit_id == unit_id
    ).first()
    
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    return progress


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserProgressSchema)
async def create_progress_record(
    progress_data: UserProgressCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new progress record.
    
    Parameters:
    - **progress_data**: Progress data including user_id, unit_id, status, and other fields
    
    Returns:
    - Newly created progress record
    
    Raises:
    - 400: Validation error
    - 409: Progress record already exists for this user and unit
    """
    # Check if progress record already exists for this user and unit
    existing = db.query(UserProgress).filter(
        UserProgress.user_id == progress_data.user_id,
        UserProgress.unit_id == progress_data.unit_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Progress record already exists for this user and unit"
        )
    
    new_progress = UserProgress(**progress_data.model_dump())
    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)
    
    return new_progress


@router.put("/{progress_id}", response_model=UserProgressSchema)
async def update_progress_record(
    progress_id: int,
    progress_data: UserProgressUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update an existing progress record.
    
    Parameters:
    - **progress_id**: The ID of the progress record to update
    - **progress_data**: Updated progress data with fields that can be modified
    
    Returns:
    - Updated progress record
    
    Raises:
    - 404: Progress record not found
    - 400: Validation error
    """
    progress = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    # Convert Pydantic model to dict
    progress_data_dict = progress_data.model_dump(exclude_unset=True)
    for key, value in progress_data_dict.items():
        setattr(progress, key, value)
    
    db.commit()
    db.refresh(progress)
    
    return progress


@router.put("/user/{user_id}/unit/{unit_id}", response_model=UserProgressSchema)
async def update_specific_progress(
    user_id: uuid.UUID,
    unit_id: int,
    progress_data: UserProgressUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update progress for a specific user and unit combination.
    
    Parameters:
    - **user_id**: The UUID of the user
    - **unit_id**: The ID of the unit
    - **progress_data**: Updated progress data with fields that can be modified
    
    Returns:
    - Updated progress record
    
    Raises:
    - 404: Progress record not found
    - 400: Validation error
    """
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.unit_id == unit_id
    ).first()
    
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    # Convert Pydantic model to dict
    progress_data_dict = progress_data.model_dump(exclude_unset=True)
    for key, value in progress_data_dict.items():
        setattr(progress, key, value)
    
    db.commit()
    db.refresh(progress)
    
    return progress


@router.delete("/{progress_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_progress_record(
    progress_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a progress record.
    
    Parameters:
    - **progress_id**: The ID of the progress record to delete
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Progress record not found
    """
    progress = db.query(UserProgress).filter(UserProgress.id == progress_id).first()
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    db.delete(progress)
    db.commit()
    
    return None
