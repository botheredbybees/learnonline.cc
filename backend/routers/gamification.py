"""
Gamification Router - Manages gamification endpoints.

This module provides endpoints for:
- Awarding points for user actions
- Getting user gamification statistics
- Managing achievements and badges
- Leaderboard functionality
- Point calculation and level progression

Follows the existing authentication router patterns for consistency
with dependency injection, error handling, and response models.
"""

from typing import Dict, Optional, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from models.tables import User, UserProfile, Achievement, UserAchievement, Badge, UserBadge
from models.schemas import UserSchema
from database import get_db
from auth.auth_handler import decode_jwt, get_user_with_role
from services.points import (
    award_points, get_user_stats, get_leaderboard, 
    check_and_award_achievements, get_points_for_action
)

# OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Get the current user from the JWT token with role and permission validation
    """
    payload = decode_jwt(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database with role information
    user = get_user_with_role(db, user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

router = APIRouter(
    prefix="/gamification",
    tags=["gamification"],
)

@router.post("/award-points", response_model=Dict[str, Any])
async def award_user_points(
    point_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Award points to the current user for a specific action.
    
    Parameters:
    - **action**: Action type (e.g., 'content_view', 'quiz_complete')
    - **points**: Custom point value (optional)
    - **description**: Optional description of the action
    
    Returns:
    - Updated user stats with points, level, and role changes
    
    Raises:
    - 400: Invalid action or point data
    - 401: Not authenticated
    """
    action = point_data.get("action")
    points = point_data.get("points")
    description = point_data.get("description")
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action is required"
        )
    
    try:
        result = award_points(db, str(current_user.id), action, points, description)
        
        # Check for new achievements
        new_achievements = check_and_award_achievements(db, str(current_user.id), action)
        result["new_achievements"] = new_achievements
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to award points"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's gamification statistics.
    
    Returns:
    - User stats including points, level, achievements, progress, etc.
    
    Raises:
    - 401: Not authenticated
    """
    try:
        stats = get_user_stats(db, str(current_user.id))
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user stats"
        )

@router.get("/leaderboard", response_model=Dict[str, Any])
async def get_points_leaderboard(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get leaderboard of top users by experience points.
    
    Parameters:
    - **limit**: Number of users to return (default: 10, max: 50)
    - **offset**: Offset for pagination (default: 0)
    
    Returns:
    - Leaderboard data with user rankings and pagination info
    
    Raises:
    - 400: Invalid pagination parameters
    """
    if limit > 50:
        limit = 50
    if limit < 1:
        limit = 10
    if offset < 0:
        offset = 0
    
    try:
        leaderboard = get_leaderboard(db, limit, offset)
        return leaderboard
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get leaderboard"
        )

