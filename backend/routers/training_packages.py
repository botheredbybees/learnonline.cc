"""
Training Packages Router - Manages training packages from the Australian training system.

This module provides endpoints for:
- Retrieving and searching training packages
- Syncing training packages with TGA (Training.gov.au)
- Managing visibility and metadata for training packages
- Supporting the training qualification structure
<<<<<<< HEAD
=======
- Bulk download and import functionality for admin users
>>>>>>> origin/main
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Sequence, Dict, Any
from db.database import get_db
import models.tables as models
from models.schemas import TrainingPackageSchema
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user
import os
<<<<<<< HEAD
from services.tga.client import TrainingGovClient
=======
import uuid
import json
from datetime import datetime
from services.tga.client import TrainingGovClient
from services.download_manager import download_manager
>>>>>>> origin/main

router = APIRouter(
    prefix="/api/training-packages",
    tags=["training packages"]
)

@router.get("/", response_model=List[TrainingPackageSchema])
async def list_training_packages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    status: Optional[str] = Query(None),
    visible: bool = Query(True),
    db: Session = Depends(get_db)
) -> Sequence[models.TrainingPackage]:
    """List all training packages with optional filtering"""
    query = db.query(models.TrainingPackage).filter(models.TrainingPackage.visible == visible)
    
    if status:
        query = query.filter(models.TrainingPackage.status == status)
    
    return query.order_by(models.TrainingPackage.code).offset(skip).limit(limit).all()

<<<<<<< HEAD
=======
@router.get("/available", dependencies=[Depends(JWTBearer())])
async def get_available_training_packages(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, le=200),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available training packages from TGA (admin only)"""
    # Check if user has admin permissions
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can access available training packages"
        )
    
    # Get TGA credentials
    username = os.getenv("TGA_USERNAME")
    password = os.getenv("TGA_PASSWORD")
    if not username or not password:
        raise HTTPException(
            status_code=500,
            detail="TGA API credentials not configured"
        )
    
    try:
        client = TrainingGovClient(username=username, password=password)
        
        # Search for all training packages
        component_types = {
            'IncludeAccreditedCourse': False,
            'IncludeAccreditedCourseModule': False,
            'IncludeQualification': False,
            'IncludeSkillSet': False,
            'IncludeTrainingPackage': True,
            'IncludeUnit': False,
            'IncludeUnitContextualisation': False
        }
        
        result = client.search_components(
            filter_text="",  # Empty filter to get all
            component_types=component_types,
            page=page,
            page_size=page_size
        )
        
        tga_packages = result.get('components', [])
        
        # Check which packages are already in our database
        for package in tga_packages:
            existing_package = db.query(models.TrainingPackage).filter(
                models.TrainingPackage.code == package["code"]
            ).first()
            package["in_database"] = existing_package is not None
            package["processed"] = existing_package.processed if existing_package else "N"
        
        return {
            "packages": tga_packages,
            "page": page,
            "page_size": page_size,
            "total": len(tga_packages)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve available training packages: {str(e)}"
        )

