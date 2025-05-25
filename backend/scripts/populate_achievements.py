"""
Populate Basic Achievements Script

This script creates the basic MVP achievements in the database:
- Welcome Aboard (first login)
- Content Explorer (viewed 10 pieces of content)
- Quiz Master (completed 5 quizzes)

Follows the same pattern as populate_roles.py for consistency.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import get_db, engine
from models.tables import Achievement
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_basic_achievements(db: Session):
    """Create the basic MVP achievements if they don't exist."""
    
    basic_achievements = [
        {
            "title": "Welcome Aboard",
            "description": "Completed first login to LearnOnline.cc",
            "experience_points": 50,
            "icon_url": "/static/images/achievements/welcome.png"
        },
        {
            "title": "Content Explorer",
            "description": "Viewed 10 pieces of content",
            "experience_points": 100,
            "icon_url": "/static/images/achievements/explorer.png"
        },
        {
            "title": "Quiz Master",
            "description": "Completed 5 quizzes successfully",
            "experience_points": 150,
            "icon_url": "/static/images/achievements/quiz_master.png"
        }
    ]
    
    created_count = 0
    
    for achievement_data in basic_achievements:
        # Check if achievement already exists
        existing = db.query(Achievement).filter(
            Achievement.title == achievement_data["title"]
        ).first()
        
        if not existing:
            achievement = Achievement(**achievement_data)
            db.add(achievement)
            created_count += 1
            logger.info(f"Created achievement: {achievement_data['title']}")
        else:
            logger.info(f"Achievement already exists: {achievement_data['title']}")
    
    if created_count > 0:
        db.commit()
        logger.info(f"Successfully created {created_count} new achievements")
    else:
        logger.info("No new achievements needed to be created")
    
    return created_count

def main():
    """Main function to populate achievements."""
    try:
        # Create database tables if they don't exist
        from models.tables import Base
        Base.metadata.create_all(bind=engine)
        
        # Get database session
        db = next(get_db())
        
        logger.info("Starting achievement population...")
        created_count = create_basic_achievements(db)
        
        # Verify achievements were created
        total_achievements = db.query(Achievement).count()
        logger.info(f"Total achievements in database: {total_achievements}")
        
        # List all achievements
        achievements = db.query(Achievement).all()
        logger.info("Current achievements:")
        for achievement in achievements:
            logger.info(f"  - {achievement.title}: {achievement.description} ({achievement.experience_points} points)")
        
        db.close()
        logger.info("Achievement population completed successfully!")
        
    except Exception as e:
        logger.error(f"Error populating achievements: {str(e)}")
        raise

if __name__ == "__main__":
    main()
