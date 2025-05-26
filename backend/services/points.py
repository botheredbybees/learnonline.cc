"""
Points Service - Manages the gamification points system.

This module provides functionality for:
- Calculating and awarding points for various user actions
- Managing level progression based on experience points
- Updating user profiles with new points and levels
- Triggering role upgrades based on experience thresholds

Follows the existing authentication system patterns for database operations
and error handling.
"""

from typing import Dict, Optional, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from uuid import UUID

from models.tables import User, UserProfile, Role, Achievement, UserAchievement
from auth.auth_handler import get_user_role_by_experience

logger = logging.getLogger(__name__)

# Point values for different actions (following concept document)
POINT_VALUES = {
    "content_view": 10,
    "quiz_complete": 50,
    "achievement_unlock": 100,
    "resource_contribution": 25,
    "community_feedback": 15,
    "team_achievement": 100,
    "first_login": 50,
    "unit_completion": 100,
    "assessment_pass": 75
}

# Level thresholds (following concept document)
LEVEL_THRESHOLDS = [
    (0, 1),      # Level 1: 0-100 points
    (101, 2),    # Level 2: 101-300 points  
    (301, 3),    # Level 3: 301-600 points
    (601, 4),    # Level 4: 601-1000 points
    (1001, 5)    # Level 5: 1001+ points
]

def calculate_level_from_points(experience_points: int) -> int:
    """
    Calculate user level based on experience points.
    
    Args:
        experience_points: Total experience points
        
    Returns:
        User level (1-5)
    """
    for threshold, level in reversed(LEVEL_THRESHOLDS):
        if experience_points >= threshold:
            return level
    return 1

def get_points_for_action(action: str) -> int:
    """
    Get point value for a specific action.
    
    Args:
        action: Action type (e.g., 'content_view', 'quiz_complete')
        
    Returns:
        Point value for the action
    """
    return POINT_VALUES.get(action, 0)

