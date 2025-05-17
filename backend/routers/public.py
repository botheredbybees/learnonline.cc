from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime

from db.database import get_db
from models.favorites import (
    Quest, QuestDetail, UserQuestProgress, GuestProgress, GuestProgressCreate, TransferGuestProgress
)
from models.user import User
from auth.auth_handler import get_current_user

# Create router for public endpoints without authentication requirements
router = APIRouter(
    prefix="/public",
    tags=["public"],
    responses={404: {"description": "Not found"}},
)

# Public endpoint to get introductory quests
@router.get("/quests/introductory", response_model=List[Quest])
async def get_introductory_quests(
    db: Session = Depends(get_db)
):
    """Get all introductory quests available to guest users"""
    query = """
        SELECT id, title, description, creator_id, is_public, is_introductory,
               quest_type, source_id, experience_points, created_at, updated_at
        FROM quests
        WHERE is_introductory = TRUE
        ORDER BY created_at DESC
    """
    
    result = db.execute(text(query))
    quests = result.fetchall()
    
    return [dict(quest) for quest in quests]

# Get a specific introductory quest
@router.get("/quests/{quest_id}", response_model=QuestDetail)
async def get_introductory_quest(
    quest_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific introductory quest by ID"""
    # Get quest details
    stmt = text("""
        SELECT id, title, description, creator_id, is_public, is_introductory,
               quest_type, source_id, experience_points, created_at, updated_at
        FROM quests
        WHERE id = :quest_id AND is_introductory = TRUE
    """)
    
    result = db.execute(stmt, {"quest_id": quest_id})
    quest = result.fetchone()
    
    if not quest:
        raise HTTPException(
            status_code=404, 
            detail="Introductory quest not found or not available to guest users"
        )
    
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

# Save guest progress using cookies
@router.post("/quest-progress")
async def save_guest_progress(
    progress: GuestProgressCreate,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    """Save guest user's progress on an introductory quest using cookies"""
    # Verify this is an introductory quest
    stmt = text("""
        SELECT id FROM quests 
        WHERE id = :quest_id AND is_introductory = TRUE
    """)
    
    result = db.execute(stmt, {"quest_id": progress.quest_id})
    if not result.fetchone():
        raise HTTPException(
            status_code=404,
            detail="Quest not found or not available to guest users"
        )
    
    # Get IP and user agent if not provided
    ip_address = progress.ip_address or request.client.host
    user_agent = progress.user_agent or request.headers.get("user-agent", "")
    
    # Check if this guest_id already exists
    stmt = text("""
        SELECT guest_id FROM guest_progress
        WHERE guest_id = :guest_id
    """)
    
    result = db.execute(stmt, {"guest_id": progress.guest_id})
    existing = result.fetchone()
    
    if existing:
        # Update existing progress
        stmt = text("""
            UPDATE guest_progress
            SET unit_progress = :unit_progress,
                last_active = CURRENT_TIMESTAMP,
                ip_address = :ip_address,
                user_agent = :user_agent
            WHERE guest_id = :guest_id
        """)
        
        db.execute(stmt, {
            "guest_id": progress.guest_id,
            "unit_progress": json.dumps(progress.unit_progress),
            "ip_address": ip_address,
            "user_agent": user_agent
        })
    else:
        # Insert new progress
        stmt = text("""
            INSERT INTO guest_progress (
                guest_id, quest_id, unit_progress, ip_address, user_agent
            ) VALUES (
                :guest_id, :quest_id, :unit_progress, :ip_address, :user_agent
            )
        """)
        
        db.execute(stmt, {
            "guest_id": progress.guest_id,
            "quest_id": progress.quest_id,
            "unit_progress": json.dumps(progress.unit_progress),
            "ip_address": ip_address,
            "user_agent": user_agent
        })
    
    db.commit()
    
    # Set a cookie with the guest_id
    response.set_cookie(
        key="guest_id",
        value=progress.guest_id,
        max_age=30 * 24 * 60 * 60,  # 30 days
        path="/",
        httponly=True,
        samesite="lax"
    )
    
    return {"status": "success", "guest_id": progress.guest_id}

# Get guest progress
@router.get("/quest-progress/{guest_id}", response_model=GuestProgress)
async def get_guest_progress(
    guest_id: str,
    db: Session = Depends(get_db)
):
    """Get a guest user's progress on introductory quests"""
    stmt = text("""
        SELECT guest_id, quest_id, unit_progress, created_at, last_active, 
               ip_address, user_agent
        FROM guest_progress
        WHERE guest_id = :guest_id
    """)
    
    result = db.execute(stmt, {"guest_id": guest_id})
    progress = result.fetchone()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Guest progress not found")
    
    # Convert JSON string to dict
    progress_dict = dict(progress)
    progress_dict["unit_progress"] = json.loads(progress_dict["unit_progress"])
    
    return progress_dict

# Transfer guest progress to user account after registration
@router.post("/transfer-progress")
async def transfer_guest_progress(
    transfer: TransferGuestProgress,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer guest user's progress to their new user account"""
    # Get guest progress
    stmt = text("""
        SELECT guest_id, quest_id, unit_progress
        FROM guest_progress
        WHERE guest_id = :guest_id
    """)
    
    result = db.execute(stmt, {"guest_id": transfer.guest_id})
    progress = result.fetchone()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Guest progress not found")
    
    progress_dict = dict(progress)
    unit_progress = json.loads(progress_dict["unit_progress"])
    quest_id = progress_dict["quest_id"]
    
    # Check if user already has progress for this quest
    stmt = text("""
        SELECT user_id FROM user_quest_progress
        WHERE user_id = :user_id AND quest_id = :quest_id
    """)
    
    result = db.execute(stmt, {
        "user_id": str(current_user.id),
        "quest_id": quest_id
    })
    
    existing = result.fetchone()
    
    if existing:
        # Update existing progress
        stmt = text("""
            UPDATE user_quest_progress
            SET progress_data = :progress_data,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = :user_id AND quest_id = :quest_id
        """)
        
        db.execute(stmt, {
            "user_id": str(current_user.id),
            "quest_id": quest_id,
            "progress_data": json.dumps(unit_progress)
        })
    else:
        # Create new progress entry
        stmt = text("""
            INSERT INTO user_quest_progress (
                user_id, quest_id, progress_data
            ) VALUES (
                :user_id, :quest_id, :progress_data
            )
        """)
        
        db.execute(stmt, {
            "user_id": str(current_user.id),
            "quest_id": quest_id,
            "progress_data": json.dumps(unit_progress)
        })
    
    # Delete the guest progress
    stmt = text("""
        DELETE FROM guest_progress
        WHERE guest_id = :guest_id
    """)
    
    db.execute(stmt, {"guest_id": transfer.guest_id})
    
    # Update user level to player if they completed the introductory quest
    # Check for completion in the unit_progress (assuming a completion flag or threshold)
    is_completed = False
    if isinstance(unit_progress, dict) and unit_progress.get("completed") == True:
        is_completed = True
    
    if is_completed:
        # Get the quest's experience points
        stmt = text("""
            SELECT experience_points FROM quests
            WHERE id = :quest_id
        """)
        
        result = db.execute(stmt, {"quest_id": quest_id})
        quest = result.fetchone()
        
        if quest:
            xp = dict(quest)["experience_points"]
            
            # Update user experience points and level
            stmt = text("""
                UPDATE users
                SET experience_points = experience_points + :xp,
                    level = CASE
                        WHEN experience_points + :xp >= 1001 THEN 'mentor'::user_level
                        WHEN experience_points + :xp >= 101 THEN 'player'::user_level
                        ELSE level
                    END
                WHERE id = :user_id
                RETURNING experience_points, level
            """)
            
            result = db.execute(stmt, {
                "user_id": str(current_user.id),
                "xp": xp
            })
            
            updated = result.fetchone()
            if updated:
                updated_dict = dict(updated)
                
                # Log the activity
                stmt = text("""
                    INSERT INTO user_activity_logs (
                        user_id, activity_type, points, reason, admin_id
                    ) VALUES (
                        :user_id, 'quest_completion', :points, :reason, NULL
                    )
                """)
                
                db.execute(stmt, {
                    "user_id": str(current_user.id),
                    "points": xp,
                    "reason": f"Completed introductory quest: {quest_id}"
                })
    
    db.commit()
    
    return {
        "status": "success", 
        "message": "Guest progress successfully transferred to user account"
    }
