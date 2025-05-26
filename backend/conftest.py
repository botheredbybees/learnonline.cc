import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set testing environment
os.environ["TESTING"] = "true"
os.environ["ENVIRONMENT"] = "test"

from database import get_db, Base
from main import app
from models.tables import User, Role, UserProfile, Achievement, Badge
from auth.auth_handler import get_password_hash, sign_jwt, get_user_permissions

# Test database URL - use Docker container when available, fallback to localhost
TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://test_user:test_password@localhost:5433/learnonline_test"
)

# Create test engine and session
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database tables before running tests"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=test_engine)
        
        # Create a session to populate initial data
        db = TestingSessionLocal()
        
        # Create default roles if they don't exist
        roles_to_create = [
            {"name": "guest", "description": "Guest user"},
            {"name": "user", "description": "Regular user"},
            {"name": "admin", "description": "Administrator"},
            {"name": "instructor", "description": "Instructor"},
        ]
        
        for role_data in roles_to_create:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data)
                db.add(role)
        
        # Create default achievements if they don't exist
        achievements_to_create = [
            {
                "title": "First Login",
                "description": "Complete your first login",
                "experience_points": 10,
                "icon_url": "login.png"
            },
            {
                "title": "Content Explorer",
                "description": "View 5 different units",
                "experience_points": 50,
                "icon_url": "explorer.png"
            },
            {
                "title": "Quiz Master",
                "description": "Complete 10 quizzes",
                "experience_points": 100,
                "icon_url": "quiz.png"
            }
        ]
        
        for achievement_data in achievements_to_create:
            existing_achievement = db.query(Achievement).filter(
                Achievement.title == achievement_data["title"]
            ).first()
            if not existing_achievement:
                achievement = Achievement(**achievement_data)
                db.add(achievement)
        
        db.commit()
        db.close()
        
        yield
        
    except Exception as e:
        print(f"Database setup failed: {e}")
        # Don't fail the tests, just continue
        yield
    finally:
        # Cleanup is handled by Docker container lifecycle
        pass


@pytest.fixture
def test_client():
    """Create test client using test database"""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Get test database session for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_db_session(test_db):
    """Alias for test_db to match gamification test expectations"""
    return test_db


@pytest.fixture
def test_user(test_db: Session):
    """Create a test user in the database"""
    # Ensure roles exist
    guest_role = test_db.query(Role).filter(Role.name == "guest").first()
    if not guest_role:
        guest_role = Role(name="guest", description="Guest user")
        test_db.add(guest_role)
        test_db.commit()
        test_db.refresh(guest_role)
    
    # Create test user (using auto-increment ID)
    user = User(
        email="testuser@example.com",
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        role_id=guest_role.id,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        experience_points=0,
        level=1,
        total_achievements_count=0
    )
    test_db.add(profile)
    test_db.commit()
    
    yield user
    
    # Cleanup
    test_db.query(UserProfile).filter(UserProfile.user_id == user.id).delete()
    test_db.delete(user)
    test_db.commit()


@pytest.fixture
def test_user_data(test_user, test_db):
    """Provide test user data for gamification tests"""
    # Get the user's role
    user_role = test_db.query(Role).filter(Role.id == test_user.role_id).first()
    
    return {
        "test_user": test_user,
        "user_role": user_role
    }


@pytest.fixture
def test_admin(test_db: Session):
    """Create a test admin user in the database"""
    # Ensure admin role exists
    admin_role = test_db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(name="admin", description="Administrator")
        test_db.add(admin_role)
        test_db.commit()
        test_db.refresh(admin_role)
    
    # Create test admin user (using auto-increment ID)
    user = User(
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        first_name="Admin",
        last_name="User",
        role_id=admin_role.id,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create user profile
    profile = UserProfile(
        user_id=user.id,
        experience_points=0,
        level=1,
        total_achievements_count=0
    )
    test_db.add(profile)
    test_db.commit()
    
    yield user
    
    # Cleanup
    test_db.query(UserProfile).filter(UserProfile.user_id == user.id).delete()
    test_db.delete(user)
    test_db.commit()


@pytest.fixture
def test_achievements_data(test_db: Session):
    """Create test achievements for gamification tests"""
    achievements = []
    
    # Get existing achievements or create new ones
    achievement1 = test_db.query(Achievement).filter(Achievement.title == "First Login").first()
    if not achievement1:
        achievement1 = Achievement(
            title="First Login",
            description="Complete your first login",
            experience_points=10,
            icon_url="login.png"
        )
        test_db.add(achievement1)
        test_db.commit()
        test_db.refresh(achievement1)
    
    achievement2 = test_db.query(Achievement).filter(Achievement.title == "Content Explorer").first()
    if not achievement2:
        achievement2 = Achievement(
            title="Content Explorer",
            description="View 5 different units",
            experience_points=50,
            icon_url="explorer.png"
        )
        test_db.add(achievement2)
        test_db.commit()
        test_db.refresh(achievement2)
    
    achievements.extend([achievement1, achievement2])
    
    yield achievements
    
    # Don't delete achievements as they might be used by other tests


@pytest.fixture
def authenticated_user(test_user: User, test_db: Session):
    """Create an authenticated user with token"""
    # Refresh user to get role relationship
    test_db.refresh(test_user)
    role_name = test_user.role.name if test_user.role else "guest"
    permissions = get_user_permissions(test_db, role_name)
    token_data = sign_jwt(str(test_user.id), role_name, permissions)
    return test_user, token_data["access_token"]


@pytest.fixture
def authenticated_user_token(authenticated_user):
    """Get just the token for authenticated user"""
    return authenticated_user[1]


@pytest.fixture
def authenticated_admin(test_admin: User, test_db: Session):
    """Create an authenticated admin user with token"""
    # Refresh admin to get role relationship
    test_db.refresh(test_admin)
    role_name = test_admin.role.name if test_admin.role else "admin"
    permissions = get_user_permissions(test_db, role_name)
    token_data = sign_jwt(str(test_admin.id), role_name, permissions)
    return test_admin, token_data["access_token"]


@pytest.fixture
def cache():
    """Mock cache for testing"""
    return {}
