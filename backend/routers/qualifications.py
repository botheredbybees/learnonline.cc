"""
Qualifications Router - Manages qualification records in the system.

This module provides endpoints for:
- Listing and retrieving qualifications and their details
- Searching qualifications from local database and external sources
- Creating, updating, and managing qualifications
- Controlling qualification visibility and accessibility

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from models.tables import Qualification
from models.schemas import QualificationSchema, QualificationCreateSchema, QualificationUpdateSchema
from db.database import get_db

router = APIRouter(
    prefix="/qualifications",
    tags=["qualifications"],
    responses={404: {"description": "Qualification not found"}},
)


@router.get("/", response_model=List[QualificationSchema])
async def get_all_qualifications(
    skip: int = 0,
    limit: int = 100,
    visible_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Retrieve all qualifications with pagination support.
    
    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **visible_only**: If True, only return visible qualifications
    
    Returns:
    - List of qualification objects with their details
    """
    if visible_only:
        qualifications = db.query(Qualification).filter(Qualification.visible == True).offset(skip).limit(limit).all()
    else:
        qualifications = db.query(Qualification).offset(skip).limit(limit).all()
    
    return qualifications


@router.get("/{qualification_id}", response_model=QualificationSchema)
async def get_qualification_by_id(
    qualification_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific qualification by its ID.
    
    Parameters:
    - **qualification_id**: The unique identifier of the qualification
    
    Returns:
    - Qualification object with full details
    
    Raises:
    - 404: Qualification not found
    """
    qualification = db.query(Qualification).filter(Qualification.id == qualification_id).first()
    if qualification is None:
        raise HTTPException(status_code=404, detail="Qualification not found")
    
    return qualification


@router.get("/code/{qualification_code}", response_model=QualificationSchema)
async def get_qualification_by_code(
    qualification_code: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific qualification by its code.
    
    Parameters:
    - **qualification_code**: The unique qualification code (e.g., "BSB50420")
    
    Returns:
    - Qualification object with full details
    
    Raises:
    - 404: Qualification not found
    """
    qualification = db.query(Qualification).filter(Qualification.code == qualification_code).first()
    if qualification is None:
        raise HTTPException(status_code=404, detail="Qualification not found")
    
    return qualification


@router.get("/search/", response_model=List[QualificationSchema])
async def search_qualifications(
    query: str,
    training_package_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Search for qualifications by title, code, or description.
    
    Parameters:
    - **query**: Search string to match against qualification fields
    - **training_package_id**: Optional filter by training package ID
    
    Returns:
    - List of matching qualification objects
    """
    search_term = f"%{query}%"
    
    if training_package_id:
        qualifications = db.query(Qualification).filter(
            Qualification.training_package_id == training_package_id,
            ((Qualification.title.ilike(search_term)) | 
             (Qualification.code.ilike(search_term)) |
             (Qualification.description.ilike(search_term))),
            Qualification.visible == True
        ).all()
    else:
        qualifications = db.query(Qualification).filter(
            ((Qualification.title.ilike(search_term)) | 
             (Qualification.code.ilike(search_term)) |
             (Qualification.description.ilike(search_term))),
            Qualification.visible == True
        ).all()
    
    return qualifications


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=QualificationSchema)
async def create_qualification(
    qualification_data: QualificationCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new qualification record.
    
    Parameters:
    - **qualification_data**: Qualification data including code, title, and description
    
    Returns:
    - Newly created qualification object
    
    Raises:
    - 400: Validation error
    - 409: Qualification with this code already exists
    """
    # Check if qualification with this code already exists
    existing = db.query(Qualification).filter(Qualification.code == qualification_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Qualification with code {qualification_data.code} already exists"
        )
    
    new_qualification = Qualification(**qualification_data.model_dump())
    db.add(new_qualification)
    db.commit()
    db.refresh(new_qualification)
    
    return new_qualification


@router.put("/{qualification_id}", response_model=QualificationSchema)
async def update_qualification(
    qualification_id: int,
    qualification_data: QualificationUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update an existing qualification record.
    
    Parameters:
    - **qualification_id**: The ID of the qualification to update
    - **qualification_data**: Updated qualification data
    
    Returns:
    - Updated qualification object
    
    Raises:
    - 404: Qualification not found
    - 400: Validation error
    """
    qualification = db.query(Qualification).filter(Qualification.id == qualification_id).first()
    if qualification is None:
        raise HTTPException(status_code=404, detail="Qualification not found")
    
    # Convert Pydantic model to dict
    qualification_data_dict = qualification_data.model_dump(exclude_unset=True)
    for key, value in qualification_data_dict.items():
        setattr(qualification, key, value)
    
    db.commit()
    db.refresh(qualification)
    
    return qualification


@router.delete("/{qualification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qualification(
    qualification_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a qualification record.
    
    Parameters:
    - **qualification_id**: The ID of the qualification to delete
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Qualification not found
    """
    qualification = db.query(Qualification).filter(Qualification.id == qualification_id).first()
    if qualification is None:
        raise HTTPException(status_code=404, detail="Qualification not found")
    
    db.delete(qualification)
    db.commit()
    
    return None
