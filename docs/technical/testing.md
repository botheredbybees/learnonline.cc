# Testing Guide for LearnOnline.cc

This document provides comprehensive instructions for testing the LearnOnline.cc application, including backend API testing, frontend testing, integration testing, and TGA API testing.

## Table of Contents

1. [Overview](#overview)
2. [Test Runner Script (run_tests.sh)](#test-runner-script-run_testssh)
3. [Test Environment Setup](#test-environment-setup)
4. [Backend Testing](#backend-testing)
5. [Frontend Testing](#frontend-testing)
6. [Integration Testing](#integration-testing)
7. [TGA API Testing](#tga-api-testing)
8. [Database Testing](#database-testing)
9. [Performance Testing](#performance-testing)
10. [Security Testing](#security-testing)
11. [Continuous Integration](#continuous-integration)

## Overview

The LearnOnline.cc application uses multiple testing approaches:

- **Backend**: Pytest for API and service testing
- **Frontend**: Manual testing and browser automation with Selenium
- **Integration**: End-to-end testing of complete workflows
- **TGA API**: Testing external API integration
- **Database**: Testing data persistence and integrity

## Test Runner Script (run_tests.sh)

The project includes a comprehensive test runner script `run_tests.sh` that provides easy commands to run different types of tests using Docker containers. This is the **recommended way** to run tests as it ensures a consistent, isolated test environment.

### Prerequisites

- Docker and Docker Compose installed
- Make sure the script is executable: `chmod +x run_tests.sh`

### Available Commands

```bash
# Show help and available commands
./run_tests.sh help

# Set up test environment (run this first)
./run_tests.sh setup

# Run unit tests
./run_tests.sh unit

# Run integration tests
./run_tests.sh integration

# Run API tests
./run_tests.sh api

# Run frontend tests (with Selenium)
./run_tests.sh frontend

# Run TGA integration tests
./run_tests.sh tga

# Run performance tests
./run_tests.sh performance

# Run load tests with Locust
./run_tests.sh load

# Run all tests (recommended for CI/CD)
./run_tests.sh all

# Clean up test environment
./run_tests.sh clean

# Show test logs
./run_tests.sh logs

# Generate coverage report
./run_tests.sh coverage

# Run health check
./run_tests.sh health
```

### Quick Start

```bash
# 1. Set up the test environment
./run_tests.sh setup

# 2. Run unit tests
./run_tests.sh unit

# 3. Run all tests
./run_tests.sh all

# 4. Clean up when done
./run_tests.sh clean
```

### Test Environment Details

The test runner uses Docker Compose to create an isolated test environment with:

- **PostgreSQL test database** (port 5433)
- **Backend test service** (port 8001)
- **Frontend test service** (port 8081)
- **Redis test cache** (port 6380)
- **Selenium Grid Hub** (port 4444)
- **Chrome and Firefox browsers** for Selenium testing

### Environment Variables

Set these environment variables for TGA testing:

```bash
export TGA_USERNAME=your_tga_username
export TGA_PASSWORD=your_tga_password
```

### Test Results and Reports

Test results are saved to the `test-results/` directory:

- `test-results/unit-tests.xml` - Unit test results (JUnit format)
- `test-results/integration-tests.xml` - Integration test results
- `test-results/api-tests.xml` - API test results
- `test-results/coverage/` - Coverage reports (HTML and XML)
- `test-results/performance/` - Performance test results
- `test-results/screenshots/` - Frontend test screenshots

### Troubleshooting Test Runner

```bash
# Check Docker is running
docker info

# Check test containers status
docker-compose -f docker-compose.test.yml ps

# View logs for specific service
./run_tests.sh logs backend-test
./run_tests.sh logs postgres-test

# Force cleanup if containers are stuck
docker-compose -f docker-compose.test.yml down -v --remove-orphans

# Rebuild test images if needed
docker-compose -f docker-compose.test.yml build --no-cache
```

## Test Environment Setup

### Prerequisites

```bash
# Install Python dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Install Node.js dependencies (if using npm for frontend tools)
npm install -g selenium-webdriver

# Install browser drivers for Selenium
# Chrome
wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/LATEST_RELEASE/chromedriver_linux64.zip
unzip /tmp/chromedriver.zip -d /usr/local/bin/

# Firefox
wget -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz
tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/
```

### Environment Configuration

Create test environment files:

```bash
# Backend test environment
cp backend/.env.example backend/.env.test

# Update test environment variables
cat >> backend/.env.test << EOF
DATABASE_URL=postgresql://test_user:test_password@postgres-test:5432/learnonline_test
TGA_USERNAME=your_test_username
TGA_PASSWORD=your_test_password
JWT_SECRET=test_secret_key_for_testing_only
ENVIRONMENT=test
EOF
```

### Test Database Setup

```bash
# Create test database
createdb learnonline_test

# Apply schema to test database
PGDATABASE=learnonline_test psql -f schema.sql

# Or using Docker (recommended)
docker-compose -f docker-compose.test.yml up -d postgres-test
```

## Backend Testing

### Running Backend Tests

**Using Test Runner (Recommended):**
```bash
# Run unit tests
./run_tests.sh unit

# Run API tests
./run_tests.sh api

# Run TGA tests
./run_tests.sh tga
```

**Manual Testing:**
```bash
# Navigate to backend directory
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test files
pytest tests/test_tga_xml.py
pytest tests/test_unit_xml_parser.py

# Run tests with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_tga" -v
```

### Test Categories

#### 1. Unit Tests
Test individual functions and classes in isolation.

```bash
# Using test runner
./run_tests.sh unit

# Manual testing
pytest tests/test_tga_client.py -v
pytest tests/test_models.py -v
pytest tests/test_routers.py -v
```

#### 2. Service Tests
Test business logic and service layer functionality.

```bash
# Test TGA service integration
pytest tests/test_tga_service.py -v

# Test authentication service
pytest tests/test_auth_service.py -v
```

#### 3. API Tests
Test REST API endpoints and responses.

```bash
# Using test runner
./run_tests.sh api

# Manual testing
pytest tests/test_api/ -v
pytest tests/test_api/test_units_router.py -v
```

### Writing New Tests

Create test files following the pattern `test_*.py`:

```python
# tests/test_example.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_async_function():
    # Test async functions
    result = await some_async_function()
    assert result is not None
```

## Frontend Testing

### Automated Frontend Testing

**Using Test Runner (Recommended):**
```bash
# Run frontend tests with Selenium
./run_tests.sh frontend
```

**Manual Testing:**
```bash
# Install Selenium dependencies
pip install selenium pytest-selenium

# Run frontend tests
pytest tests/frontend/ -v

# Run with specific browser
pytest tests/frontend/ --browser=chrome -v
pytest tests/frontend/ --browser=firefox -v

# Run headless
pytest tests/frontend/ --headless -v
```

### Manual Testing Checklist

See [Frontend Testing Checklist](testing/frontend_testing.md) for detailed manual testing procedures.

### Browser Testing

```python
# tests/frontend/test_units_page.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import pytest

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

def test_units_page_loads(driver):
    driver.get("http://localhost:8080/units")
    assert "Training Units Explorer" in driver.title
    
def test_unit_search(driver):
    driver.get("http://localhost:8080/units")
    search_box = driver.find_element(By.ID, "search-query")
    search_box.send_keys("ICT")
    search_box.submit()
    # Add assertions for search results
```

## Integration Testing

### End-to-End Testing

**Using Test Runner (Recommended):**
```bash
# Run integration tests
./run_tests.sh integration

# Run all tests including integration
./run_tests.sh all
```

**Manual Testing:**
```bash
# Run full integration tests
pytest tests/integration/ -v

# Test complete user workflows
pytest tests/integration/test_user_workflows.py -v

# Test TGA integration
pytest tests/integration/test_tga_integration.py -v
```

### Docker Integration Testing

```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run integration tests against Docker environment
pytest tests/integration/ --base-url=http://localhost:8080 -v

# Cleanup
docker-compose -f docker-compose.test.yml down
```

## TGA API Testing

### TGA Service Testing

**Using Test Runner (Recommended):**
```bash
# Run TGA integration tests
./run_tests.sh tga
```

**Manual Testing:**
```bash
# Test TGA API connectivity
python backend/scripts/tga_utils.py parse --unit ICTICT214

# Test TGA client directly
pytest tests/test_tga_xml.py::test_tga_client_search -v

# Test XML parsing
pytest tests/test_unit_xml_parser.py -v
```

### TGA Integration Tests

```bash
# Test full TGA workflow
pytest tests/integration/test_tga_workflow.py -v

# Test TGA data synchronization
python backend/scripts/tga/tp_get.py --test-mode
```

See [TGA Testing Guide](testing/tga_testing.md) for detailed TGA-specific testing procedures.

## Database Testing

### Database Test Setup

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///./test.db")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
```

### Database Tests

```bash
# Test database operations
pytest tests/test_database.py -v

# Test data migrations
pytest tests/test_migrations.py -v

# Test data integrity
pytest tests/test_data_integrity.py -v
```

## Performance Testing

### Load Testing

**Using Test Runner (Recommended):**
```bash
# Run performance tests
./run_tests.sh performance

# Run load tests with Locust
./run_tests.sh load
```

**Manual Testing:**
```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

### Performance Benchmarks

```python
# tests/performance/test_api_performance.py
import time
import pytest

def test_api_response_time():
    start_time = time.time()
    response = client.get("/api/units/")
    end_time = time.time()
    
    assert response.status_code == 200
    assert (end_time - start_time) < 1.0  # Should respond within 1 second
```

## Security Testing

### Authentication Testing

```bash
# Test authentication endpoints
pytest tests/security/test_auth.py -v

# Test authorization
pytest tests/security/test_authorization.py -v

# Test JWT token handling
pytest tests/security/test_jwt.py -v
```

### Security Checklist

- [ ] SQL injection protection
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Authentication bypass attempts
- [ ] Authorization escalation attempts
- [ ] Input validation
- [ ] Rate limiting

## Continuous Integration

### GitHub Actions Setup

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1
    
    - name: Make test script executable
      run: chmod +x run_tests.sh
    
    - name: Run all tests
      run: ./run_tests.sh all
      env:
        TGA_USERNAME: ${{ secrets.TGA_USERNAME }}
        TGA_PASSWORD: ${{ secrets.TGA_PASSWORD }}
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: test-results
        path: test-results/
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v1
      with:
        file: test-results/coverage/unit.xml
```

## Test Data Management

### Test Fixtures

```python
# tests/fixtures.py
import pytest
from models.tables import User, Unit, TrainingPackage

@pytest.fixture
def sample_user():
    return User(
        email="test@example.com",
        username="testuser",
        is_active=True
    )

@pytest.fixture
def sample_unit():
    return Unit(
        code="ICTICT214",
        title="Operate application software packages",
        description="Test unit description"
    )
```

### Test Data Cleanup

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def cleanup_test_data():
    yield
    # Cleanup code runs after each test
    db.query(User).filter(User.email.like("%test%")).delete()
    db.commit()
```

## Troubleshooting

### Common Issues

1. **Test Runner Issues**
   ```bash
   # Check Docker is running
   docker info
   
   # Check script permissions
   chmod +x run_tests.sh
   
   # Force cleanup stuck containers
   docker-compose -f docker-compose.test.yml down -v --remove-orphans
   ```

2. **Database Connection Errors**
   ```bash
   # Check database is running
   pg_isready -h localhost -p 5433
   
   # Check test database exists
   docker-compose -f docker-compose.test.yml exec postgres-test psql -U test_user -d learnonline_test -c "\l"
   ```

3. **TGA API Connection Issues**
   ```bash
   # Test TGA connectivity
   curl -u username:password https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV12.svc?wsdl
   ```

4. **Frontend Test Failures**
   ```bash
   # Check if frontend server is running
   curl http://localhost:8081/
   
   # Check Selenium hub
   curl http://localhost:4444/wd/hub/status
   ```

### Debug Mode

```bash
# Run tests with debug output
pytest -s -v --tb=long

# Run specific test with debugging
pytest tests/test_specific.py::test_function -s -vv

# View test runner logs
./run_tests.sh logs backend-test
./run_tests.sh logs test-runner
```

## Test Reports

### Coverage Reports

**Using Test Runner:**
```bash
# Generate coverage report
./run_tests.sh coverage

# View coverage report
open test-results/coverage/unit/index.html
```

**Manual:**
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# Generate XML coverage report for CI
pytest --cov=. --cov-report=xml
```

### Test Results

```bash
# Generate JUnit XML report
pytest --junitxml=test-results.xml

# Generate detailed test report
pytest --html=report.html --self-contained-html
```

## Related Documentation

- [Frontend Testing Checklist](testing/frontend_testing.md)
- [TGA Testing Guide](testing/tga_testing.md)
- [API Testing Examples](testing/api_testing.md)
- [Performance Testing Guide](testing/performance_testing.md)
