#!/usr/bin/env python3

import os
import sys
sys.path.append('backend')

# Set test environment
os.environ['ENVIRONMENT'] = 'test'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.conftest import get_test_database_url
from backend.models.tables import User, Role
from backend.auth.auth_handler import get_password_hash, verify_password
from backend.database import Base
from sqlalchemy import inspect

def debug_auth():
    print("=== Auth Debug ===")
    
    # Get test database URL
    db_url = get_test_database_url()
    print(f"Test DB URL: {db_url}")
    
    # Create engine and session
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        # Create tables if they don't exist
        if not tables:
            print("No tables found, creating them...")
            Base.metadata.create_all(bind=engine)
            tables = inspector.get_table_names()
            print(f"Tables after creation: {tables}")
        
        # Check if users exist
        users = session.query(User).all()
        print(f"Found {len(users)} users in database")
        
        for user in users:
            print(f"User: {user.email}, Active: {user.is_active}")
            print(f"Password hash: {user.password_hash[:50]}...")
            
            # Test password verification
            test_password = "secret"
            is_valid = verify_password(test_password, user.password_hash)
            print(f"Password 'secret' valid for {user.email}: {is_valid}")
            
        # Check roles
        roles = session.query(Role).all()
        print(f"Found {len(roles)} roles in database")
        for role in roles:
            print(f"Role: {role.name}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    debug_auth()
