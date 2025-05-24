"""
Roles Router - Manages user roles and their associated permissions.

This module provides endpoints for:
- Creating, reading, updating and deleting roles
- Managing role-permission associations
- Retrieving permissions for specific roles
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Sequence
from db.database import get_db
import models.tables as models
from models.schemas import RoleSchema, RolePermissionSchema
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/api/roles",
    tags=["roles"]
)

@router.get("/", response_model=List[RoleSchema])
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
) -> Sequence[models.Role]:
    """List all roles with pagination"""
    return db.query(models.Role).offset(skip).limit(limit).all()

@router.get("/{role_id}", response_model=RoleSchema)
async def get_role(role_id: int, db: Session = Depends(get_db)):
    """Get a specific role by ID"""
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("/", response_model=RoleSchema, dependencies=[Depends(JWTBearer())])
async def create_role(
    role_schema: RoleSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new role (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create roles")
    
    # Check if role with same name already exists
    existing_role = db.query(models.Role).filter(models.Role.name == role_schema.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    # Create new role
    new_role = models.Role(
        name=role_schema.name,
        description=role_schema.description
    )
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@router.put("/{role_id}", response_model=RoleSchema, dependencies=[Depends(JWTBearer())])
async def update_role(
    role_id: int,
    role_schema: RoleSchema,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update an existing role (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update roles")
    
    # Get the role to update
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Update role fields
    updates = {}
    
    if role_schema.name:
        # Check if another role already has this name
        existing_role = db.query(models.Role).filter(
            models.Role.name == role_schema.name,
            models.Role.id != role_id
        ).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Another role with this name already exists")
        updates["name"] = role_schema.name
    
    if role_schema.description is not None:
        updates["description"] = role_schema.description
        
    # Apply the updates using direct attribute assignment
    for key, value in updates.items():
        setattr(role, key, value)
    
    db.commit()
    db.refresh(role)
    return role

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(JWTBearer())])
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Delete a role (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete roles")
    
    # Get the role to delete
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if any users are using this role
    users_with_role = db.query(models.User).filter(models.User.role_id == role_id).count()
    if users_with_role > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role as it is assigned to {users_with_role} users"
        )
    
    # Delete role permissions first
    db.query(models.RolePermission).filter(models.RolePermission.role_id == role_id).delete()
    
    # Delete the role
    db.delete(role)
    db.commit()
    return None

@router.get("/{role_id}/permissions", response_model=List[RolePermissionSchema])
async def get_role_permissions(role_id: int, db: Session = Depends(get_db)):
    """Get all permissions for a specific role"""
    # Check if role exists
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Get role permissions
    permissions = db.query(models.RolePermission).filter(
        models.RolePermission.role_id == role_id
    ).all()
    
    return permissions

@router.post("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Add a permission to a role (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to assign permissions")
    
    # Check if role exists
    role = db.query(models.Role).filter(models.Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check if permission exists
    permission = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check if permission is already assigned to role
    existing = db.query(models.RolePermission).filter(
        models.RolePermission.role_id == role_id,
        models.RolePermission.permission_id == permission_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Permission is already assigned to this role")
    
    # Assign permission to role
    role_permission = models.RolePermission(
        role_id=role_id,
        permission_id=permission_id
    )
    db.add(role_permission)
    db.commit()
    
    return {"message": f"Permission '{permission.name}' assigned to role '{role.name}'"}

@router.delete("/{role_id}/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(JWTBearer())])
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Remove a permission from a role (admin only)"""
    # Check if user has admin role
    if not hasattr(current_user, "role") or current_user.role.name != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to remove permissions")
    
    # Check if role permission exists
    role_permission = db.query(models.RolePermission).filter(
        models.RolePermission.role_id == role_id,
        models.RolePermission.permission_id == permission_id
    ).first()
    
    if not role_permission:
        raise HTTPException(status_code=404, detail="Permission is not assigned to this role")
    
    # Remove permission from role
    db.delete(role_permission)
    db.commit()
    
    return None
