#!/usr/bin/env python3
"""
Create demo accounts for LearnOnline.cc authentication testing
"""

import asyncio
import sys
from pathlib import Path
import uuid

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from database import get_db, engine
from models.tables import User, Role, UserProfile, Base
from auth.auth_handler import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_demo_accounts():
    """Create demo accounts for testing"""
    print("🚀 Creating demo accounts for LearnOnline.cc")
    
    # Create database tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # First, ensure roles exist
        print("📝 Setting up roles...")
        
        # Check if roles exist
        existing_roles = db.query(Role).all()
        
        if not existing_roles:
            # Insert default roles
            roles_data = [
                Role(name="admin", description="Administrator with full system access"),
                Role(name="mentor", description="Mentor with content creation privileges (1001+ points)"),
                Role(name="player", description="Player with content access (101-1000 points)"),
                Role(name="guest", description="Guest with limited browsing (0-100 points)")
            ]
            
            for role in roles_data:
                db.add(role)
            db.commit()
            print("✅ Created default roles")
        else:
            print("✅ Roles already exist")
        
        # Get role objects
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        player_role = db.query(Role).filter(Role.name == "player").first()
        mentor_role = db.query(Role).filter(Role.name == "mentor").first()
        
        # Check if demo users already exist
        existing_users = db.query(User).filter(User.email.in_([
            'admin@learnonline.cc',
            'user@learnonline.cc',
            'mentor@learnonline.cc'
        ])).all()
        
        if existing_users:
            print("✅ Demo accounts already exist")
            for user in existing_users:
                print(f"   - {user.email} (Role: {user.role.name if user.role else 'None'})")
            return
        
        # Create demo accounts
        print("👤 Creating demo accounts...")
        
        # Admin account
        admin_id = uuid.uuid4()
        admin_password_hash = get_password_hash("admin123")
        
        admin_user = User(
            id=admin_id,
            email="admin@learnonline.cc",
            password_hash=admin_password_hash,
            first_name="Admin",
            last_name="User",
            role_id=admin_role.id,
            is_active=True
        )
        db.add(admin_user)
        db.flush()  # Flush to get the ID
        
        admin_profile = UserProfile(
            id=uuid.uuid4(),
            user_id=admin_id,
            experience_points=5000,
            level=10
        )
        db.add(admin_profile)
        
        print("✅ Created admin@learnonline.cc / admin123")
        
        # Regular user account
        user_id = uuid.uuid4()
        user_password_hash = get_password_hash("user123")
        
        regular_user = User(
            id=user_id,
            email="user@learnonline.cc",
            password_hash=user_password_hash,
            first_name="Demo",
            last_name="User",
            role_id=player_role.id,
            is_active=True
        )
        db.add(regular_user)
        db.flush()  # Flush to get the ID
        
        user_profile = UserProfile(
            id=uuid.uuid4(),
            user_id=user_id,
            experience_points=500,
            level=3
        )
        db.add(user_profile)
        
        print("✅ Created user@learnonline.cc / user123")
        
        # Mentor account
        mentor_id = uuid.uuid4()
        mentor_password_hash = get_password_hash("mentor123")
        
        mentor_user = User(
            id=mentor_id,
            email="mentor@learnonline.cc",
            password_hash=mentor_password_hash,
            first_name="Mentor",
            last_name="User",
            role_id=mentor_role.id,
            is_active=True
        )
        db.add(mentor_user)
        db.flush()  # Flush to get the ID
        
        mentor_profile = UserProfile(
            id=uuid.uuid4(),
            user_id=mentor_id,
            experience_points=1500,
            level=7
        )
        db.add(mentor_profile)
        
        print("✅ Created mentor@learnonline.cc / mentor123")
        
        # Commit all changes
        db.commit()
        
        print("\n🎉 Demo accounts created successfully!")
        print("\nDemo Accounts:")
        print("Admin:  admin@learnonline.cc  / admin123")
        print("User:   user@learnonline.cc   / user123")
        print("Mentor: mentor@learnonline.cc / mentor123")
        
    except Exception as e:
        print(f"❌ Error creating demo accounts: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_accounts()
