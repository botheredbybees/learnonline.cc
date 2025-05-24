"""
Permissions Router - Manages system permissions for access control.

This module provides endpoints for:
- Creating, reading, updating and deleting permissions
- Managing granular access control for system features
- Supporting role-based permissions system
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Sequence
from db.database import get_db
import models.tables as models
from models.schemas import PermissionSchema
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/api/permissions",
    tags=["permissions"]
)

@router.get("/", response_model=List[PermissionSchema])
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
) -> Sequence[models.Permission]:
    """List all permissions with pagination"""
    return db.query(models.Permission).offset(skip).limit(limit).all()

@router.get("/{permission_id}", response_model=PermissionSchema)
async def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """Get a specific permission by ID"""
    permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission

@router.post("/", response_model=PermissionSchema, dependencies=[Depends(JWTBearer())])
async def create_permission(
    permission_schema: PermissionSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new permission (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create permissions")
    
    # Check if permission with same name already exists
    existing_permission = db.query(models.Permission).filter(
        models.Permission.name == permission_schema.name
    ).first()
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission with this name already exists")
    
    # Create new permission
    new_permission = models.Permission(
        name=permission_schema.name,
        description=permission_schema.description
    )
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return new_permission

@router.put("/{permission_id}", response_model=PermissionSchema, dependencies=[Depends(JWTBearer())])
async def update_permission(
    permission_id: int,
    permission_schema: PermissionSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing permission (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update permissions")
    
    # Get the permission to update
    permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Update permission fields
    updates = {}
    
    if permission_schema.name:
        # Check if another permission already has this name
        existing_permission = db.query(models.Permission).filter(
            models.Permission.name == permission_schema.name,
            models.Permission.id != permission_id
        ).first()
        if existing_permission:
            raise HTTPException(status_code=400, detail="Another permission with this name already exists")
        updates["name"] = permission_schema.name
    
    if permission_schema.description is not None:
        updates["description"] = permission_schema.description
        
    # Apply the updates using direct attribute assignment
    for key, value in updates.items():
        setattr(permission, key, value)
    
    db.commit()
    db.refresh(permission)
    return permission

@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(JWTBearer())])
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a permission (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete permissions")
    
    # Get the permission to delete
    permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check if any roles are using this permission
    role_permissions = db.query(models.RolePermission).filter(
        models.RolePermission.permission_id == permission_id
    ).count()
    
    if role_permissions > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete permission as it is assigned to {role_permissions} roles"
        )
    
    # Delete the permission
    db.delete(permission)
    db.commit()
    return None
