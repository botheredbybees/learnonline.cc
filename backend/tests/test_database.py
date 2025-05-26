"""
Simple Database Connection Tests

Tests basic database connectivity using production database for development testing.
"""

import pytest
from sqlalchemy import text
from models.tables import Role, User, Achievement


def test_database_connection(test_db):
    """Test that we can connect to the database."""
    # Simple query to verify connection
    result = test_db.execute(text("SELECT 1 as test_value"))
    row = result.fetchone()
    assert row[0] == 1


def test_database_tables_exist(test_db):
    """Test that all required tables exist in the database."""
    # Check that we can query the main tables
    roles_count = test_db.query(Role).count()
    users_count = test_db.query(User).count()
    achievements_count = test_db.query(Achievement).count()
    
    # These should not fail (tables exist)
    assert roles_count >= 0
    assert users_count >= 0
    assert achievements_count >= 0


def test_database_basic_operations(test_db):
    """Test basic database operations work."""
    # Count existing roles
    initial_roles = test_db.query(Role).count()
    
    # This should work without errors
    roles = test_db.query(Role).all()
    assert len(roles) == initial_roles
    
    # Test that we can access role properties
    if roles:
        first_role = roles[0]
        assert hasattr(first_role, 'name')
        assert hasattr(first_role, 'description')
