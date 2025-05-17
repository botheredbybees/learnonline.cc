from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from db.database import get_db
from models.user import User
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={404: {"description": "Not found"}},
)

class UnitBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None

class UnitResponse(UnitBase):
    id: int
    training_package_id: Optional[int] = None
    elements: Optional[List[dict]] = None
    
    class Config:
        orm_mode = True

@router.get("", response_model=List[UnitResponse])
async def get_units(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all units"""
    stmt = text("""
        SELECT 
            id, code, title, description, training_package_id, elements_json as elements
        FROM units
        ORDER BY code
        LIMIT :limit OFFSET :skip
    """)
    
    result = db.execute(stmt, {"limit": limit, "skip": skip})
    units = result.fetchall()
    
    # Convert to list of dicts
    return [dict(unit) for unit in units]

@router.get("/{unit_id}", response_model=UnitResponse)
async def get_unit(unit_id: int, db: Session = Depends(get_db)):
    """Get a specific unit by ID"""
    stmt = text("""
        SELECT 
            id, code, title, description, training_package_id, elements_json as elements
        FROM units
        WHERE id = :unit_id
    """)
    
    result = db.execute(stmt, {"unit_id": unit_id})
    unit = result.fetchone()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return dict(unit)

@router.get("/code/{unit_code}", response_model=UnitResponse)
async def get_unit_by_code(unit_code: str, db: Session = Depends(get_db)):
    """Get a specific unit by code"""
    stmt = text("""
        SELECT 
            id, code, title, description, training_package_id, elements_json as elements
        FROM units
        WHERE code = :unit_code
    """)
    
    result = db.execute(stmt, {"unit_code": unit_code})
    unit = result.fetchone()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return dict(unit)

@router.get("/{unit_id}/elements")
async def get_unit_elements(unit_id: int, db: Session = Depends(get_db)):
    """Get elements and performance criteria for a unit"""
    # First check if the unit exists
    stmt = text("""
        SELECT id, code, title 
        FROM units 
        WHERE id = :unit_id
    """)
    
    result = db.execute(stmt, {"unit_id": unit_id})
    unit = result.fetchone()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Get elements
    stmt = text("""
        SELECT 
            id, element_num, element_text
        FROM unit_elements
        WHERE unit_id = :unit_id
        ORDER BY element_num
    """)
    
    result = db.execute(stmt, {"unit_id": unit_id})
    elements = [dict(row) for row in result]
    
    # Get performance criteria for each element
    for element in elements:
        stmt = text("""
            SELECT 
                id, pc_num, pc_text
            FROM unit_performance_criteria
            WHERE element_id = :element_id
            ORDER BY pc_num
        """)
        
        result = db.execute(stmt, {"element_id": element["id"]})
        element["performance_criteria"] = [dict(row) for row in result]
    
    return {
        "unit": dict(unit),
        "elements": elements
    }
