#!/usr/bin/env python3

import os
import sys
sys.path.append('backend')

# Set test environment
os.environ['ENVIRONMENT'] = 'test'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.conftest import get_test_database_url
from backend.models.tables import User, Role, UserProfile
from backend.auth.auth_handler import get_password_hash

def populate_test_data():
    print("=== Populating Test Database ===")
    
    # Get test database URL
    db_url = get_test_database_url()
    print(f"Test DB URL: {db_url}")
    
    # Create engine and session
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Clear existing data
        session.query(UserProfile).delete()
        session.query(User).delete()
        session.query(Role).delete()
        session.commit()
        
        # Create roles
        roles_data = [
            ("admin", "Administrator with full access"),
            ("mentor", "Mentor with content creation and team management"),
            ("user", "Regular user with content access and assessments"),
            ("guest", "Guest with limited browsing")
        ]
        
        roles = {}
        for role_name, role_desc in roles_data:
            role = Role(
                name=role_name,
                description=role_desc
            )
            session.add(role)
            roles[role_name] = role
        
        session.commit()
        print(f"Created {len(roles)} roles")
        
        # Create users
        users_data = [
            {
                "email": "admin@example.com",
                "password": "secret",
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "experience_points": 1000,
                "level": 5
            },
            {
                "email": "mentor@example.com", 
                "password": "secret",
                "first_name": "Mentor",
                "last_name": "User",
                "role": "mentor",
                "experience_points": 500,
                "level": 3
            },
            {
                "email": "test@example.com",
                "password": "secret",
                "first_name": "Test",
                "last_name": "User", 
                "role": "user",
                "experience_points": 100,
                "level": 1
            },
            {
                "email": "guest@example.com",
                "password": "secret",
                "first_name": "Guest",
                "last_name": "User",
                "role": "guest",
                "experience_points": 0,
                "level": 1
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role_id=roles[user_data["role"]].id,
                is_active=True
            )
            session.add(user)
            session.flush()  # This will assign the ID
            created_users.append((user, user_data))
        
        session.commit()
        print(f"Created {len(created_users)} users")
        
        # Create user profiles
        for user, user_data in created_users:
            profile = UserProfile(
                user_id=user.id,
                experience_points=user_data["experience_points"],
                level=user_data["level"]
            )
            session.add(profile)
        
        session.commit()
        print(f"Created {len(created_users)} user profiles")
        
        # Verify data
        print("\n=== Verification ===")
        users = session.query(User).all()
        for user in users:
            print(f"User: {user.email} ({user.role.name}) - Active: {user.is_active}")
        
        print("\nTest data population completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    populate_test_data()
