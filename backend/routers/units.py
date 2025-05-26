"""
Units Router - Manages training units, which are the core components of qualifications.

This module provides endpoints for:
- Listing and retrieving units and their components (elements, performance criteria)
- Searching units from local database and TGA API
- Synchronizing units with TGA data
- Managing visibility and accessibility of units
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Sequence, Dict, Any
from db.database import get_db, SessionLocal
import models.tables as models
from models.schemas import (
    UnitSchema, UnitElementSchema, UnitPerformanceCriteriaSchema,
    UnitCriticalAspectSchema, UnitRequiredSkillSchema
)
import os
from sqlalchemy import text
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user
from services.tga.client import TrainingGovClient

router = APIRouter(
    prefix="/api/units",
    tags=["units"]
)

@router.get("/", response_model=List[UnitSchema])
async def list_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    training_package_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> Sequence[models.Unit]:
    """List all units with optional filtering"""
    query = db.query(models.Unit)
    
    if training_package_id:
        query = query.filter(models.Unit.training_package_id == training_package_id)
    if status:
        query = query.filter(models.Unit.status == status)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{unit_id}", response_model=UnitSchema)
async def get_unit(unit_id: int, db: Session = Depends(get_db)):
    """Get a specific unit by ID"""
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.get("/code/{unit_code}", response_model=UnitSchema)
async def get_unit_by_code(unit_code: str, db: Session = Depends(get_db)):
    """Get a specific unit by code"""
    unit = db.query(models.Unit).filter(models.Unit.code == unit_code).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

@router.get("/{unit_id}/elements", response_model=List[UnitElementSchema])
async def get_unit_elements(unit_id: int, db: Session = Depends(get_db)):
    """Get all elements for a unit"""
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return db.query(models.UnitElement).filter(
        models.UnitElement.unit_id == unit_id
    ).all()

@router.get("/{unit_id}/performance-criteria", response_model=List[UnitPerformanceCriteriaSchema])
async def get_unit_performance_criteria(unit_id: int, db: Session = Depends(get_db)):
    """Get all performance criteria for a unit"""
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return db.query(models.UnitPerformanceCriteria).filter(
        models.UnitPerformanceCriteria.unit_id == unit_id
    ).all()

@router.get("/{unit_id}/critical-aspects", response_model=List[UnitCriticalAspectSchema])
async def get_unit_critical_aspects(unit_id: int, db: Session = Depends(get_db)):
    """Get all critical aspects for a unit"""
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return db.query(models.UnitCriticalAspect).filter(
        models.UnitCriticalAspect.unit_id == unit_id
    ).all()

@router.get("/{unit_id}/required-skills", response_model=List[UnitRequiredSkillSchema])
async def get_unit_required_skills(unit_id: int, db: Session = Depends(get_db)):
    """Get all required skills for a unit"""
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return db.query(models.UnitRequiredSkill).filter(
        models.UnitRequiredSkill.unit_id == unit_id
    ).all()

@router.get("/{unit_id}/elements-with-pc")
async def get_unit_elements_with_performance_criteria(unit_id: int, db: Session = Depends(get_db)):
    """Get all elements with performance criteria for a unit"""
    # Check if unit exists
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Get elements
    elements = db.query(models.UnitElement).filter(
        models.UnitElement.unit_id == unit_id
    ).order_by(models.UnitElement.element_num).all()
    
    # Convert to dicts and add performance criteria
    result_elements = []
    for element in elements:
        element_dict = {
            "id": element.id,
            "element_num": element.element_num,
            "element_text": element.element_text
        }
        
        # Get performance criteria for this element
        pcs = db.query(models.UnitPerformanceCriteria).filter(
            models.UnitPerformanceCriteria.element_id == element.id
        ).order_by(models.UnitPerformanceCriteria.pc_num).all()
        
        element_dict["performance_criteria"] = [
            {
                "id": pc.id,
                "pc_num": pc.pc_num,
                "pc_text": pc.pc_text
            } for pc in pcs
        ]
        
        result_elements.append(element_dict)
    
    return {
        "unit": {
            "id": unit.id,
            "code": unit.code,
            "title": unit.title
        },
        "elements": result_elements
    }

@router.get("/search")
async def search_units(
    query: str,
    training_package_code: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Search units using TGA API and local database"""
    # First try local database - using ORM filter instead of raw SQL
    db_query = db.query(models.Unit).filter(
        # Using ilike for case-insensitive search on multiple fields
        (
            models.Unit.title.ilike(f"%{query}%") |
            models.Unit.description.ilike(f"%{query}%") |
            models.Unit.code.ilike(f"%{query}%")
        )
    )
    
    # Add training package filter if provided
    if training_package_code:
        db_query = db_query.filter(models.Unit.code.startswith(training_package_code))
    
    # Apply pagination and order
    db_query = db_query.order_by(models.Unit.code)
    db_query = db_query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    local_units = db_query.all()
    
    # Convert to dict representation
    local_units_dict = [
        {
            "id": unit.id,
            "code": unit.code,
            "title": unit.title,
            "description": unit.description,
            "training_package_id": unit.training_package_id,
            "release_date": unit.release_date,
            "status": unit.status
        } for unit in local_units
    ]
    
    # If we have enough results, return them
    if len(local_units_dict) >= page_size:
        return local_units_dict
    
    # Otherwise, search TGA API
    username = os.getenv("TGA_USERNAME")
    password = os.getenv("TGA_PASSWORD")
    if not username or not password:
        raise HTTPException(
            status_code=500,
            detail="TGA API credentials not configured"
        )
    
    client = TrainingGovClient(username=username, password=password)
    # Create filter for training package code if provided
    filter_text = query
    if training_package_code:
        filter_text = f"{filter_text} {training_package_code}"
        
    tga_response = client.search_components(
        filter_text=filter_text,
        page=page or 1,
        page_size=page_size or 20
    )
    
    # Extract the components from the response
    tga_units = tga_response.get('components', [])
    
    # For any new units from TGA, store them in our database
    for unit in tga_units:
        # Check if unit already exists
        existing_unit = db.query(models.Unit).filter(models.Unit.code == unit["code"]).first()
        
        if existing_unit:
            # Update existing unit with direct attribute assignment
            updates = {
                "title": unit["title"],
                "processed": "N"
            }
            
            if "description" in unit:
                updates["description"] = unit.get("description")
            if "status" in unit:
                updates["status"] = unit.get("status") 
            if "release_date" in unit:
                updates["release_date"] = unit.get("release_date")
            if "xml_file" in unit:
                updates["xml_file"] = unit.get("xml_file")
                
            # Apply all updates using setattr
            for key, value in updates.items():
                setattr(existing_unit, key, value)
        else:
            # Create new unit with dictionary approach
            new_unit_data = {
                "code": unit["code"],
                "title": unit["title"],
                "processed": "N"
            }
            
            if "description" in unit and unit.get("description") is not None:
                new_unit_data["description"] = unit.get("description")
            if "status" in unit and unit.get("status") is not None:
                new_unit_data["status"] = unit.get("status")
            if "release_date" in unit and unit.get("release_date") is not None:
                new_unit_data["release_date"] = unit.get("release_date")
            if "xml_file" in unit and unit.get("xml_file") is not None:
                new_unit_data["xml_file"] = unit.get("xml_file")
                
            # Create the unit with all attributes at once
            new_unit = models.Unit(**new_unit_data)
            db.add(new_unit)
    
    db.commit()
    
    # Return combined results, ensuring no duplicates
    return local_units_dict + [u for u in tga_units if not any(l["code"] == u["code"] for l in local_units_dict)]

