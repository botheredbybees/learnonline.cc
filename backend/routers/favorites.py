from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from db.database import get_db
from models.favorites import (
    FavoriteTrainingPackage, FavoriteUnit, FavoriteQuest, 
    AddFavorite, FavoritesResponse
)
from models.user import User
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/favorites",
    tags=["favorites"],
    dependencies=[Depends(JWTBearer())],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=FavoritesResponse)
async def get_user_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all favorites for the current user"""
    user_id = str(current_user.id)
    
    # Get favorite training packages
    stmt = text("""
        SELECT training_package_id, created_at
        FROM user_favorite_training_packages
        WHERE user_id = :user_id
        ORDER BY created_at DESC
    """)
    
    result = db.execute(stmt, {"user_id": user_id})
    training_packages = result.fetchall()
    
    # Get favorite units
    stmt = text("""
        SELECT unit_id, created_at
        FROM user_favorite_units
        WHERE user_id = :user_id
        ORDER BY created_at DESC
    """)
    
    result = db.execute(stmt, {"user_id": user_id})
    units = result.fetchall()
    
    # Get favorite quests
    stmt = text("""
        SELECT quest_id, created_at
        FROM user_favorite_quests
        WHERE user_id = :user_id
        ORDER BY created_at DESC
    """)
    
    result = db.execute(stmt, {"user_id": user_id})
    quests = result.fetchall()
    
    return {
        "training_packages": [dict(tp) for tp in training_packages],
        "units": [dict(unit) for unit in units],
        "quests": [dict(quest) for quest in quests]
    }


@router.post("/training-packages")
async def add_favorite_training_package(
    favorite: AddFavorite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a training package to favorites"""
    user_id = str(current_user.id)
    
    # Check user level - Only player+ users can add favorites
    if current_user.level == 'guest':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only player level or higher can add favorites. Complete an introductory quest to level up."
        )
    
    # Check if training package exists
    stmt = text("""
        SELECT id FROM training_packages WHERE id = :id
    """)
    
    result = db.execute(stmt, {"id": favorite.id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Training package not found")
    
    # Check if already in favorites
    stmt = text("""
        SELECT 1 FROM user_favorite_training_packages
        WHERE user_id = :user_id AND training_package_id = :training_package_id
    """)
    
    result = db.execute(stmt, {
        "user_id": user_id,
        "training_package_id": favorite.id
    })
    
    if result.fetchone():
        return {"detail": "Training package already in favorites"}
    
    # Add to favorites
    stmt = text("""
        INSERT INTO user_favorite_training_packages (user_id, training_package_id)
        VALUES (:user_id, :training_package_id)
    """)
    
    db.execute(stmt, {
        "user_id": user_id,
        "training_package_id": favorite.id
    })
    
    db.commit()
    return {"detail": "Training package added to favorites"}


@router.delete("/training-packages/{training_package_id}")
async def remove_favorite_training_package(
    training_package_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a training package from favorites"""
    user_id = str(current_user.id)
    
    stmt = text("""
        DELETE FROM user_favorite_training_packages
        WHERE user_id = :user_id AND training_package_id = :training_package_id
    """)
    
    db.execute(stmt, {
        "user_id": user_id,
        "training_package_id": training_package_id
    })
    
    db.commit()
    return {"detail": "Training package removed from favorites"}


@router.post("/units")
async def add_favorite_unit(
    favorite: AddFavorite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a unit to favorites"""
    user_id = str(current_user.id)
    
    # Check user level - Only player+ users can add favorites
    if current_user.level == 'guest':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only player level or higher can add favorites. Complete an introductory quest to level up."
        )
    
    # Check if unit exists
    stmt = text("""
        SELECT id FROM units WHERE id = :id
    """)
    
    result = db.execute(stmt, {"id": favorite.id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Unit not found")
    
    # Check if already in favorites
    stmt = text("""
        SELECT 1 FROM user_favorite_units
        WHERE user_id = :user_id AND unit_id = :unit_id
    """)
    
    result = db.execute(stmt, {
        "user_id": user_id,
        "unit_id": favorite.id
    })
    
    if result.fetchone():
        return {"detail": "Unit already in favorites"}
    
    # Add to favorites
    stmt = text("""
        INSERT INTO user_favorite_units (user_id, unit_id)
        VALUES (:user_id, :unit_id)
    """)
    
    db.execute(stmt, {
        "user_id": user_id,
        "unit_id": favorite.id
    })
    
    db.commit()
    return {"detail": "Unit added to favorites"}


@router.delete("/units/{unit_id}")
async def remove_favorite_unit(
    unit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a unit from favorites"""
    user_id = str(current_user.id)
    
    stmt = text("""
        DELETE FROM user_favorite_units
        WHERE user_id = :user_id AND unit_id = :unit_id
    """)
    
    db.execute(stmt, {
        "user_id": user_id,
        "unit_id": unit_id
    })
    
    db.commit()
    return {"detail": "Unit removed from favorites"}


@router.post("/quests")
async def add_favorite_quest(
    favorite: AddFavorite,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a quest to favorites"""
    user_id = str(current_user.id)
    
    # Check user level - Only player+ users can add favorites
    if current_user.level == 'guest':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only player level or higher can add favorites. Complete an introductory quest to level up."
        )
    
    # Check if quest exists
    stmt = text("""
        SELECT id FROM quests WHERE id = :id
    """)
    
    result = db.execute(stmt, {"id": favorite.id})
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Check if already in favorites
    stmt = text("""
        SELECT 1 FROM user_favorite_quests
        WHERE user_id = :user_id AND quest_id = :quest_id
    """)
    
    result = db.execute(stmt, {
        "user_id": user_id,
        "quest_id": favorite.id
    })
    
    if result.fetchone():
        return {"detail": "Quest already in favorites"}
    
    # Add to favorites
    stmt = text("""
        INSERT INTO user_favorite_quests (user_id, quest_id)
        VALUES (:user_id, :quest_id)
    """)
    
    db.execute(stmt, {
        "user_id": user_id,
        "quest_id": favorite.id
    })
    
    db.commit()
    return {"detail": "Quest added to favorites"}


@router.delete("/quests/{quest_id}")
async def remove_favorite_quest(
    quest_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a quest from favorites"""
    user_id = str(current_user.id)
    
    stmt = text("""
        DELETE FROM user_favorite_quests
        WHERE user_id = :user_id AND quest_id = :quest_id
    """)
    
    db.execute(stmt, {
        "user_id": user_id,
        "quest_id": quest_id
    })
    
    db.commit()
    return {"detail": "Quest removed from favorites"}
