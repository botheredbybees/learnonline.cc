from fastapi import APIRouter, Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Any, Dict
import uuid
import json
from datetime import datetime

from db.database import get_db
from models.favorites import (
    Quest, QuestDetail, QuestCreate, QuestUpdate,
    FavoriteTrainingPackage, FavoriteUnit, FavoriteQuest, 
    AddFavorite, FavoritesResponse, GuestProgressCreate, GuestProgress,
    UserQuestProgress, TransferGuestProgress
)
from models.user import User
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user, decode_jwt

# Optional authentication for public endpoints
async def get_current_user_or_none(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None."""
    # Get the Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
        
    try:
        # Extract the token
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
            
        # Try to decode the token
        payload = decode_jwt(token)
        user_id = payload.get("user_id", "")
        
        if not user_id:
            return None
            
        # Get user from database
        stmt = text("""
            SELECT id, email, username, full_name, disabled, is_admin, 
                   experience_points, level, created_at, updated_at
            FROM users
            WHERE id = :user_id
        """)
        
        result = db.execute(stmt, {"user_id": user_id})
        user = result.fetchone()
        
        if not user:
            return None
            
        return User(**dict(user))
    except Exception:
        return None

router = APIRouter(
    prefix="/quests",
    tags=["quests"],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=List[Quest])
async def get_quests(
    skip: int = 0, 
    limit: int = 100,
    creator_id: Optional[str] = None,
    quest_type: Optional[str] = None,
    is_public: bool = None,
    is_introductory: bool = None,
    current_user: User = Depends(get_current_user_or_none),  # Allow anonymous access
    db: Session = Depends(get_db)
):
    """Get all quests with optional filters"""
    query = """
        SELECT id, title, description, creator_id, is_public, is_introductory,
               quest_type, source_id, experience_points, created_at, updated_at
        FROM quests
        WHERE 1=1
    """
    params = {"skip": skip, "limit": limit}
    
    # If not logged in or not admin, only show public or introductory quests
    if current_user is None:
        query += " AND (is_introductory = TRUE)"
    elif not current_user.is_admin and str(current_user.id) != creator_id:
        # Non-admin users can see:
        # 1. Public quests
        # 2. Introductory quests
        # 3. Their own created quests (handled by creator_id filter)
        # 4. If they're Player+ level, they can see all public quests
        if current_user.level == 'guest':
            query += " AND (is_introductory = TRUE OR is_public = TRUE)"
        else:
            query += " AND (is_public = TRUE OR creator_id = :user_id)"
            params["user_id"] = str(current_user.id)
    
    if creator_id:
        query += " AND creator_id = :creator_id"
        params["creator_id"] = creator_id
    
    if quest_type:
        query += " AND quest_type = :quest_type"
        params["quest_type"] = quest_type
    
    if is_public is not None:
        query += " AND is_public = :is_public"
        params["is_public"] = is_public
        
    if is_introductory is not None:
        query += " AND is_introductory = :is_introductory"
        params["is_introductory"] = is_introductory
    
    query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
    
    result = db.execute(text(query), params)
    quests = result.fetchall()
    
    return [dict(quest) for quest in quests]


@router.get("/{quest_id}", response_model=QuestDetail)
async def get_quest(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific quest by ID with its units"""
    # Get quest details
    stmt = text("""
        SELECT id, title, description, creator_id, is_public, 
               quest_type, source_id, experience_points, created_at, updated_at
        FROM quests
        WHERE id = :quest_id
    """)
    
    result = db.execute(stmt, {"quest_id": quest_id})
    quest = result.fetchone()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Get quest units
    stmt = text("""
        SELECT unit_id, sequence_number, is_required
        FROM quest_units
        WHERE quest_id = :quest_id
        ORDER BY sequence_number
    """)
    
    result = db.execute(stmt, {"quest_id": quest_id})
    units = result.fetchall()
    
    # Combine quest and units
    quest_dict = dict(quest)
    quest_dict["units"] = [dict(unit) for unit in units]
    
    return quest_dict


@router.post("", response_model=Quest, dependencies=[Depends(JWTBearer())])
async def create_quest(
    quest_create: QuestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new quest (mentor level or admin only)"""
    # Check if user can create quests (admin or mentor level)
    if not current_user.is_admin and current_user.level != 'mentor':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users or mentors can create quests"
        )
    
    # Generate a UUID for the new quest
    quest_id = str(uuid.uuid4())
    
    # Insert quest into database
    stmt = text("""
        INSERT INTO quests (
            id, title, description, creator_id, is_public,
            quest_type, source_id, experience_points
        ) VALUES (
            :id, :title, :description, :creator_id, :is_public,
            :quest_type, :source_id, :experience_points
        )
        RETURNING id, title, description, creator_id, is_public, 
                 quest_type, source_id, experience_points, created_at, updated_at
    """)
    
    params = {
        "id": quest_id,
        "title": quest_create.title,
        "description": quest_create.description,
        "creator_id": str(current_user.id),
        "is_public": quest_create.is_public,
        "quest_type": quest_create.quest_type,
        "source_id": quest_create.source_id,
        "experience_points": quest_create.experience_points
    }
    
    result = db.execute(stmt, params)
    quest = result.fetchone()
    
    # Add units to quest
    for i, unit_id in enumerate(quest_create.unit_ids):
        stmt = text("""
            INSERT INTO quest_units (quest_id, unit_id, sequence_number)
            VALUES (:quest_id, :unit_id, :sequence_number)
        """)
        
        db.execute(stmt, {
            "quest_id": quest_id,
            "unit_id": unit_id,
            "sequence_number": i + 1
        })
    
    db.commit()
    return dict(quest)


@router.put("/{quest_id}", response_model=Quest, dependencies=[Depends(JWTBearer())])
async def update_quest(
    quest_id: str,
    quest_update: QuestUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a quest (creator or admin only)"""
    # Check if quest exists and user has permission
    stmt = text("""
        SELECT creator_id FROM quests WHERE id = :quest_id
    """)
    
    result = db.execute(stmt, {"quest_id": quest_id})
    quest = result.fetchone()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Check permissions (admin or creator)
    if not current_user.is_admin and str(current_user.id) != quest.creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this quest"
        )
    
    # Prepare update fields
    update_fields = {}
    update_sql_parts = []
    
    if quest_update.title is not None:
        update_fields["title"] = quest_update.title
        update_sql_parts.append("title = :title")
    
    if quest_update.description is not None:
        update_fields["description"] = quest_update.description
        update_sql_parts.append("description = :description")
    
    if quest_update.is_public is not None:
        update_fields["is_public"] = quest_update.is_public
        update_sql_parts.append("is_public = :is_public")
    
    if quest_update.experience_points is not None:
        update_fields["experience_points"] = quest_update.experience_points
        update_sql_parts.append("experience_points = :experience_points")
    
    # Only update if there are fields to update
    if update_sql_parts:
        # Add updated_at field
        update_sql_parts.append("updated_at = CURRENT_TIMESTAMP")
        
        # Construct SQL query
        update_sql = f"""
            UPDATE quests
            SET {', '.join(update_sql_parts)}
            WHERE id = :quest_id
            RETURNING id, title, description, creator_id, is_public, 
                     quest_type, source_id, experience_points, created_at, updated_at
        """
        
        # Add quest_id to update fields
        update_fields["quest_id"] = quest_id
        
        # Execute update
        stmt = text(update_sql)
        result = db.execute(stmt, update_fields)
        updated_quest = result.fetchone()
    
    # Update units if provided
    if quest_update.unit_ids is not None:
        # Delete existing units
        stmt = text("""
            DELETE FROM quest_units
            WHERE quest_id = :quest_id
        """)
        
        db.execute(stmt, {"quest_id": quest_id})
        
        # Add new units
        for i, unit_id in enumerate(quest_update.unit_ids):
            stmt = text("""
                INSERT INTO quest_units (quest_id, unit_id, sequence_number)
                VALUES (:quest_id, :unit_id, :sequence_number)
            """)
            
            db.execute(stmt, {
                "quest_id": quest_id,
                "unit_id": unit_id,
                "sequence_number": i + 1
            })
    
    db.commit()
    
    # Get updated quest
    stmt = text("""
        SELECT id, title, description, creator_id, is_public, 
               quest_type, source_id, experience_points, created_at, updated_at
        FROM quests
        WHERE id = :quest_id
    """)
    
    result = db.execute(stmt, {"quest_id": quest_id})
    quest = result.fetchone()
    
    return dict(quest)


@router.delete("/{quest_id}", dependencies=[Depends(JWTBearer())])
async def delete_quest(
    quest_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a quest (creator or admin only)"""
    # Check if quest exists and user has permission
    stmt = text("""
        SELECT creator_id FROM quests WHERE id = :quest_id
    """)
    
    result = db.execute(stmt, {"quest_id": quest_id})
    quest = result.fetchone()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Check permissions (admin or creator)
    if not current_user.is_admin and str(current_user.id) != quest.creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this quest"
        )
    
    # Delete quest (cascade will delete quest_units)
    stmt = text("""
        DELETE FROM quests
        WHERE id = :quest_id
    """)
    
    db.execute(stmt, {"quest_id": quest_id})
    db.commit()
    
    return {"detail": "Quest deleted successfully"}
