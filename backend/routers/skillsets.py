"""
Skillsets Router - Manages skillset records in the system.

This module provides endpoints for:
- Listing and retrieving skillsets and their details
- Searching skillsets from local database
- Creating, updating, and managing skillsets
- Controlling skillset visibility and accessibility

All endpoints are documented with appropriate response models and error responses
for integration with Swagger UI and ReDoc.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from models.tables import Skillset
from models.schemas import SkillsetSchema, SkillsetCreateSchema, SkillsetUpdateSchema
from db.database import get_db

router = APIRouter(
    prefix="/skillsets",
    tags=["skillsets"],
    responses={404: {"description": "Skillset not found"}},
)


@router.get("/", response_model=List[SkillsetSchema])
async def get_all_skillsets(
    skip: int = 0,
    limit: int = 100,
    visible_only: bool = True,
    db: Session = Depends(get_db)
):
    """
    Retrieve all skillsets with pagination support.
    
    Parameters:
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **visible_only**: If True, only return visible skillsets
    
    Returns:
    - List of skillset objects with their details
    """
    if visible_only:
        skillsets = db.query(Skillset).filter(Skillset.visible == True).offset(skip).limit(limit).all()
    else:
        skillsets = db.query(Skillset).offset(skip).limit(limit).all()
    
    return skillsets


@router.get("/{skillset_id}", response_model=SkillsetSchema)
async def get_skillset_by_id(
    skillset_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific skillset by its ID.
    
    Parameters:
    - **skillset_id**: The unique identifier of the skillset
    
    Returns:
    - Skillset object with full details
    
    Raises:
    - 404: Skillset not found
    """
    skillset = db.query(Skillset).filter(Skillset.id == skillset_id).first()
    if skillset is None:
        raise HTTPException(status_code=404, detail="Skillset not found")
    
    return skillset


@router.get("/code/{skillset_code}", response_model=SkillsetSchema)
async def get_skillset_by_code(
    skillset_code: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific skillset by its code.
    
    Parameters:
    - **skillset_code**: The unique skillset code
    
    Returns:
    - Skillset object with full details
    
    Raises:
    - 404: Skillset not found
    """
    skillset = db.query(Skillset).filter(Skillset.code == skillset_code).first()
    if skillset is None:
        raise HTTPException(status_code=404, detail="Skillset not found")
    
    return skillset


@router.get("/search/", response_model=List[SkillsetSchema])
async def search_skillsets(
    query: str,
    training_package_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Search for skillsets by title, code, or description.
    
    Parameters:
    - **query**: Search string to match against skillset fields
    - **training_package_id**: Optional filter by training package ID
    
    Returns:
    - List of matching skillset objects
    """
    search_term = f"%{query}%"
    
    if training_package_id:
        skillsets = db.query(Skillset).filter(
            Skillset.training_package_id == training_package_id,
            ((Skillset.title.ilike(search_term)) | 
             (Skillset.code.ilike(search_term)) |
             (Skillset.description.ilike(search_term))),
            Skillset.visible == True
        ).all()
    else:
        skillsets = db.query(Skillset).filter(
            ((Skillset.title.ilike(search_term)) | 
             (Skillset.code.ilike(search_term)) |
             (Skillset.description.ilike(search_term))),
            Skillset.visible == True
        ).all()
    
    return skillsets


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SkillsetSchema)
async def create_skillset(
    skillset_data: SkillsetCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Create a new skillset record.
    
    Parameters:
    - **skillset_data**: Skillset data including code, title, and description
    
    Returns:
    - Newly created skillset object
    
    Raises:
    - 400: Validation error
    - 409: Skillset with this code already exists
    """
    # Check if skillset with this code already exists
    existing = db.query(Skillset).filter(Skillset.code == skillset_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Skillset with code {skillset_data.code} already exists"
        )
    
    new_skillset = Skillset(**skillset_data.model_dump())
    db.add(new_skillset)
    db.commit()
    db.refresh(new_skillset)
    
    return new_skillset


@router.put("/{skillset_id}", response_model=SkillsetSchema)
async def update_skillset(
    skillset_id: int,
    skillset_data: SkillsetUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update an existing skillset record.
    
    Parameters:
    - **skillset_id**: The ID of the skillset to update
    - **skillset_data**: Updated skillset data
    
    Returns:
    - Updated skillset object
    
    Raises:
    - 404: Skillset not found
    - 400: Validation error
    """
    skillset = db.query(Skillset).filter(Skillset.id == skillset_id).first()
    if skillset is None:
        raise HTTPException(status_code=404, detail="Skillset not found")
    
    # Convert Pydantic model to dict
    skillset_data_dict = skillset_data.model_dump(exclude_unset=True)
    for key, value in skillset_data_dict.items():
        setattr(skillset, key, value)
    
    db.commit()
    db.refresh(skillset)
    
    return skillset


@router.delete("/{skillset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skillset(
    skillset_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a skillset record.
    
    Parameters:
    - **skillset_id**: The ID of the skillset to delete
    
    Returns:
    - 204 No Content
    
    Raises:
    - 404: Skillset not found
    """
    skillset = db.query(Skillset).filter(Skillset.id == skillset_id).first()
    if skillset is None:
        raise HTTPException(status_code=404, detail="Skillset not found")
    
    db.delete(skillset)
    db.commit()
    
    return None
