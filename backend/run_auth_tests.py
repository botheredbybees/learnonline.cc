#!/usr/bin/env python3
"""
Authentication Test Runner for LearnOnline.cc

This script runs comprehensive authentication tests including:
- Unit tests for JWT token generation, validation, and refresh mechanisms
- Integration tests for registration, login, and password reset flows
- Role-based access control testing for all permission levels
- Security testing for authentication bypass attempts and token manipulation
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    end_time = time.time()
    
    print(f"Duration: {end_time - start_time:.2f} seconds")
    
    if result.returncode == 0:
        print(f"✅ SUCCESS: {description}")
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
    else:
        print(f"❌ FAILED: {description}")
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
    
    return result.returncode == 0

def main():
    """Main test runner function"""
    print("🚀 Starting Authentication Test Suite for LearnOnline.cc")
    print(f"Working directory: {os.getcwd()}")
    
    # Change to backend directory if not already there
    if not os.path.exists("tests"):
        if os.path.exists("backend/tests"):
            os.chdir("backend")
            print(f"Changed to backend directory: {os.getcwd()}")
        else:
            print("❌ Could not find tests directory")
            sys.exit(1)
    
    # Ensure we have the required dependencies
    print("\n📦 Checking dependencies...")
    dependencies_check = run_command(
        "python -c \"import pytest, fastapi, sqlalchemy, passlib, jwt; print('All dependencies available')\"",
        "Dependency Check"
    )
    
    if not dependencies_check:
        print("❌ Missing dependencies. Please install requirements:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Set environment variables for testing
    os.environ["TESTING"] = "1"
    os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"
    os.environ["DATABASE_URL"] = "sqlite:///./test_auth.db"
    
    test_results = []
    
    # 1. Run authentication unit tests
    auth_tests = run_command(
        "python -m pytest tests/test_auth.py -v --tb=short --cov=auth --cov-report=term-missing",
        "Authentication Unit Tests"
    )
    test_results.append(("Authentication Unit Tests", auth_tests))
    
    # 2. Run authentication integration tests
    integration_tests = run_command(
        "python -m pytest tests/test_auth.py::TestAuthEndpoints -v --tb=short",
        "Authentication Integration Tests"
    )
    test_results.append(("Authentication Integration Tests", integration_tests))
    
    # 3. Run security tests
    security_tests = run_command(
        "python -m pytest tests/test_auth.py::TestSecurityFeatures -v --tb=short",
        "Security Tests"
    )
    test_results.append(("Security Tests", security_tests))
    
    # 4. Run role-based access control tests
    rbac_tests = run_command(
        "python -m pytest tests/test_auth.py::TestRoleBasedAccess -v --tb=short",
        "Role-Based Access Control Tests"
    )
    test_results.append(("RBAC Tests", rbac_tests))
    
    # 5. Run password hashing performance tests
    performance_tests = run_command(
        "python -c \"import time; from auth.auth_handler import get_password_hash, verify_password; "
        "start = time.time(); "
        "for i in range(100): hash = get_password_hash('test123'); verify_password('test123', hash); "
        "print(f'100 hash/verify cycles: {time.time() - start:.2f}s')\"",
        "Password Hashing Performance Tests"
    )
    test_results.append(("Performance Tests", performance_tests))
    
    # 6. Generate test coverage report
    coverage_report = run_command(
        "python -m pytest tests/test_auth.py --cov=auth --cov=routers.auth --cov-report=html --cov-report=term",
        "Test Coverage Report"
    )
    test_results.append(("Coverage Report", coverage_report))
    
    # Print summary
    print(f"\n{'='*60}")
    print("🏁 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} test suites")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All authentication tests passed!")
        print("✅ JWT token generation, validation, and refresh mechanisms working")
        print("✅ Registration, login, and password reset flows working")
        print("✅ Role-based access control working for all permission levels")
        print("✅ Security measures protecting against authentication bypass")
        return 0
    else:
        print(f"\n⚠️  {failed} test suite(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
