import pytest
import uuid
import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to Python path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models.tables import Base, User, Role, UserProfile
from db.database import get_db
from auth.auth_handler import (
    get_password_hash, verify_password, sign_jwt, decode_jwt,
    create_access_token, create_refresh_token, refresh_access_token,
    get_user_permissions, get_user_role_by_experience
)

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(setup_database):
    return TestClient(app)

@pytest.fixture
def db_session(setup_database):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def test_roles():
    """Create test roles once per session"""
    db = TestingSessionLocal()
    try:
        # Ensure all tables are created first
        Base.metadata.create_all(bind=engine)
        
        role_data = [
            ("admin", "Administrator with full access"),
            ("mentor", "Mentor with content creation and team management"),
            ("player", "Player with content access and assessments"),
            ("guest", "Guest with limited browsing")
        ]
        
        roles = {}
        for name, description in role_data:
            # Check if role already exists
            existing_role = db.query(Role).filter(Role.name == name).first()
            if existing_role:
                roles[name] = existing_role
            else:
                role = Role(name=name, description=description)
                db.add(role)
                db.commit()
                db.refresh(role)
                roles[name] = role
        
        return roles
    finally:
        db.close()

@pytest.fixture
def test_user(db_session, test_roles):
    """Create a test user with unique email"""
    unique_email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    user = User(
        id=uuid.uuid4(),
        email=unique_email,
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        role_id=test_roles["guest"].id,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create user profile
    profile = UserProfile(
        id=uuid.uuid4(),
        user_id=user.id,
        experience_points=50,
        level=1
    )
    db_session.add(profile)
    db_session.commit()
    
    return user

class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes"""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)"""
        password = "testpassword123"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

class TestJWTTokens:
    """Test JWT token functionality"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"user_id": "test-user-id", "role": "player"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        data = {"user_id": "test-user-id"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding valid token"""
        data = {"user_id": "test-user-id", "role": "player"}
        token = create_access_token(data)
        decoded = decode_jwt(token)
        
        assert decoded is not None
        assert decoded["user_id"] == "test-user-id"
        assert decoded["role"] == "player"
        assert decoded["type"] == "access"
    
    def test_decode_invalid_token(self):
        """Test decoding invalid token"""
        invalid_token = "invalid.token.here"
        decoded = decode_jwt(invalid_token)
        
        assert decoded is None
    
    def test_decode_expired_token(self):
        """Test decoding expired token"""
        data = {"user_id": "test-user-id"}
        # Create token with past expiration
        expired_delta = timedelta(minutes=-10)
        token = create_access_token(data, expired_delta)
        decoded = decode_jwt(token)
        
        assert decoded is None
    
    def test_sign_jwt_complete(self):
        """Test complete JWT signing with role and permissions"""
        user_id = "test-user-id"
        role = "player"
        permissions = ["content_access", "assessments"]
        
        result = sign_jwt(user_id, role, permissions)
        
        assert "access_token" in result
        assert "refresh_token" in result
        assert "token_type" in result
        assert "expires_in" in result
        assert result["token_type"] == "bearer"
        
        # Verify access token content
        decoded = decode_jwt(result["access_token"])
        assert decoded["user_id"] == user_id
        assert decoded["role"] == role
        assert decoded["permissions"] == permissions

class TestRolePermissions:
    """Test role-based permission system"""
    
    def test_get_user_role_by_experience(self):
        """Test role assignment based on experience points"""
        assert get_user_role_by_experience(0) == "guest"
        assert get_user_role_by_experience(50) == "guest"
        assert get_user_role_by_experience(100) == "guest"
        assert get_user_role_by_experience(101) == "player"
        assert get_user_role_by_experience(500) == "player"
        assert get_user_role_by_experience(1000) == "player"
        assert get_user_role_by_experience(1001) == "mentor"
        assert get_user_role_by_experience(5000) == "mentor"
    
    def test_get_user_permissions(self, db_session):
        """Test getting permissions for different roles"""
        # Test predefined permissions
        admin_perms = get_user_permissions(db_session, "admin")
        assert "full_access" in admin_perms
        assert "user_management" in admin_perms
        assert "aqtf_sync" in admin_perms
        
        mentor_perms = get_user_permissions(db_session, "mentor")
        assert "content_creation" in mentor_perms
        assert "team_management" in mentor_perms
        assert "full_access" not in mentor_perms
        
        player_perms = get_user_permissions(db_session, "player")
        assert "content_access" in player_perms
        assert "assessments" in player_perms
        assert "content_creation" not in player_perms
        
        guest_perms = get_user_permissions(db_session, "guest")
        assert "limited_browsing" in guest_perms
        assert len(guest_perms) == 1

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_new_user(self, client, test_roles):
        """Test user registration"""
        user_data = {
            "email": f"newuser-{uuid.uuid4().hex[:8]}@example.com",
            "password": "NewPassword123!",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["first_name"] == user_data["first_name"]
        assert data["last_name"] == user_data["last_name"]
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["role"] == "guest"
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user.email,
            "password": "Password123!",
            "first_name": "Duplicate",
            "last_name": "User"
        }
        
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_login_valid_credentials(self, client, test_user):
        """Test login with valid credentials"""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["role"] == "guest"
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, test_user):
        """Test getting current user information"""
        # First login to get token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["role"] == "guest"
        assert "permissions" in data
        assert "profile" in data
    
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_refresh_token(self, client, test_user, db_session):
        """Test token refresh functionality"""
        # First login to get tokens
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        login_response = client.post("/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = client.post("/auth/refresh-token", json={"token": refresh_token})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post("/auth/refresh-token", json={"token": "invalid_token"})
        
        assert response.status_code == 401
    
    def test_change_password(self, client, test_user):
        """Test password change"""
        # First login to get token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Change password
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": "testpassword123",
            "new_password": "NewPassword123!"
        }
        response = client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 200
        
        # Verify old password no longer works
        old_login = client.post("/auth/login", data={
            "username": test_user.email,
            "password": "testpassword123"
        })
        assert old_login.status_code == 401
        
        # Verify new password works
        new_login = client.post("/auth/login", data={
            "username": test_user.email,
            "password": "NewPassword123!"
        })
        assert new_login.status_code == 200
    
    def test_change_password_wrong_current(self, client, test_user):
        """Test password change with wrong current password"""
        # First login to get token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Try to change password with wrong current password
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123!"
        }
        response = client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 400
        assert "Invalid current password" in response.json()["detail"]
    
    def test_verify_token(self, client, test_user):
        """Test token verification"""
        # First login to get token
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        login_response = client.post("/auth/login", data=login_data)
        token = login_response.json()["access_token"]
        
        # Verify token
        response = client.post("/auth/verify-token", json={"token": token})
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "role" in data
        assert "exp" in data
    
    def test_verify_invalid_token(self, client):
        """Test verification of invalid token"""
        response = client.post("/auth/verify-token", json={"token": "invalid_token"})
        
        assert response.status_code == 401