@router.get("/achievements", response_model=Dict[str, Any])
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's achievements.
    
    Returns:
    - List of user's achievements with details
    
    Raises:
    - 401: Not authenticated
    """
    try:
        # Get user achievements with achievement details
        user_achievements = db.query(UserAchievement, Achievement).join(
            Achievement, UserAchievement.achievement_id == Achievement.id
        ).filter(
            UserAchievement.user_id == current_user.id
        ).order_by(
            UserAchievement.awarded_at.desc()
        ).all()
        
        achievements = []
        for user_achievement, achievement in user_achievements:
            achievements.append({
                "id": achievement.id,
                "title": achievement.title,
                "description": achievement.description,
                "icon_url": achievement.icon_url,
                "experience_points": achievement.experience_points,
                "awarded_at": user_achievement.awarded_at.isoformat()
            })
        
        return {
            "achievements": achievements,
            "total_count": len(achievements)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user achievements"
        )

@router.get("/achievements/available", response_model=Dict[str, Any])
async def get_available_achievements(
    db: Session = Depends(get_db)
):
    """
    Get all available achievements in the system.
    
    Returns:
    - List of all achievements that can be earned
    """
    try:
        achievements = db.query(Achievement).order_by(Achievement.title).all()
        
        achievement_list = []
        for achievement in achievements:
            achievement_list.append({
                "id": achievement.id,
                "title": achievement.title,
                "description": achievement.description,
                "icon_url": achievement.icon_url,
                "experience_points": achievement.experience_points
            })
        
        return {
            "achievements": achievement_list,
            "total_count": len(achievement_list)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available achievements"
        )

@router.post("/achievements/unlock", response_model=Dict[str, Any])
async def unlock_achievement(
    achievement_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually unlock an achievement for testing purposes.
    Note: In production, achievements should be unlocked automatically.
    
    Parameters:
    - **achievement_id**: ID of the achievement to unlock
    
    Returns:
    - Achievement details and success status
    
    Raises:
    - 400: Invalid achievement ID or already unlocked
    - 401: Not authenticated
    - 404: Achievement not found
    """
    achievement_id = achievement_data.get("achievement_id")
    
    if not achievement_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Achievement ID is required"
        )
    
    try:
        # Check if achievement exists
        achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
        if not achievement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement not found"
            )
        
        # Check if user already has this achievement
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == current_user.id,
            UserAchievement.achievement_id == achievement_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Achievement already unlocked"
            )
        
        # Award achievement
        user_achievement = UserAchievement(
            user_id=current_user.id,
            achievement_id=achievement_id,
            awarded_at=datetime.now()
        )
        db.add(user_achievement)
        
        # Update total achievements count
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if profile:
            profile.total_achievements_count = (profile.total_achievements_count or 0) + 1
        
        db.commit()
        
        # Award points for the achievement
        award_points(db, str(current_user.id), "achievement_unlock", achievement.experience_points)
        
        return {
            "success": True,
            "achievement": {
                "id": achievement.id,
                "title": achievement.title,
                "description": achievement.description,
                "experience_points": achievement.experience_points
            },
            "message": f"Achievement '{achievement.title}' unlocked!"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock achievement"
        )

@router.get("/point-values", response_model=Dict[str, int])
async def get_point_values():
    """
    Get point values for different actions.
    
    Returns:
    - Dictionary of action types and their point values
    """
    from services.points import POINT_VALUES
    return POINT_VALUES

@router.get("/level-thresholds", response_model=List[Dict[str, int]])
async def get_level_thresholds():
    """
    Get level thresholds and requirements.
    
    Returns:
    - List of level thresholds with point requirements
    """
    from services.points import LEVEL_THRESHOLDS
    
    thresholds = []
    for points, level in LEVEL_THRESHOLDS:
        thresholds.append({
            "level": level,
            "points_required": points
        })
    
    return thresholds

@router.post("/simulate-action", response_model=Dict[str, Any])
async def simulate_user_action(
    action_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulate a user action for testing the gamification system.
    
    Parameters:
    - **action**: Action to simulate (e.g., 'content_view', 'quiz_complete')
    - **count**: Number of times to perform the action (default: 1)
    
    Returns:
    - Results of the simulated actions including points and achievements
    
    Raises:
    - 400: Invalid action data
    - 401: Not authenticated
    """
    action = action_data.get("action")
    count = action_data.get("count", 1)
    
    if not action:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action is required"
        )
    
    if count < 1 or count > 10:  # Limit to prevent abuse
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count must be between 1 and 10"
        )
    
    try:
        results = []
        total_points_awarded = 0
        all_achievements = []
        
        for i in range(count):
            # Award points for the action
            result = award_points(db, str(current_user.id), action, description=f"Simulated {action} #{i+1}")
            total_points_awarded += result.get("points_awarded", 0)
            
            # Check for achievements
            new_achievements = check_and_award_achievements(db, str(current_user.id), action)
            all_achievements.extend(new_achievements)
            
            results.append(result)
        
        # Get final user stats
        final_stats = get_user_stats(db, str(current_user.id))
        
        return {
            "success": True,
            "action": action,
            "count": count,
            "total_points_awarded": total_points_awarded,
            "new_achievements": all_achievements,
            "final_stats": final_stats,
            "detailed_results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to simulate action: {str(e)}"
        )