@router.post("/bulk-download", dependencies=[Depends(JWTBearer())])
async def bulk_download_training_packages(
    package_codes: List[str],
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Queue multiple training packages for bulk download (admin only)"""
    # Check if user has admin permissions
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can perform bulk downloads"
        )
    
    if not package_codes:
        raise HTTPException(
            status_code=400,
            detail="No training package codes provided"
        )
    
    # Create download job using download manager
    job_id = download_manager.create_job("training_packages", package_codes, current_user.id)
    
    # Start background processing
    background_tasks.add_task(
        download_manager.process_training_package_download, 
        job_id, 
        package_codes, 
        current_user.id
    )
    
    return {
        "job_id": job_id,
        "message": f"Bulk download started for {len(package_codes)} training packages",
        "status": "queued"
    }

@router.get("/download-status/{job_id}", dependencies=[Depends(JWTBearer())])
async def get_download_status(
    job_id: str,
    current_user: models.User = Depends(get_current_user)
):
    """Get the status of a bulk download job (admin only)"""
    # Check if user has admin permissions
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can check download status"
        )
    
    job_status = download_manager.get_job_status(job_id)
    if not job_status:
        raise HTTPException(
            status_code=404,
            detail="Download job not found"
        )
    
    return job_status

>>>>>>> origin/main
@router.get("/{training_package_id}", response_model=TrainingPackageSchema)
async def get_training_package(
    training_package_id: int, 
    db: Session = Depends(get_db)
):
    """Get a specific training package by ID"""
    package = db.query(models.TrainingPackage).filter(models.TrainingPackage.id == training_package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Training package not found")
    return package

@router.get("/code/{code}", response_model=TrainingPackageSchema)
async def get_training_package_by_code(
    code: str,
    db: Session = Depends(get_db)
):
    """Get a specific training package by code"""
    package = db.query(models.TrainingPackage).filter(models.TrainingPackage.code == code).first()
    if not package:
        raise HTTPException(status_code=404, detail="Training package not found")
    return package

@router.post("/search")
async def search_training_packages(
    query: str,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Search training packages in local database and TGA API"""
    # Search local database
    db_query = db.query(models.TrainingPackage).filter(
        # Using ilike for case-insensitive search on multiple fields
        (
            models.TrainingPackage.title.ilike(f"%{query}%") |
            models.TrainingPackage.description.ilike(f"%{query}%") |
            models.TrainingPackage.code.ilike(f"%{query}%")
        ),
        models.TrainingPackage.visible == True
    )
    
    # Apply pagination and order
    db_query = db_query.order_by(models.TrainingPackage.code)
    db_query = db_query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    local_packages = db_query.all()
    
    # Convert to dict representation
    local_packages_dict = [
        {
            "id": package.id,
            "code": package.code,
            "title": package.title,
            "description": package.description,
            "status": package.status,
            "release_date": package.release_date
        } for package in local_packages
    ]
    
    # If we have enough results, return them
    if len(local_packages_dict) >= page_size:
        return local_packages_dict
    
    # Otherwise, search TGA API
    username = os.getenv("TGA_USERNAME")
    password = os.getenv("TGA_PASSWORD")
    if not username or not password:
        raise HTTPException(
            status_code=500,
            detail="TGA API credentials not configured"
        )
    
    client = TrainingGovClient(username=username, password=password)
    # Use search_components with component types set to only include training packages
    component_types = {
        'IncludeAccreditedCourse': False,
        'IncludeAccreditedCourseModule': False,
        'IncludeQualification': False,
        'IncludeSkillSet': False,
        'IncludeTrainingPackage': True,
        'IncludeUnit': False,
        'IncludeUnitContextualisation': False
    }
    
    result = client.search_components(
        filter_text=query,
        component_types=component_types,
        page=page,
        page_size=page_size
    )
    tga_packages = result.get('components', [])
    
    # For any new packages from TGA, store them in our database
    for package in tga_packages:
        # Check if package already exists
        existing_package = db.query(models.TrainingPackage).filter(
            models.TrainingPackage.code == package["code"]
        ).first()
        
        if existing_package:
            # Update existing package with clean dict approach
            updates = {"processed": "N"}
            if "title" in package and package.get("title") is not None:
                updates["title"] = package["title"]
            if "description" in package and package.get("description") is not None:
                updates["description"] = package.get("description")
            if "status" in package and package.get("status") is not None:
                updates["status"] = package.get("status")
            if "release_date" in package and package.get("release_date") is not None:
                updates["release_date"] = package.get("release_date")
            if "xml_file" in package and package.get("xml_file") is not None:
                updates["xml_file"] = package.get("xml_file")
                
            # Update using direct attribute assignment
            for key, value in updates.items():
                setattr(existing_package, key, value)
        else:
            # Create new package using dictionary and ** operator
            new_package_data = {
                "code": package["code"],
                "title": package["title"],
                "processed": "N"
            }
            
            if "description" in package and package.get("description") is not None:
                new_package_data["description"] = package.get("description")
            if "status" in package and package.get("status") is not None:
                new_package_data["status"] = package.get("status")
            if "release_date" in package and package.get("release_date") is not None:
                new_package_data["release_date"] = package.get("release_date")
            if "xml_file" in package and package.get("xml_file") is not None:
                new_package_data["xml_file"] = package.get("xml_file")
            
            new_package = models.TrainingPackage(**new_package_data)
            db.add(new_package)
    
    db.commit()
    
    # Return combined results, ensuring no duplicates
    return local_packages_dict + [
        p for p in tga_packages if not any(l["code"] == p["code"] for l in local_packages_dict)
    ]

@router.post("/{package_code}/sync", dependencies=[Depends(JWTBearer())])
async def sync_training_package(
    package_code: str,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync a training package with TGA (admin only)"""
    # Check if user has admin permissions
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can sync training packages"
        )
    
    # Get package details from TGA
    username = os.getenv("TGA_USERNAME")
    password = os.getenv("TGA_PASSWORD")
    if not username or not password:
        raise HTTPException(
            status_code=500,
            detail="TGA API credentials not configured"
        )
    
    client = TrainingGovClient(username=username, password=password)
    package_data = client.get_component_details(package_code)
    
    if not package_data or not isinstance(package_data, dict):
        raise HTTPException(
            status_code=404,
            detail=f"Training package {package_code} not found in TGA"
        )
    
    # Store or update package in database
    package = db.query(models.TrainingPackage).filter(
        models.TrainingPackage.code == package_code
    ).first()
    
    if package:
        # Update existing package - create a clean dict of valid updates
        updates = {}
        if "title" in package_data and package_data.get("title") is not None:
            updates["title"] = package_data["title"]
        if "description" in package_data and package_data.get("description") is not None:
            updates["description"] = package_data.get("description")
        if "status" in package_data and package_data.get("status") is not None:
            updates["status"] = package_data.get("status")
        if "release_date" in package_data and package_data.get("release_date") is not None:
            updates["release_date"] = package_data.get("release_date")
        if "xml_file" in package_data and package_data.get("xml_file") is not None:
            updates["xml_file"] = package_data.get("xml_file")
        
        updates["processed"] = "N"  # Mark for reprocessing
        
        # Update using direct attribute assignment
        for key, value in updates.items():
            setattr(package, key, value)
    else:
        # Create new package with a clean dict approach
        new_package_data = {
            "code": package_data["code"],
            "title": package_data["title"],
            "processed": "N"
        }
        
        if "description" in package_data and package_data.get("description") is not None:
            new_package_data["description"] = package_data.get("description")
        if "status" in package_data and package_data.get("status") is not None:
            new_package_data["status"] = package_data.get("status")
        if "release_date" in package_data and package_data.get("release_date") is not None:
            new_package_data["release_date"] = package_data.get("release_date")
        if "xml_file" in package_data and package_data.get("xml_file") is not None:
            new_package_data["xml_file"] = package_data.get("xml_file")
            
        package = models.TrainingPackage(**new_package_data)
        db.add(package)
    
    db.commit()
    db.refresh(package)
    
    # Build background task to sync units, qualifications, and skillsets
    def process_package_components(package_id):
        # Implemented in a separate task to avoid this endpoint from timing out
        pass
    
    # Add background task
    background_tasks.add_task(process_package_components, package.id)
    
    # Get package_id safely
    package_id = None
    try:
        package_id = package.id
    except:
        # If direct access doesn't work, query again
        refreshed_package = db.query(models.TrainingPackage).filter(
            models.TrainingPackage.code == package_code
        ).first()
        if refreshed_package:
            package_id = refreshed_package.id
    
    return {
        "message": f"Training package {package_code} sync started",
        "package_id": package_id
    }

@router.put("/{training_package_id}/visibility", dependencies=[Depends(JWTBearer())])
async def set_training_package_visibility(
    training_package_id: int,
    visible: bool,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Set visibility of a training package (admin only)"""
    # Check if user has admin permissions
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Only admin users can modify training package visibility"
        )
    
    # Get the package
    package = db.query(models.TrainingPackage).filter(
        models.TrainingPackage.id == training_package_id
    ).first()
    
    if not package:
        raise HTTPException(
            status_code=404,
            detail="Training package not found"
        )
    
    # Update visibility using direct attribute assignment
    setattr(package, "visible", visible)
    db.commit()
    
    return {
        "message": f"Training package {package.code} visibility set to {visible}"
    }
