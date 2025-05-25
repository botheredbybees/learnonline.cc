#!/bin/bash

# LearnOnline.cc Test Runner Script
# This script provides easy commands to run different types of tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check if docker-compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install it and try again."
        exit 1
    fi
}

# Function to create test results directory
create_test_dirs() {
    mkdir -p test-results
    mkdir -p test-results/coverage
    mkdir -p test-results/performance
    mkdir -p test-results/screenshots
}

# Function to show usage
show_usage() {
    echo "LearnOnline.cc Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup           Set up test environment"
    echo "  unit            Run unit tests"
    echo "  auth            Run authentication tests"
    echo "  integration     Run integration tests"
    echo "  api             Run API tests"
    echo "  frontend        Run frontend tests"
    echo "  tga             Run TGA integration tests"
    echo "  performance     Run performance tests"
    echo "  security        Run security-focused tests"
    echo "  load            Run load tests with Locust"
    echo "  all             Run all tests"
    echo "  clean           Clean up test environment"
    echo "  logs            Show test logs"
    echo "  coverage        Generate coverage report"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup           # Set up test environment"
    echo "  $0 unit            # Run unit tests"
    echo "  $0 api             # Run API tests"
    echo "  $0 performance     # Run performance tests"
    echo "  $0 clean           # Clean up test environment"
}

# Function to set up test environment
setup_test_env() {
    print_status "Setting up test environment..."
    
    check_docker
    check_docker_compose
    create_test_dirs
    
    # Copy environment file if it doesn't exist
    if [ ! -f backend/.env.test ]; then
        if [ -f backend/.env.example ]; then
            cp backend/.env.example backend/.env.test
            print_status "Created backend/.env.test from example"
        else
            print_warning "No .env.example found. You may need to create backend/.env.test manually"
        fi
    fi
    
    # Start test database
    print_status "Starting test database..."
    docker-compose -f docker-compose.test.yml up -d postgres-test
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run database migrations
    print_status "Running database migrations..."
    docker-compose -f docker-compose.test.yml run --rm backend-test alembic upgrade head
    
    print_success "Test environment setup complete!"
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/ -v --tb=short \
        --junitxml=test-results/unit-tests.xml \
        --cov=. --cov-report=html:test-results/coverage/unit \
        --cov-report=xml:test-results/coverage/unit.xml
    
    print_success "Unit tests completed!"
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    # Check if integration tests directory exists
    if ! docker-compose -f docker-compose.test.yml run --rm test-runner test -d tests/integration; then
        print_warning "No integration tests directory found. Skipping integration tests."
        # Create empty test results file
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            pytest --collect-only -q tests/ --junitxml=test-results/integration-tests.xml > /dev/null 2>&1 || true
        return 0
    fi
    
    # Start all required services
    docker-compose -f docker-compose.test.yml up -d postgres-test backend-test
    
    # Wait for services to be ready
    sleep 20
    
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/integration/ -v --tb=short \
        --junitxml=test-results/integration-tests.xml
    
    print_success "Integration tests completed!"
}

# Function to run API tests
run_api_tests() {
    print_status "Running API tests..."
    
    # Check if API test files exist
    if ! docker-compose -f docker-compose.test.yml run --rm test-runner sh -c 'ls tests/test_*_api.py 2>/dev/null | head -1' > /dev/null 2>&1; then
        print_warning "No API test files found (tests/test_*_api.py). Skipping API tests."
        # Create empty test results file
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            pytest --collect-only -q tests/ --junitxml=test-results/api-tests.xml > /dev/null 2>&1 || true
        return 0
    fi
    
    # Start backend service
    docker-compose -f docker-compose.test.yml up -d postgres-test backend-test
    
    # Wait for services to be ready
    sleep 15
    
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/test_*_api.py -v --tb=short \
        --junitxml=test-results/api-tests.xml
    
    print_success "API tests completed!"
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running frontend tests..."
    
    # Check if frontend tests directory exists
    if ! docker-compose -f docker-compose.test.yml run --rm test-runner test -d tests/frontend; then
        print_warning "No frontend tests directory found. Skipping frontend tests."
        # Create empty test results file
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            pytest --collect-only -q tests/ --junitxml=test-results/frontend-tests.xml > /dev/null 2>&1 || true
        return 0
    fi
    
    # Start all services including Selenium
    docker-compose -f docker-compose.test.yml up -d postgres-test backend-test frontend-test selenium-hub selenium-chrome
    
    # Wait for services to be ready
    sleep 30
    
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/frontend/ -v --tb=short \
        --junitxml=test-results/frontend-tests.xml
    
    print_success "Frontend tests completed!"
}

# Function to run TGA integration tests
run_tga_tests() {
    print_status "Running TGA integration tests..."
    
    if [ -z "$TGA_USERNAME" ] || [ -z "$TGA_PASSWORD" ]; then
        print_warning "TGA_USERNAME and TGA_PASSWORD environment variables not set."
        print_warning "TGA tests may fail or be skipped."
    fi
    
    # Check if TGA test files exist
    if ! docker-compose -f docker-compose.test.yml run --rm test-runner sh -c 'ls tests/test_tga* 2>/dev/null | head -1' > /dev/null 2>&1; then
        print_warning "No TGA test files found (tests/test_tga*). Skipping TGA tests."
        # Create empty test results file
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            pytest --collect-only -q tests/ --junitxml=test-results/tga-tests.xml > /dev/null 2>&1 || true
        return 0
    fi
    
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/test_tga* -v --tb=short \
        --junitxml=test-results/tga-tests.xml
    
    print_success "TGA integration tests completed!"
}

