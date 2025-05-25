"""
Test Authentication System

Tests for the authentication functionality including:
- Password hashing and verification
- JWT token creation and validation
- User registration and login
- Role-based access control
- Security features

Uses centralized PostgreSQL test configuration from conftest.py.
"""

import pytest
import uuid
from datetime import datetime, timedelta

from models.tables import User, Role, UserProfile
from auth.auth_handler import (
    get_password_hash, verify_password, sign_jwt, decode_jwt,
    create_access_token, create_refresh_token, refresh_access_token,
    get_user_permissions, get_user_role_by_experience
)


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
        data = {"user_id": "test-user-id", "role": "user"}
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
        data = {"user_id": "test-user-id", "role": "user"}
        token = create_access_token(data)
        decoded = decode_jwt(token)
        
        assert decoded is not None
        assert decoded["user_id"] == "test-user-id"
        assert decoded["role"] == "user"
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
        role = "user"
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
        assert get_user_role_by_experience(0) == "user"
        assert get_user_role_by_experience(50) == "user"
        assert get_user_role_by_experience(100) == "user"
        assert get_user_role_by_experience(101) == "player"  # Fixed: should be player
        assert get_user_role_by_experience(500) == "player"  # Fixed: should be player
        assert get_user_role_by_experience(1000) == "player"  # Fixed: should be player
        assert get_user_role_by_experience(1001) == "mentor"  # Fixed: should be mentor
        assert get_user_role_by_experience(5000) == "mentor"  # Fixed: should be mentor
    
    def test_get_user_permissions(self, test_db):
        """Test getting permissions for different roles"""
        # Test predefined permissions
        admin_perms = get_user_permissions(test_db, "admin")
        assert "full_access" in admin_perms
        assert "user_management" in admin_perms
        
        user_perms = get_user_permissions(test_db, "user")
        assert "limited_browsing" in user_perms
        assert "full_access" not in user_perms


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_register_new_user(self, test_client):
        """Test user registration"""
        user_data = {
            "email": f"newuser-{uuid.uuid4().hex[:8]}@example.com",
            "password": "NewPassword123!",
            "first_name": "New",
            "last_name": "User"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["email"]  # Fixed: username should be email
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_register_duplicate_email(self, test_client, test_user):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user.email,
            "password": "Password123!",
            "first_name": "Duplicate",
            "last_name": "User"
        }
        
        response = test_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409  # Fixed: should be 409 for conflict
        assert "already exists" in response.json()["detail"]
    
    def test_login_valid_credentials(self, test_client, test_user):
        """Test login with valid credentials"""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = test_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_invalid_credentials(self, test_client, test_user):
        """Test login with invalid credentials"""
        login_data = {
            "username": test_user.email,
            "password": "wrongpassword"
        }
        
        response = test_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, test_client):
        """Test login with nonexistent user"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = test_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
    
    def test_get_current_user(self, test_client, authenticated_user):
        """Test getting current user information"""
        user, token = authenticated_user
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user.email
        assert "permissions" in data
    
    def test_get_current_user_invalid_token(self, test_client):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_refresh_token(self, test_client, test_user):
        """Test token refresh functionality"""
        # First login to get tokens
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        login_response = test_client.post("/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = test_client.post("/auth/refresh-token", json={"token": refresh_token})
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_refresh_token_invalid(self, test_client):
        """Test refresh with invalid token"""
        response = test_client.post("/auth/refresh-token", json={"token": "invalid_token"})
        
        assert response.status_code == 401
    
    def test_change_password(self, test_client, authenticated_user):
        """Test password change"""
        user, token = authenticated_user
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": "testpassword123",
            "new_password": "NewPassword123!"
        }
        response = test_client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 200
        
        # Verify old password no longer works
        old_login = test_client.post("/auth/login", data={
            "username": user.email,
            "password": "testpassword123"
        })
        assert old_login.status_code == 401
        
        # Verify new password works
        new_login = test_client.post("/auth/login", data={
            "username": user.email,
            "password": "NewPassword123!"
        })
        assert new_login.status_code == 200
    
    def test_change_password_wrong_current(self, test_client, authenticated_user):
        """Test password change with wrong current password"""
        user, token = authenticated_user
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123!"
        }
        response = test_client.post("/auth/change-password", json=password_data, headers=headers)
        
        assert response.status_code == 400
        assert "Invalid current password" in response.json()["detail"]
    
    def test_verify_token(self, test_client, authenticated_user):
        """Test token verification"""
        user, token = authenticated_user
        response = test_client.post("/auth/verify-token", json={"token": token})
        
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "role" in data
        assert "exp" in data
    
    def test_verify_invalid_token(self, test_client):
        """Test verification of invalid token"""
        response = test_client.post("/auth/verify-token", json={"token": "invalid_token"})
        
        assert response.status_code == 401


class TestSecurityFeatures:
    """Test security features and edge cases"""
    
    def test_inactive_user_login(self, test_client, test_user, test_db):
        """Test that inactive users cannot login"""
        # Deactivate user
        test_user.is_active = False
        test_db.commit()
        
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = test_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"]
    
    def test_password_reset_request(self, test_client, test_user):
        """Test password reset request"""
        reset_data = {"email": test_user.email}
        
        response = test_client.post("/auth/reset-password-request", json=reset_data)
        
        assert response.status_code == 200
        assert "reset link" in response.json()["message"]
    
    def test_password_reset_nonexistent_email(self, test_client):
        """Test password reset request for nonexistent email"""
        reset_data = {"email": "nonexistent@example.com"}
        
        response = test_client.post("/auth/reset-password-request", json=reset_data)
        
        # Should still return success to prevent email enumeration
        assert response.status_code == 200
        assert "reset link" in response.json()["message"]
    
    def test_token_expiration_handling(self, test_client):
        """Test handling of expired tokens"""
        # Create an expired token
        data = {"user_id": "test-user-id"}
        expired_delta = timedelta(minutes=-10)
        expired_token = create_access_token(data, expired_delta)
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
    
    def test_malformed_token_handling(self, test_client):
        """Test handling of malformed tokens"""
        malformed_tokens = [
            "not.a.token",
            "Bearer malformed",
            "",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.malformed",
        ]
        
        for token in malformed_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = test_client.get("/auth/me", headers=headers)
            assert response.status_code == 401


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_role_permissions_in_token(self, test_client, test_user):
        """Test that role permissions are included in tokens"""
        login_data = {
            "username": test_user.email,
            "password": "testpassword123"
        }
        
        response = test_client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "permissions" in data
        assert isinstance(data["permissions"], list)
    
    def test_admin_permissions(self, test_client, authenticated_admin):
        """Test admin user permissions"""
        user, token = authenticated_admin
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "full_access" in data["permissions"]
        assert "user_management" in data["permissions"]
    
    def test_user_permissions(self, test_client, authenticated_user):
        """Test regular user permissions"""
        user, token = authenticated_user
        headers = {"Authorization": f"Bearer {token}"}
        response = test_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        permissions = data["permissions"]
        assert "limited_browsing" in permissions
        assert "full_access" not in permissions


if __name__ == "__main__":
    pytest.main([__file__])
