#!/usr/bin/env python3
"""
Script to populate roles and permissions tables with initial data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.tables import Role, Permission, RolePermission
from db.database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_roles_and_permissions():
    """Populate the roles and permissions tables with initial data"""
    
    # Create database connection
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Define roles
        roles_data = [
            {
                "name": "admin",
                "description": "Full system access, AQTF sync, user management"
            },
            {
                "name": "mentor", 
                "description": "Team management, content creation (1001+ points)"
            },
            {
                "name": "player",
                "description": "Content access, assessments (101-1000 points)"
            },
            {
                "name": "guest",
                "description": "Limited browsing (0-100 points)"
            }
        ]
        
        # Define permissions
        permissions_data = [
            {"name": "view_dashboard", "description": "Access to user dashboard"},
            {"name": "view_content", "description": "View training content"},
            {"name": "create_content", "description": "Create and edit training content"},
            {"name": "manage_users", "description": "Manage user accounts"},
            {"name": "sync_aqtf", "description": "Synchronize AQTF data"},
            {"name": "take_assessments", "description": "Take assessments and quizzes"},
            {"name": "view_progress", "description": "View learning progress"},
            {"name": "manage_teams", "description": "Manage teams and mentoring"},
            {"name": "admin_access", "description": "Full administrative access"},
            {"name": "browse_units", "description": "Browse training units"},
            {"name": "view_achievements", "description": "View achievements and badges"},
            {"name": "limited_browse", "description": "Limited browsing access"}
        ]
        
        # Create roles
        created_roles = {}
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
                db.flush()  # Get the ID
                created_roles[role_data["name"]] = role
                logger.info(f"Created role: {role_data['name']}")
            else:
                created_roles[role_data["name"]] = existing_role
                logger.info(f"Role already exists: {role_data['name']}")
        
        # Create permissions
        created_permissions = {}
        for perm_data in permissions_data:
            existing_perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing_perm:
                permission = Permission(**perm_data)
                db.add(permission)
                db.flush()  # Get the ID
                created_permissions[perm_data["name"]] = permission
                logger.info(f"Created permission: {perm_data['name']}")
            else:
                created_permissions[perm_data["name"]] = existing_perm
                logger.info(f"Permission already exists: {perm_data['name']}")
        
        # Define role-permission mappings
        role_permissions = {
            "admin": [
                "view_dashboard", "view_content", "create_content", "manage_users",
                "sync_aqtf", "take_assessments", "view_progress", "manage_teams",
                "admin_access", "browse_units", "view_achievements"
            ],
            "mentor": [
                "view_dashboard", "view_content", "create_content", "take_assessments",
                "view_progress", "manage_teams", "browse_units", "view_achievements"
            ],
            "player": [
                "view_dashboard", "view_content", "take_assessments", "view_progress",
                "browse_units", "view_achievements"
            ],
            "guest": [
                "limited_browse", "view_content", "browse_units"
            ]
        }
        
        # Create role-permission associations
        for role_name, permission_names in role_permissions.items():
            role = created_roles[role_name]
            for perm_name in permission_names:
                permission = created_permissions[perm_name]
                
                # Check if association already exists
                existing_assoc = db.query(RolePermission).filter(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == permission.id
                ).first()
                
                if not existing_assoc:
                    role_perm = RolePermission(role_id=role.id, permission_id=permission.id)
                    db.add(role_perm)
                    logger.info(f"Associated {role_name} with {perm_name}")
        
        # Commit all changes
        db.commit()
        logger.info("Successfully populated roles and permissions!")
        
        # Print summary
        print("\n=== ROLES AND PERMISSIONS SUMMARY ===")
        for role_name in roles_data:
            role = created_roles[role_name["name"]]
            perms = role_permissions[role_name["name"]]
            print(f"\n{role_name['name'].upper()} ({role.id}):")
            print(f"  Description: {role.description}")
            print(f"  Permissions: {', '.join(perms)}")
        
    except Exception as e:
        logger.error(f"Error populating roles and permissions: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    populate_roles_and_permissions()
