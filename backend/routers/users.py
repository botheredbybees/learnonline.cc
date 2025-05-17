from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json

from db.database import get_db
from models.user import User, UserResponse, UserUpdate, UserLevel
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
    level: Optional[str] = None,
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
    
    # Build the query based on parameters
    query = """
        SELECT id, email, username, full_name, disabled, is_admin, 
               experience_points, level, created_at, updated_at
        FROM users
    """
    
    # Add filter by level if specified
    params = {"limit": limit, "skip": skip}
    if level:
        query += " WHERE level::text = :level"
        params["level"] = level
    
    # Add ordering and pagination
    query += " ORDER BY experience_points DESC, username LIMIT :limit OFFSET :skip"
    
    # Execute query
    stmt = text(query)
    result = db.execute(stmt, params)
    users = result.fetchall()
    
    # Convert to list of UserResponse objects
    user_list = []
    for user_row in users:
        user_dict = dict(user_row)
        # Ensure proper typing of the level field
        user_dict["level"] = UserLevel(user_dict["level"])
        user_list.append(UserResponse(**user_dict))
    
    return user_list

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
        SELECT id, email, username, full_name, disabled, is_admin, 
               experience_points, level, created_at, updated_at
        FROM users
        WHERE id = :user_id
    """)
    
    result = db.execute(stmt, {"user_id": user_id})
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert to UserResponse with proper typing
    user_dict = dict(user)
    user_dict["level"] = UserLevel(user_dict["level"])
    
    return UserResponse(**user_dict)

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
            
        # Allow admins to update experience points directly
        if user_update.experience_points is not None:
            update_fields["experience_points"] = user_update.experience_points
            update_sql_parts.append("experience_points = :experience_points")
            
        # Level will be automatically updated via database trigger
    
    # Only update if there are fields to update
    if update_sql_parts:
        # Add updated_at field
        update_sql_parts.append("updated_at = CURRENT_TIMESTAMP")
        
        # Construct SQL query
        update_sql = f"""
            UPDATE users
            SET {', '.join(update_sql_parts)}
            WHERE id = :user_id
            RETURNING id, email, username, full_name, disabled, is_admin, 
                     experience_points, level, created_at, updated_at
        """
        
        # Add user_id to update fields
        update_fields["user_id"] = user_id
        
        # Execute update
        stmt = text(update_sql)
        result = db.execute(stmt, update_fields)
        db.commit()
        
        # Get updated user
        updated_user = result.fetchone()
        user_dict = dict(updated_user)
        user_dict["level"] = UserLevel(user_dict["level"])
        
        return UserResponse(**user_dict)
    
    # If no fields to update, just return the current user
    stmt = text("""
        SELECT id, email, username, full_name, disabled, is_admin,
               experience_points, level, created_at, updated_at
        FROM users
        WHERE id = :user_id
    """)
    
    result = db.execute(stmt, {"user_id": user_id})
    user = result.fetchone()
    user_dict = dict(user)
    user_dict["level"] = UserLevel(user_dict["level"])
    
    return UserResponse(**user_dict)

class ExperiencePointsAward(BaseModel):
    points: int = Field(..., gt=0, description="Number of points to award (must be positive)")
    reason: Optional[str] = Field(None, description="Reason for awarding points")

@router.post("/{user_id}/award-points", response_model=UserResponse, dependencies=[Depends(JWTBearer())])
async def award_experience_points(
    user_id: str,
    award: ExperiencePointsAward,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Award experience points to a user (admin only)"""
    # Only admins can award experience points
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to award experience points"
        )
    
    # Check if user exists
    stmt = text("""
        SELECT id FROM users WHERE id = :user_id
    """)
    result = db.execute(stmt, {"user_id": user_id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="User not found")
    
    # Award experience points - level will be updated by the database trigger
    update_sql = """
        UPDATE users
        SET experience_points = experience_points + :points,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = :user_id
        RETURNING id, email, username, full_name, disabled, is_admin, 
                 experience_points, level, created_at, updated_at
    """
    
    # Execute the update
    stmt = text(update_sql)
    result = db.execute(stmt, {"user_id": user_id, "points": award.points})
    updated_user = result.fetchone()
    
    # Convert to UserResponse with proper typing
    user_dict = dict(updated_user)
    user_dict["level"] = UserLevel(user_dict["level"])
    
    # Log the award if reason is provided
    if award.reason:
        try:
            # Check if the table exists
            check_table_sql = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_activity_logs'
                )
            """
            table_exists = db.execute(text(check_table_sql)).scalar()
            
            if table_exists:
                log_sql = """
                    INSERT INTO user_activity_logs (user_id, activity_type, points, description, created_at)
                    VALUES (:user_id, 'award_points', :points, :reason, CURRENT_TIMESTAMP)
                """
                db.execute(text(log_sql), {
                    "user_id": user_id,
                    "points": award.points,
                    "reason": award.reason
                })
        except Exception:
            # If logging fails, we still want to return the updated user
            pass
    
    db.commit()
    return UserResponse(**user_dict)

@router.get("/leaderboard", response_model=List[Dict[str, Any]], dependencies=[Depends(JWTBearer())])
async def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get user leaderboard based on experience points"""
    stmt = text("""
        SELECT id, username, full_name, experience_points, level
        FROM users
        WHERE disabled = FALSE
        ORDER BY experience_points DESC
        LIMIT :limit
    """)
    
    result = db.execute(stmt, {"limit": limit})
    leaderboard = []
    
    for i, row in enumerate(result.fetchall()):
        user_dict = dict(row)
        user_dict["rank"] = i + 1
        user_dict["level"] = user_dict["level"]  # Keep as string for simpler serialization
        leaderboard.append(user_dict)
    
    return leaderboard