@router.post("/{unit_code}/sync", dependencies=[Depends(JWTBearer())])
async def sync_unit(
    unit_code: str,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync a unit with TGA and process its elements"""
    # Check if user has admin permissions
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can sync units"
        )
    
    # Get unit details from TGA
    username = os.getenv("TGA_USERNAME")
    password = os.getenv("TGA_PASSWORD")
    if not username or not password:
        raise HTTPException(
            status_code=500,
            detail="TGA API credentials not configured"
        )
    
    client = TrainingGovClient(username=username, password=password)
    unit_data = client.get_component_details(unit_code)
    
    if not unit_data or not isinstance(unit_data, dict):
        raise HTTPException(
            status_code=404,
            detail=f"Unit {unit_code} not found in TGA"
        )
    
    # Store or update unit in database using ORM
    unit = db.query(models.Unit).filter(models.Unit.code == unit_code).first()
    
    if unit:
        # Update existing unit with query.update approach
        updates = {
            "title": unit_data["title"],
            "processed": "N"  # Mark for reprocessing
        }
        
        if "description" in unit_data and unit_data.get("description") is not None:
            updates["description"] = unit_data.get("description")
        if "status" in unit_data and unit_data.get("status") is not None:
            updates["status"] = unit_data.get("status")
        if "release_date" in unit_data and unit_data.get("release_date") is not None:
            updates["release_date"] = unit_data.get("release_date")
        if "xml_file" in unit_data and unit_data.get("xml_file") is not None:
            updates["xml_file"] = unit_data.get("xml_file")
        
        # Apply the updates using direct attribute assignment
        for key, value in updates.items():
            setattr(unit, key, value)
    else:
        # Create new unit with dictionary approach
        new_unit_data = {
            "code": unit_data["code"],
            "title": unit_data["title"],
            "processed": "N"
        }
        
        if "description" in unit_data and unit_data.get("description") is not None:
            new_unit_data["description"] = unit_data.get("description")
        if "status" in unit_data and unit_data.get("status") is not None:
            new_unit_data["status"] = unit_data.get("status")
        if "release_date" in unit_data and unit_data.get("release_date") is not None:
            new_unit_data["release_date"] = unit_data.get("release_date")
        if "xml_file" in unit_data and unit_data.get("xml_file") is not None:
            new_unit_data["xml_file"] = unit_data.get("xml_file")
            
        unit = models.Unit(**new_unit_data)
        db.add(unit)
    
    db.commit()
    db.refresh(unit)
    
    # Extract and store elements in background
    def process_elements(unit_id, unit_code: str):
        # Create a new session for the background task
        session = SessionLocal()
        try:
            # Get elements from TGA
            elements_data = client.get_component_xml(unit_code)
            
            if elements_data and isinstance(elements_data, dict):
                elements = elements_data.get("elements", [])
                if not elements:
                    return
                
                # Clear existing elements using ORM
                # First, delete performance criteria
                session.query(models.UnitPerformanceCriteria).filter(
                    models.UnitPerformanceCriteria.unit_id == unit_id
                ).delete()
                
                # Then delete elements
                session.query(models.UnitElement).filter(
                    models.UnitElement.unit_id == unit_id
                ).delete()
                
                session.commit()
                
                # Insert new elements
                for element_data in elements:
                    if not isinstance(element_data, dict):
                        continue
                    
                    # Create element
                    element = models.UnitElement(
                        unit_id=unit_id,
                        element_num=str(element_data.get("number", "")),
                        element_text=str(element_data.get("text", ""))
                    )
                    session.add(element)
                    session.flush()  # Flush to get the ID
                    
                    # Insert performance criteria
                    for pc_data in element_data.get("performance_criteria", []):
                        if not isinstance(pc_data, dict):
                            continue
                        
                        pc = models.UnitPerformanceCriteria(
                            element_id=element.id,
                            unit_id=unit_id,
                            pc_num=str(pc_data.get("number", "")),
                            pc_text=str(pc_data.get("text", ""))
                        )
                        session.add(pc)
                
                # Mark unit as processed
                unit = session.query(models.Unit).filter(models.Unit.id == unit_id).first()
                if unit:
                    setattr(unit, "processed", "Y")
                    
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error processing elements: {str(e)}")
        finally:
            session.close()
    
    background_tasks.add_task(process_elements, unit.id, unit_code)
    
    # Get the ID manually
    unit_id = None
    if unit:
        # Use _sa_instance_state.__dict__ to access the raw values
        try:
            unit_id = getattr(unit, "id")
        except:
            # If that doesn't work, just fetch it again
            unit_db = db.query(models.Unit).filter(models.Unit.code == unit_code).first()
            if unit_db:
                unit_id = unit_db.id
    
    return {
        "message": f"Unit {unit_code} sync started",
        "unit_id": unit_id
    }

@router.put("/{unit_id}/visibility", dependencies=[Depends(JWTBearer())])
async def set_unit_visibility(
    unit_id: int,
    visible: bool,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Set visibility of a unit (admin only)"""
    # Check if user has admin permissions
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can modify unit visibility"
        )
    
    # Get the unit
    unit = db.query(models.Unit).filter(models.Unit.id == unit_id).first()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Update visibility
    setattr(unit, "visible", visible)
    db.commit()
    
    return {"message": f"Unit {unit.code} visibility set to {visible}"}