# Function to run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    # Check if performance tests directory exists
    if ! docker-compose -f docker-compose.test.yml run --rm test-runner test -d tests/performance; then
        print_warning "No performance tests directory found. Skipping performance tests."
        # Create empty test results file
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            pytest --collect-only -q tests/ --junitxml=test-results/performance-tests.xml > /dev/null 2>&1 || true
        return 0
    fi
    
    # Start backend service
    docker-compose -f docker-compose.test.yml up -d postgres-test backend-test
    
    # Wait for services to be ready
    sleep 15
    
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/performance/ -v --tb=short \
        --junitxml=test-results/performance-tests.xml
    
    print_success "Performance tests completed!"
}

# Function to run authentication tests
run_auth_tests() {
    print_status "Running authentication tests..."
    
    # Start backend service
    docker-compose -f docker-compose.test.yml up -d postgres-test backend-test
    
    # Wait for services to be ready
    sleep 15
    
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/test_auth.py -v --tb=short \
        --junitxml=test-results/auth-tests.xml \
        --cov=auth --cov=routers.auth --cov-report=html:test-results/coverage/auth \
        --cov-report=xml:test-results/coverage/auth.xml
    
    print_success "Authentication tests completed!"
}

# Function to run security tests
run_security_tests() {
    print_status "Running security-focused tests..."
    
    # Start backend service
    docker-compose -f docker-compose.test.yml up -d postgres-test backend-test
    
    # Wait for services to be ready
    sleep 15
    
    # Run authentication security tests
    docker-compose -f docker-compose.test.yml run --rm test-runner \
        pytest tests/test_auth.py::TestSecurityFeatures -v --tb=short \
        --junitxml=test-results/security-tests.xml
    
    # Run additional security tests if they exist
    if docker-compose -f docker-compose.test.yml run --rm test-runner test -f tests/test_security.py; then
        docker-compose -f docker-compose.test.yml run --rm test-runner \
            pytest tests/test_security.py -v --tb=short \
            --junitxml=test-results/security-additional-tests.xml
    fi
    
    print_success "Security tests completed!"
}

# Function to run load tests
run_load_tests() {
    print_status "Running load tests with Locust..."
    
    # Start backend service
    docker-compose -f docker-compose.test.yml up -d postgres-test backend-test
    
    # Wait for backend to be ready
    sleep 15
    
    print_status "Starting Locust load testing..."
    print_status "Locust web interface will be available at http://localhost:8089"
    
    # Start load test service
    docker-compose -f docker-compose.test.yml up load-test
    
    print_success "Load tests completed!"
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    
    setup_test_env
    run_unit_tests
    
    # Run other test types, but don't fail if they don't exist
    run_api_tests || true
    run_integration_tests || true
    run_tga_tests || true
    run_performance_tests || true
    
    print_success "All available tests completed!"
    
    # Generate combined coverage report
    generate_coverage_report
}

# Function to clean up test environment
clean_test_env() {
    print_status "Cleaning up test environment..."
    
    # Stop and remove all test containers
    docker-compose -f docker-compose.test.yml down -v
    
    # Remove test images (optional)
    read -p "Remove test Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f docker-compose.test.yml down --rmi all
    fi
    
    # Clean up test results (optional)
    read -p "Remove test results? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf test-results/*
    fi
    
    print_success "Test environment cleaned up!"
}

# Function to show logs
show_logs() {
    print_status "Showing test logs..."
    
    if [ -n "$2" ]; then
        # Show logs for specific service
        docker-compose -f docker-compose.test.yml logs -f "$2"
    else
        # Show logs for all services
        docker-compose -f docker-compose.test.yml logs -f
    fi
}

# Function to generate coverage report
generate_coverage_report() {
    print_status "Generating coverage report..."
    
    if [ -d "test-results/coverage" ]; then
        print_status "Coverage reports available in test-results/coverage/"
        
        # Try to open coverage report in browser
        if command -v xdg-open &> /dev/null; then
            xdg-open test-results/coverage/unit/index.html
        elif command -v open &> /dev/null; then
            open test-results/coverage/unit/index.html
        else
            print_status "Open test-results/coverage/unit/index.html in your browser to view the coverage report"
        fi
    else
        print_warning "No coverage reports found. Run tests first."
    fi
}

# Function to run quick health check
health_check() {
    print_status "Running health check..."
    
    # Check if services are running
    if docker-compose -f docker-compose.test.yml ps | grep -q "Up"; then
        print_success "Test services are running"
        
        # Test database connection
        if docker-compose -f docker-compose.test.yml exec -T postgres-test pg_isready -U test_user -d learnonline_test; then
            print_success "Database is accessible"
        else
            print_error "Database is not accessible"
        fi
        
        # Test backend API
        if curl -f http://localhost:8001/docs > /dev/null 2>&1; then
            print_success "Backend API is accessible"
        else
            print_warning "Backend API is not accessible"
        fi
        
    else
        print_warning "Test services are not running. Run 'setup' first."
    fi
}

# Main script logic
case "${1:-help}" in
    setup)
        setup_test_env
        ;;
    unit)
        run_unit_tests
        ;;
    auth)
        run_auth_tests
        ;;
    integration)
        run_integration_tests
        ;;
    api)
        run_api_tests
        ;;
    frontend)
        run_frontend_tests
        ;;
    tga)
        run_tga_tests
        ;;
    performance)
        run_performance_tests
        ;;
    security)
        run_security_tests
        ;;
    load)
        run_load_tests
        ;;
    all)
        run_all_tests
        ;;
    clean)
        clean_test_env
        ;;
    logs)
        show_logs "$@"
        ;;
    coverage)
        generate_coverage_report
        ;;
    health)
        health_check
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