class TestSecurityFeatures:
    """Test security features and edge cases"""
    
    def test_inactive_user_login(self, client, test_user, db_session):
        """Test that inactive users cannot login"""
        # Deactivate user
        test_user.is_active = False
        db_session.commit()
        
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"]
    
    def test_password_reset_request(self, client, test_user):
        """Test password reset request"""
        reset_data = {"email": test_user.email}
        
        response = client.post("/auth/reset-password-request", json=reset_data)
        
        assert response.status_code == 200
        assert "reset link" in response.json()["message"]
    
    def test_password_reset_nonexistent_email(self, client):
        """Test password reset request for nonexistent email"""
        reset_data = {"email": "nonexistent@example.com"}
        
        response = client.post("/auth/reset-password-request", json=reset_data)
        
        # Should still return success to prevent email enumeration
        assert response.status_code == 200
        assert "reset link" in response.json()["message"]
    
    def test_token_expiration_handling(self, client):
        """Test handling of expired tokens"""
        # Create an expired token
        data = {"user_id": "test-user-id"}
        expired_delta = timedelta(minutes=-10)
        expired_token = create_access_token(data, expired_delta)
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_malformed_token_handling(self, client):
        """Test handling of malformed tokens"""
        malformed_tokens = [
            "not.a.token",
            "Bearer malformed",
            "",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.malformed",
        ]
        
        for token in malformed_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/auth/me", headers=headers)
            assert response.status_code == 401

class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_role_upgrade_by_experience(self, client, test_user, db_session):
        """Test automatic role upgrade based on experience points"""
        # Update user's experience points to trigger role change
        profile = db_session.query(UserProfile).filter(UserProfile.user_id == test_user.id).first()
        profile.experience_points = 1500  # Should make user a mentor
        db_session.commit()
        
        # Login should update role
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "mentor"
        assert "content_creation" in data["permissions"]
        assert "team_management" in data["permissions"]

if __name__ == "__main__":
    pytest.main([__file__])
