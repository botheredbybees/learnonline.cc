# API Testing Examples

This document provides comprehensive examples and procedures for testing the LearnOnline.cc REST API endpoints.

## Table of Contents

1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [Authentication Testing](#authentication-testing)
4. [Units API Testing](#units-api-testing)
5. [User Management API Testing](#user-management-api-testing)
6. [Achievements API Testing](#achievements-api-testing)
7. [Error Handling Testing](#error-handling-testing)
8. [Performance Testing](#performance-testing)
9. [Security Testing](#security-testing)

## Overview

The LearnOnline.cc API provides RESTful endpoints for:
- Authentication and authorization
- Training units management
- User management and progress tracking
- Achievements and badges
- TGA data synchronization

## Test Environment Setup

### Base URL Configuration

```python
# Test configuration
BASE_URL = "http://localhost:8000"  # Development
# BASE_URL = "https://api.staging.learnonline.cc"  # Staging
# BASE_URL = "https://api.learnonline.cc"  # Production

API_BASE = f"{BASE_URL}/api"
```

### Test Client Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """Get authentication headers for testing."""
    client = TestClient(app)
    
    # Login to get token
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    return {}

@pytest.fixture
def admin_headers():
    """Get admin authentication headers for testing."""
    client = TestClient(app)
    
    # Login as admin
    response = client.post("/api/auth/login", data={
        "username": "admin@example.com",
        "password": "adminpassword"
    })
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    return {}
```

## Authentication Testing

### Login Endpoint Testing

```python
# tests/test_auth_api.py
def test_login_success(client):
    """Test successful login."""
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data

def test_login_missing_fields(client):
    """Test login with missing fields."""
    response = client.post("/api/auth/login", data={
        "username": "test@example.com"
        # Missing password
    })
    
    assert response.status_code == 422

def test_login_invalid_email_format(client):
    """Test login with invalid email format."""
    response = client.post("/api/auth/login", data={
        "username": "invalid-email",
        "password": "testpassword"
    })
    
    assert response.status_code == 401
```

### Token Validation Testing

```python
def test_protected_endpoint_with_valid_token(client, auth_headers):
    """Test accessing protected endpoint with valid token."""
    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert "email" in data
    assert "username" in data
    assert "role" in data

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401

def test_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/auth/me", headers=headers)
    
    assert response.status_code == 401

def test_token_expiration(client):
    """Test token expiration handling."""
    # This would require mocking time or using expired tokens
    # Implementation depends on your token expiration strategy
    pass
```

## Units API Testing

### List Units Endpoint

```python
# tests/test_units_api.py
def test_get_units_list(client):
    """Test getting list of units."""
    response = client.get("/api/units/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert isinstance(data["items"], list)

def test_get_units_with_pagination(client):
    """Test units list with pagination."""
    response = client.get("/api/units/?page=1&size=5")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["items"]) <= 5
    assert data["page"] == 1
    assert data["size"] == 5

def test_get_units_with_search(client):
    """Test units list with search filter."""
    response = client.get("/api/units/?search=ICT")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify search results contain ICT
    for unit in data["items"]:
        assert "ICT" in unit["code"] or "ICT" in unit["title"]

def test_get_units_with_component_type_filter(client):
    """Test units list with component type filter."""
    response = client.get("/api/units/?component_type=Unit")
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify all results are units
    for unit in data["items"]:
        assert unit["component_type"] == "Unit"
```

### Individual Unit Endpoints

```python
def test_get_unit_by_id(client):
    """Test getting unit by ID."""
    # First get a unit ID from the list
    response = client.get("/api/units/?size=1")
    assert response.status_code == 200
    
    units = response.json()["items"]
    if not units:
        pytest.skip("No units available for testing")
    
    unit_id = units[0]["id"]
    
    # Get unit by ID
    response = client.get(f"/api/units/{unit_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == unit_id
    assert "code" in data
    assert "title" in data
    assert "description" in data

def test_get_unit_by_code(client):
    """Test getting unit by code."""
    response = client.get("/api/units/code/ICTICT214")
    
    if response.status_code == 200:
        data = response.json()
        assert data["code"] == "ICTICT214"
        assert "title" in data
        assert "description" in data
    elif response.status_code == 404:
        # Unit not found - acceptable for test
        pass
    else:
        pytest.fail(f"Unexpected status code: {response.status_code}")

def test_get_unit_nonexistent_id(client):
    """Test getting non-existent unit."""
    response = client.get("/api/units/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_get_unit_invalid_id(client):
    """Test getting unit with invalid ID format."""
    response = client.get("/api/units/invalid_id")
    
    assert response.status_code == 422
```

### Unit Elements and Performance Criteria

```python
def test_get_unit_elements_with_pc(client):
    """Test getting unit elements with performance criteria."""
    # Get a unit first
    response = client.get("/api/units/?size=1")
    assert response.status_code == 200
    
    units = response.json()["items"]
    if not units:
        pytest.skip("No units available for testing")
    
    unit_id = units[0]["id"]
    
    # Get elements with performance criteria
    response = client.get(f"/api/units/{unit_id}/elements-with-pc")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    
    for element in data:
        assert "id" in element
        assert "number" in element
        assert "title" in element
        assert "performance_criteria" in element
        assert isinstance(element["performance_criteria"], list)
        
        for pc in element["performance_criteria"]:
            assert "id" in pc
            assert "number" in pc
            assert "text" in pc
```

### Search Endpoint

```python
def test_search_units_local_and_tga(client):
    """Test searching units in local database and TGA."""
    response = client.get("/api/units/search?query=ICT&source=both")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "local_results" in data
    assert "tga_results" in data
    assert isinstance(data["local_results"], list)
    assert isinstance(data["tga_results"], list)

def test_search_units_local_only(client):
    """Test searching units in local database only."""
    response = client.get("/api/units/search?query=ICT&source=local")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "local_results" in data
    assert "tga_results" not in data

def test_search_units_tga_only(client):
    """Test searching units in TGA only."""
    response = client.get("/api/units/search?query=ICT&source=tga")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "tga_results" in data
    assert "local_results" not in data

def test_search_units_empty_query(client):
    """Test searching with empty query."""
    response = client.get("/api/units/search?query=")
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
```

### Admin-Only Sync Endpoint

```python
def test_sync_unit_as_admin(client, admin_headers):
    """Test syncing unit as admin user."""
    response = client.post(
        "/api/units/ICTICT214/sync",
        headers=admin_headers
    )
    
    # Response could be 200 (success) or 404 (unit not found in TGA)
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert "message" in data
        assert "unit" in data

def test_sync_unit_as_regular_user(client, auth_headers):
    """Test syncing unit as regular user (should fail)."""
    response = client.post(
        "/api/units/ICTICT214/sync",
        headers=auth_headers
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data

def test_sync_unit_without_auth(client):
    """Test syncing unit without authentication."""
    response = client.post("/api/units/ICTICT214/sync")
    
    assert response.status_code == 401
```

## User Management API Testing

### User Profile Endpoints

```python
# tests/test_users_api.py
def test_get_current_user(client, auth_headers):
    """Test getting current user profile."""
    response = client.get("/api/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert "email" in data
    assert "username" in data
    assert "role" in data
    assert "is_active" in data

def test_update_user_profile(client, auth_headers):
    """Test updating user profile."""
    update_data = {
        "username": "updated_username",
        "first_name": "Updated",
        "last_name": "Name"
    }
    
    response = client.put(
        "/api/users/me",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["username"] == "updated_username"
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"

def test_get_user_progress(client, auth_headers):
    """Test getting user progress."""
    response = client.get("/api/users/me/progress", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "total_points" in data
    assert "level" in data
    assert "completed_units" in data
    assert "achievements" in data
```

### Admin User Management

```python
def test_list_users_as_admin(client, admin_headers):
    """Test listing users as admin."""
    response = client.get("/api/users/", headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)

def test_list_users_as_regular_user(client, auth_headers):
    """Test listing users as regular user (should fail)."""
    response = client.get("/api/users/", headers=auth_headers)
    
    assert response.status_code == 403

def test_create_user_as_admin(client, admin_headers):
    """Test creating user as admin."""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword",
        "role_id": 2  # Regular user role
    }
    
    response = client.post(
        "/api/users/",
        json=user_data,
        headers=admin_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "password" not in data  # Password should not be returned
```

## Achievements API Testing

### Achievements Endpoints

```python
# tests/test_achievements_api.py
def test_get_achievements_list(client):
    """Test getting list of achievements."""
    response = client.get("/api/achievements/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    
    for achievement in data:
        assert "id" in achievement
        assert "name" in achievement
        assert "description" in achievement
        assert "points_required" in achievement

def test_get_user_achievements(client, auth_headers):
    """Test getting user's achievements."""
    response = client.get("/api/users/me/achievements", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    
    for user_achievement in data:
        assert "achievement" in user_achievement
        assert "earned_at" in user_achievement
        assert "points_earned" in user_achievement

def test_get_badges_list(client):
    """Test getting list of badges."""
    response = client.get("/api/badges/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    
    for badge in data:
        assert "id" in badge
        assert "name" in badge
        assert "description" in badge
        assert "icon_url" in badge
```

## Error Handling Testing

### HTTP Error Responses

```python
# tests/test_error_handling.py
def test_404_not_found(client):
    """Test 404 error handling."""
    response = client.get("/api/nonexistent-endpoint")
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data

def test_405_method_not_allowed(client):
    """Test 405 error handling."""
    response = client.delete("/api/units/")  # DELETE not allowed on list endpoint
    
    assert response.status_code == 405
    data = response.json()
    assert "detail" in data

def test_422_validation_error(client):
    """Test 422 validation error handling."""
    response = client.post("/api/auth/login", data={
        "username": "invalid-email-format",
        "password": ""  # Empty password
    })
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)

def test_500_internal_server_error(client):
    """Test 500 error handling."""
    # This would require triggering an actual server error
    # Implementation depends on your error simulation strategy
    pass
```

### Rate Limiting Testing

```python
def test_rate_limiting(client):
    """Test API rate limiting."""
    # Make multiple rapid requests
    responses = []
    for i in range(100):  # Adjust based on your rate limits
        response = client.get("/api/units/")
        responses.append(response.status_code)
        
        if response.status_code == 429:  # Too Many Requests
            break
    
    # Should eventually hit rate limit
    assert 429 in responses
```

## Performance Testing

### Response Time Testing

```python
# tests/test_performance.py
import time

def test_api_response_times(client):
    """Test API response times."""
    endpoints = [
        "/api/units/",
        "/api/achievements/",
        "/api/badges/"
    ]
    
    for endpoint in endpoints:
        start_time = time.time()
        response = client.get(endpoint)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds

def test_large_dataset_performance(client):
    """Test performance with large datasets."""
    # Request large page size
    response = client.get("/api/units/?size=1000")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should handle large requests efficiently
    assert len(data["items"]) <= 1000
```

### Concurrent Request Testing

```python
import threading
import time

def test_concurrent_requests(client):
    """Test handling of concurrent requests."""
    results = []
    
    def make_request():
        response = client.get("/api/units/")
        results.append(response.status_code)
    
    # Create multiple threads
    threads = []
    for i in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
    
    # Start all threads
    start_time = time.time()
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    
    # All requests should succeed
    assert all(status == 200 for status in results)
    
    # Should handle concurrent requests efficiently
    assert end_time - start_time < 5.0
```

## Security Testing

### Input Validation Testing

```python
# tests/test_security.py
def test_sql_injection_protection(client):
    """Test protection against SQL injection."""
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'/*",
        "1; DELETE FROM units; --"
    ]
    
    for malicious_input in malicious_inputs:
        response = client.get(f"/api/units/search?query={malicious_input}")
        
        # Should not cause server error
        assert response.status_code in [200, 400, 422]
        
        # Should not return unexpected data
        if response.status_code == 200:
            data = response.json()
            # Verify response structure is normal
            assert isinstance(data, dict)

def test_xss_protection(client):
    """Test protection against XSS attacks."""
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "';alert('xss');//"
    ]
    
    for payload in xss_payloads:
        response = client.get(f"/api/units/search?query={payload}")
        
        # Should handle malicious input safely
        assert response.status_code in [200, 400, 422]
        
        if response.status_code == 200:
            # Response should not contain unescaped script tags
            response_text = response.text
            assert "<script>" not in response_text
            assert "javascript:" not in response_text

def test_authorization_bypass_attempts(client):
    """Test protection against authorization bypass."""
    # Try to access admin endpoints without proper authorization
    admin_endpoints = [
        "/api/users/",
        "/api/units/ICTICT214/sync"
    ]
    
    for endpoint in admin_endpoints:
        # Without authentication
        response = client.get(endpoint)
        assert response.status_code == 401
        
        # With regular user token (if available)
        # This would require setting up a regular user token
        pass
```

## Manual Testing with cURL

### Authentication

```bash
# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword"

# Save token
TOKEN="your_access_token_here"

# Access protected endpoint
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### Units API

```bash
# Get units list
curl -X GET "http://localhost:8000/api/units/"

# Get units with pagination
curl -X GET "http://localhost:8000/api/units/?page=1&size=10"

# Search units
curl -X GET "http://localhost:8000/api/units/search?query=ICT&source=both"

# Get unit by code
curl -X GET "http://localhost:8000/api/units/code/ICTICT214"

# Sync unit (admin only)
curl -X POST "http://localhost:8000/api/units/ICTICT214/sync" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Error Testing

```bash
# Test 404
curl -X GET "http://localhost:8000/api/nonexistent"

# Test 401
curl -X GET "http://localhost:8000/api/auth/me"

# Test 422
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=invalid&password="
```

## Test Data Management

### Creating Test Data

```python
# tests/fixtures/test_data.py
def create_test_user(db_session):
    """Create a test user."""
    from models.tables import User, Role
    
    role = db_session.query(Role).filter(Role.name == "user").first()
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_here",
        role_id=role.id,
        is_active=True
    )
    
    db_session.add(user)
    db_session.commit()
    return user

def create_test_unit(db_session):
    """Create a test unit."""
    from models.tables import Unit
    
    unit = Unit(
        code="TEST001",
        title="Test Unit",
        description="A test unit for API testing",
        component_type="Unit"
    )
    
    db_session.add(unit)
    db_session.commit()
    return unit
```

### Cleanup Test Data

```python
@pytest.fixture(autouse=True)
def cleanup_test_data(db_session):
    """Clean up test data after each test."""
    yield
    
    # Clean up test data
    db_session.query(User).filter(User.email.like("%test%")).delete()
    db_session.query(Unit).filter(Unit.code.like("TEST%")).delete()
    db_session.commit()
```

## Continuous Integration

### API Test Pipeline

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: learnonline_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-cov httpx
    
    - name: Run API tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/learnonline_test
      run: |
        cd backend
        pytest tests/test_*_api.py -v --cov=routers
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

This comprehensive API testing guide provides examples and procedures for testing all aspects of the LearnOnline.cc REST API, ensuring reliability, security, and performance.
