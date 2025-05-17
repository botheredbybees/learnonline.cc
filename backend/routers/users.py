from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from db.database import get_db
from models.user import User, UserResponse, UserUpdate
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/me", response_model=UserResponse)
async def read_user_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("", response_model=List[UserResponse], dependencies=[Depends(JWTBearer())])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access user list"
        )
    
    # Get users
    stmt = text("""
        SELECT id, email, username, full_name, disabled, is_admin, created_at, updated_at
        FROM users
        ORDER BY username
        LIMIT :limit OFFSET :skip
    """)
    
    result = db.execute(stmt, {"limit": limit, "skip": skip})
    users = result.fetchall()
    
    # Convert to list of UserResponse
    return [UserResponse(**dict(user)) for user in users]

@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(JWTBearer())])
async def read_user(
    user_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID (admin or self only)"""
    # Allow access only to admins or the user themselves
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )
    
    # Get user
    stmt = text("""
        SELECT id, email, username, full_name, disabled, is_admin, created_at, updated_at
        FROM users
        WHERE id = :user_id
    """)
    
    result = db.execute(stmt, {"user_id": user_id})
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**dict(user))

@router.put("/{user_id}", response_model=UserResponse, dependencies=[Depends(JWTBearer())])
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user (admin or self only)"""
    # Allow access only to admins or the user themselves
    if not current_user.is_admin and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    # Check if user exists
    stmt = text("""
        SELECT id FROM users WHERE id = :user_id
    """)
    result = db.execute(stmt, {"user_id": user_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prepare update fields
    update_fields = {}
    update_sql_parts = []
    
    if user_update.email is not None:
        update_fields["email"] = user_update.email
        update_sql_parts.append("email = :email")
    
    if user_update.username is not None:
        update_fields["username"] = user_update.username
        update_sql_parts.append("username = :username")
    
    if user_update.full_name is not None:
        update_fields["full_name"] = user_update.full_name
        update_sql_parts.append("full_name = :full_name")
    
    # Only admins can change disabled and admin status
    if current_user.is_admin:
        if user_update.disabled is not None:
            update_fields["disabled"] = user_update.disabled
            update_sql_parts.append("disabled = :disabled")
        
        if user_update.is_admin is not None:
            update_fields["is_admin"] = user_update.is_admin
            update_sql_parts.append("is_admin = :is_admin")
    
    # Only update if there are fields to update
    if update_sql_parts:
        # Add updated_at field
        update_sql_parts.append("updated_at = CURRENT_TIMESTAMP")
        
        # Construct SQL query
        update_sql = f"""
            UPDATE users
            SET {', '.join(update_sql_parts)}
            WHERE id = :user_id
            RETURNING id, email, username, full_name, disabled, is_admin, created_at, updated_at
        """
        
        # Add user_id to update fields
        update_fields["user_id"] = user_id
        
        # Execute update
        stmt = text(update_sql)
        result = db.execute(stmt, update_fields)
        db.commit()
        
        # Get updated user
        updated_user = result.fetchone()
        return UserResponse(**dict(updated_user))
    
    # If no fields to update, just return the current user
    stmt = text("""
        SELECT id, email, username, full_name, disabled, is_admin, created_at, updated_at
        FROM users
        WHERE id = :user_id
    """)
    
    result = db.execute(stmt, {"user_id": user_id})
    user = result.fetchone()
    
    return UserResponse(**dict(user))