def award_points(
    db: Session, 
    user_id: str, 
    action: str, 
    points: Optional[int] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Award points to a user for a specific action.
    
    Args:
        db: Database session
        user_id: User UUID string
        action: Action type
        points: Custom point value (optional, uses default if not provided)
        description: Optional description of the action
        
    Returns:
        Dictionary with updated user stats and any level/role changes
        
    Raises:
        ValueError: If user not found or invalid action
    """
    try:
        # Convert string to UUID
        user_uuid = UUID(user_id)
        
        # Get user with profile
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get or create user profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_uuid).first()
        if not profile:
            profile = UserProfile(
                user_id=user_uuid,
                experience_points=0,
                level=1
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        
        # Calculate points to award
        points_to_award = points if points is not None else get_points_for_action(action)
        if points_to_award <= 0:
            logger.warning(f"No points awarded for action: {action}")
            return {
                "success": False,
                "message": f"Invalid action: {action}",
                "points_awarded": 0
            }
        
        # Store previous values
        old_points = profile.experience_points
        old_level = profile.level
        old_role = user.role.name if user.role else "guest"
        
        # Update experience points
        profile.experience_points += points_to_award
        
        # Calculate new level
        new_level = calculate_level_from_points(profile.experience_points)
        level_changed = new_level != old_level
        profile.level = new_level
        
        # Check for role upgrade based on experience
        new_role_name = get_user_role_by_experience(profile.experience_points)
        role_changed = False
        
        if new_role_name != old_role:
            new_role = db.query(Role).filter(Role.name == new_role_name).first()
            if new_role:
                user.role_id = new_role.id
                role_changed = True
        
        # Commit changes
        db.commit()
        db.refresh(profile)
        db.refresh(user)
        
        result = {
            "success": True,
            "points_awarded": points_to_award,
            "total_points": profile.experience_points,
            "previous_points": old_points,
            "level": profile.level,
            "previous_level": old_level,
            "level_changed": level_changed,
            "role": user.role.name if user.role else "guest",
            "previous_role": old_role,
            "role_changed": role_changed,
            "action": action,
            "description": description or f"Points awarded for {action}"
        }
        
        logger.info(f"Awarded {points_to_award} points to user {user_id} for {action}")
        
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error awarding points to user {user_id}: {str(e)}")
        raise

def get_user_stats(db: Session, user_id: str) -> Dict[str, Any]:
    """
    Get comprehensive user gamification statistics.
    
    Args:
        db: Database session
        user_id: User UUID string
        
    Returns:
        Dictionary with user stats including points, level, achievements, etc.
    """
    try:
        user_uuid = UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_uuid).first()
        if not profile:
            return {
                "experience_points": 0,
                "level": 1,
                "role": "guest",
                "achievements_count": 0,
                "badges_count": 0
            }
        
        # Get achievement count
        achievements_count = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_uuid
        ).count()
        
        # Get badges count (if user has badges)
        badges_count = 0
        if hasattr(user, 'badges'):
            badges_count = len(user.badges)
        
        # Calculate progress to next level
        current_level = profile.level
        next_level_threshold = None
        points_needed = 0
        
        for threshold, level in LEVEL_THRESHOLDS:
            if level > current_level:
                next_level_threshold = threshold
                break
        
        if next_level_threshold:
            current_threshold = 0
            for threshold, level in LEVEL_THRESHOLDS:
                if level == current_level:
                    current_threshold = threshold
                    break
            
            points_needed = next_level_threshold - profile.experience_points
            level_range = next_level_threshold - current_threshold
            progress_to_next = max(0, min(100, 
                ((profile.experience_points - current_threshold) / level_range) * 100
            )) if level_range > 0 else 0
        else:
            progress_to_next = 100  # Max level reached
        
        return {
            "experience_points": profile.experience_points,
            "level": profile.level,
            "role": user.role.name if user.role else "guest",
            "achievements_count": achievements_count,
            "badges_count": badges_count,
            "progress_to_next_level": round(progress_to_next, 1),
            "points_to_next_level": max(0, points_needed),
            "next_level_threshold": next_level_threshold
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats for {user_id}: {str(e)}")
        raise

def get_leaderboard(
    db: Session, 
    limit: int = 10, 
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get leaderboard of top users by experience points.
    
    Args:
        db: Database session
        limit: Number of users to return
        offset: Offset for pagination
        
    Returns:
        Dictionary with leaderboard data and pagination info
    """
    try:
        # Query top users by experience points with left join for role
        query = db.query(User, UserProfile, Role).outerjoin(
            UserProfile, User.id == UserProfile.user_id
        ).outerjoin(
            Role, User.role_id == Role.id
        ).filter(
            UserProfile.experience_points.isnot(None)
        ).order_by(
            UserProfile.experience_points.desc()
        )
        
        total_count = query.count()
        users = query.offset(offset).limit(limit).all()
        
        leaderboard = []
        for rank, (user, profile, role) in enumerate(users, start=offset + 1):
            # Handle cases where profile might be None
            experience_points = profile.experience_points if profile else 0
            level = profile.level if profile else 1
            role_name = role.name if role else "guest"
            
            leaderboard.append({
                "rank": rank,
                "user_id": str(user.id),
                "first_name": user.first_name or "Unknown",
                "last_name": user.last_name or "User",
                "experience_points": experience_points,
                "level": level,
                "role": role_name
            })
        
        return {
            "leaderboard": leaderboard,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total_count
        }
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        # Return empty leaderboard instead of raising exception
        return {
            "leaderboard": [],
            "total_count": 0,
            "limit": limit,
            "offset": offset,
            "has_more": False,
            "error": "Failed to load leaderboard data"
        }

def check_and_award_achievements(
    db: Session, 
    user_id: str, 
    action: str,
    context: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Check if user qualifies for any achievements based on action and award them.
    
    Args:
        db: Database session
        user_id: User UUID string
        action: Action that triggered the check
        context: Additional context for achievement checking
        
    Returns:
        List of newly awarded achievements
    """
    try:
        user_uuid = UUID(user_id)
        awarded_achievements = []
        
        # Get user stats first
        stats = get_user_stats(db, user_id)
        
        # Get existing user achievements to prevent duplicates
        existing_achievements = db.query(UserAchievement).join(Achievement).filter(
            UserAchievement.user_id == user_uuid
        ).all()
        existing_titles = {ua.achievement.title for ua in existing_achievements}
        
        # Define achievement criteria (basic MVP set)
        achievement_criteria = [
            {
                "title": "Welcome Aboard",
                "description": "Completed first login to LearnOnline.cc",
                "experience_points": 50,
                "condition": action == "first_login"
            },
            {
                "title": "Content Explorer", 
                "description": "Viewed 10 pieces of content",
                "experience_points": 100,
                "condition": stats["experience_points"] >= 100  # 10 content views * 10 points
            },
            {
                "title": "Quiz Master",
                "description": "Completed 5 quizzes successfully",
                "experience_points": 150,
                "condition": stats["experience_points"] >= 250  # 5 quizzes * 50 points
            }
        ]
        
        # Check each achievement
        for criteria in achievement_criteria:
            # Skip if user already has this achievement
            if criteria["title"] in existing_titles:
                continue
                
            # Check if condition is met
            if criteria["condition"]:
                # Get or create achievement
                achievement = db.query(Achievement).filter(
                    Achievement.title == criteria["title"]
                ).first()
                
                if not achievement:
                    achievement = Achievement(
                        title=criteria["title"],
                        description=criteria["description"],
                        experience_points=criteria["experience_points"]
                    )
                    db.add(achievement)
                    db.commit()
                    db.refresh(achievement)
                
                # Award achievement to user
                user_achievement = UserAchievement(
                    user_id=user_uuid,
                    achievement_id=achievement.id,
                    awarded_at=datetime.utcnow()
                )
                db.add(user_achievement)
                db.commit()
                
                awarded_achievements.append({
                    "id": achievement.id,
                    "title": achievement.title,
                    "description": achievement.description,
                    "experience_points": achievement.experience_points
                })
                
                # Award points for the achievement (but don't trigger recursive achievement checking)
                award_points(db, user_id, "achievement_unlock", achievement.experience_points)
        
        return awarded_achievements
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error checking achievements for user {user_id}: {str(e)}")
        return []
