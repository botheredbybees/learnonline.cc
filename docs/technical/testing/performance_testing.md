# Performance Testing Guide

This document provides comprehensive guidelines for performance testing the LearnOnline.cc application, including load testing, stress testing, and performance optimization strategies.

## Table of Contents

1. [Overview](#overview)
2. [Performance Testing Tools](#performance-testing-tools)
3. [Load Testing](#load-testing)
4. [Stress Testing](#stress-testing)
5. [Database Performance Testing](#database-performance-testing)
6. [Frontend Performance Testing](#frontend-performance-testing)
7. [API Performance Testing](#api-performance-testing)
8. [TGA Integration Performance](#tga-integration-performance)
9. [Performance Monitoring](#performance-monitoring)
10. [Performance Optimization](#performance-optimization)

## Overview

Performance testing ensures the LearnOnline.cc application can handle expected user loads while maintaining acceptable response times and resource utilization.

### Performance Goals

- **Response Time**: API endpoints should respond within 2 seconds under normal load
- **Throughput**: Support 100 concurrent users with minimal degradation
- **Database**: Query response times under 500ms for most operations
- **Frontend**: Page load times under 3 seconds on standard connections
- **TGA Integration**: External API calls should complete within 10 seconds

## Performance Testing Tools

### Load Testing Tools

```bash
# Install performance testing tools
pip install locust pytest-benchmark

# Install Apache Bench (if not available)
sudo apt-get install apache2-utils

# Install wrk (modern HTTP benchmarking tool)
git clone https://github.com/wg/wrk.git
cd wrk && make && sudo cp wrk /usr/local/bin/
```

### Monitoring Tools

```bash
# System monitoring
sudo apt-get install htop iotop nethogs

# Database monitoring
sudo apt-get install postgresql-contrib

# Application monitoring
pip install psutil memory-profiler
```

## Load Testing

### Locust Load Testing

Create a comprehensive load testing suite:

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random
import json

class LearnOnlineUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Login when user starts."""
        self.login()
    
    def login(self):
        """Authenticate user."""
        response = self.client.post("/api/auth/login", data={
            "username": f"testuser{random.randint(1, 100)}@example.com",
            "password": "testpassword"
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                self.client.headers.update({
                    "Authorization": f"Bearer {token}"
                })
    
    @task(3)
    def browse_units(self):
        """Browse units list - most common action."""
        self.client.get("/api/units/", params={
            "page": random.randint(1, 5),
            "size": random.choice([10, 20, 50])
        })
    
    @task(2)
    def search_units(self):
        """Search for units."""
        search_terms = ["ICT", "BSB", "CHC", "SIT", "AUR"]
        self.client.get("/api/units/search", params={
            "query": random.choice(search_terms),
            "source": "local"
        })
    
    @task(1)
    def view_unit_details(self):
        """View specific unit details."""
        # Get a random unit first
        response = self.client.get("/api/units/", params={"size": 1})
        if response.status_code == 200:
            units = response.json().get("items", [])
            if units:
                unit_id = units[0]["id"]
                self.client.get(f"/api/units/{unit_id}")
                
                # Also get elements with performance criteria
                self.client.get(f"/api/units/{unit_id}/elements-with-pc")
    
    @task(1)
    def view_achievements(self):
        """View achievements."""
        self.client.get("/api/achievements/")
    
    @task(1)
    def view_user_profile(self):
        """View user profile."""
        self.client.get("/api/auth/me")

class AdminUser(HttpUser):
    wait_time = between(2, 5)
    weight = 1  # Lower weight - fewer admin users
    
    def on_start(self):
        """Login as admin."""
        response = self.client.post("/api/auth/login", data={
            "username": "admin@example.com",
            "password": "adminpassword"
        })
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                self.client.headers.update({
                    "Authorization": f"Bearer {token}"
                })
    
    @task(1)
    def sync_unit(self):
        """Sync unit from TGA - admin only."""
        unit_codes = ["ICTICT214", "BSBWHS211", "CHCCOM005"]
        code = random.choice(unit_codes)
        self.client.post(f"/api/units/{code}/sync")
    
    @task(2)
    def manage_users(self):
        """View user management."""
        self.client.get("/api/users/")
```

### Running Load Tests

```bash
# Basic load test
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# Headless load test
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 300s \
  --headless

# Load test with specific user distribution
locust -f tests/performance/locustfile.py \
  --host=http://localhost:8000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 600s \
  --headless \
  --csv=results/load_test
```

### Apache Bench Testing

```bash
# Test units endpoint
ab -n 1000 -c 10 http://localhost:8000/api/units/

# Test with authentication
ab -n 500 -c 5 -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/auth/me

# Test POST endpoint
ab -n 100 -c 5 -p login_data.txt -T application/x-www-form-urlencoded \
  http://localhost:8000/api/auth/login
```

### wrk Testing

```bash
# Basic load test
wrk -t12 -c400 -d30s http://localhost:8000/api/units/

# Test with custom script
wrk -t12 -c400 -d30s -s tests/performance/wrk_script.lua \
  http://localhost:8000/api/units/
```

```lua
-- tests/performance/wrk_script.lua
wrk.method = "GET"
wrk.headers["Content-Type"] = "application/json"

request = function()
   local paths = {"/api/units/", "/api/achievements/", "/api/badges/"}
   local path = paths[math.random(#paths)]
   return wrk.format(nil, path)
end
```

## Stress Testing

### Gradual Load Increase

```python
# tests/performance/stress_test.py
import requests
import time
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

class StressTest:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def make_request(self, endpoint="/api/units/"):
        """Make a single request and measure response time."""
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code == 200
            }
        except Exception as e:
            end_time = time.time()
            return {
                "status_code": 0,
                "response_time": end_time - start_time,
                "success": False,
                "error": str(e)
            }
    
    def run_concurrent_requests(self, num_requests, num_threads):
        """Run concurrent requests and collect results."""
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(self.make_request) 
                for _ in range(num_requests)
            ]
            
            results = []
            for future in as_completed(futures):
                results.append(future.result())
            
            return results
    
    def analyze_results(self, results):
        """Analyze performance results."""
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        
        analysis = {
            "total_requests": len(results),
            "successful_requests": success_count,
            "success_rate": success_count / len(results) * 100,
            "avg_response_time": statistics.mean(response_times),
            "median_response_time": statistics.median(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": statistics.quantiles(response_times, n=20)[18],
            "p99_response_time": statistics.quantiles(response_times, n=100)[98]
        }
        
        return analysis
    
    def run_stress_test(self):
        """Run progressive stress test."""
        test_scenarios = [
            (50, 5),    # 50 requests, 5 threads
            (100, 10),  # 100 requests, 10 threads
            (200, 20),  # 200 requests, 20 threads
            (500, 50),  # 500 requests, 50 threads
            (1000, 100) # 1000 requests, 100 threads
        ]
        
        for num_requests, num_threads in test_scenarios:
            print(f"\nTesting {num_requests} requests with {num_threads} threads...")
            
            results = self.run_concurrent_requests(num_requests, num_threads)
            analysis = self.analyze_results(results)
            
            print(f"Success Rate: {analysis['success_rate']:.2f}%")
            print(f"Average Response Time: {analysis['avg_response_time']:.3f}s")
            print(f"95th Percentile: {analysis['p95_response_time']:.3f}s")
            print(f"99th Percentile: {analysis['p99_response_time']:.3f}s")
            
            # Stop if success rate drops below 95%
            if analysis['success_rate'] < 95:
                print("⚠️  Success rate dropped below 95%, stopping stress test")
                break
            
            # Wait between test scenarios
            time.sleep(5)

if __name__ == "__main__":
    stress_test = StressTest()
    stress_test.run_stress_test()
```

### Memory Leak Detection

```python
# tests/performance/memory_test.py
import psutil
import requests
import time
import gc

def monitor_memory_usage(duration=300, interval=5):
    """Monitor memory usage over time."""
    process = psutil.Process()
    memory_usage = []
    
    start_time = time.time()
    while time.time() - start_time < duration:
        memory_info = process.memory_info()
        memory_usage.append({
            "timestamp": time.time(),
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024   # MB
        })
        
        # Make some requests to simulate load
        try:
            requests.get("http://localhost:8000/api/units/")
        except:
            pass
        
        time.sleep(interval)
    
    return memory_usage

def detect_memory_leaks(memory_usage):
    """Detect potential memory leaks."""
    if len(memory_usage) < 10:
        return False
    
    # Check if memory usage is consistently increasing
    rss_values = [m["rss"] for m in memory_usage]
    
    # Simple trend detection
    first_half = rss_values[:len(rss_values)//2]
    second_half = rss_values[len(rss_values)//2:]
    
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    
    # If memory usage increased by more than 20%
    if avg_second > avg_first * 1.2:
        return True
    
    return False
```

## Database Performance Testing

### Query Performance Testing

```python
# tests/performance/db_performance.py
import time
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class DatabasePerformanceTest:
    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def time_query(self, query, params=None):
        """Time a database query."""
        session = self.Session()
        try:
            start_time = time.time()
            result = session.execute(text(query), params or {})
            rows = result.fetchall()
            end_time = time.time()
            
            return {
                "query_time": end_time - start_time,
                "row_count": len(rows)
            }
        finally:
            session.close()
    
    def test_common_queries(self):
        """Test performance of common queries."""
        queries = {
            "list_units": "SELECT * FROM units LIMIT 50",
            "search_units": "SELECT * FROM units WHERE title ILIKE '%ICT%' LIMIT 20",
            "unit_with_elements": """
                SELECT u.*, e.* FROM units u 
                LEFT JOIN elements e ON u.id = e.unit_id 
                WHERE u.code = :code
            """,
            "user_progress": """
                SELECT u.*, up.* FROM users u 
                LEFT JOIN user_progress up ON u.id = up.user_id 
                WHERE u.id = :user_id
            """,
            "achievements_count": "SELECT COUNT(*) FROM user_achievements WHERE user_id = :user_id"
        }
        
        results = {}
        for query_name, query in queries.items():
            params = {}
            if "code" in query:
                params["code"] = "ICTICT214"
            if "user_id" in query:
                params["user_id"] = 1
            
            try:
                result = self.time_query(query, params)
                results[query_name] = result
                print(f"{query_name}: {result['query_time']:.3f}s ({result['row_count']} rows)")
            except Exception as e:
                print(f"{query_name}: ERROR - {e}")
        
        return results
    
    def test_index_performance(self):
        """Test index effectiveness."""
        # Test queries with and without indexes
        queries = [
            ("units_by_code", "SELECT * FROM units WHERE code = 'ICTICT214'"),
            ("units_by_title", "SELECT * FROM units WHERE title ILIKE '%software%'"),
            ("elements_by_unit", "SELECT * FROM elements WHERE unit_id = 1"),
            ("user_by_email", "SELECT * FROM users WHERE email = 'test@example.com'")
        ]
        
        for query_name, query in queries:
            result = self.time_query(query)
            print(f"{query_name}: {result['query_time']:.3f}s")
            
            # Queries should be fast with proper indexes
            if result['query_time'] > 0.1:  # 100ms threshold
                print(f"⚠️  {query_name} is slow, check indexes")

# Run database performance tests
if __name__ == "__main__":
    db_test = DatabasePerformanceTest("postgresql://user:pass@localhost/learnonline")
    db_test.test_common_queries()
    db_test.test_index_performance()
```

### Connection Pool Testing

```python
# tests/performance/connection_pool_test.py
import time
import threading
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

def test_connection_pool_performance():
    """Test database connection pool performance."""
    # Create engine with connection pool
    engine = create_engine(
        "postgresql://user:pass@localhost/learnonline",
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
    
    def worker():
        """Worker function to test connections."""
        for i in range(10):
            start_time = time.time()
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                result.fetchone()
            end_time = time.time()
            print(f"Connection time: {end_time - start_time:.3f}s")
    
    # Test with multiple threads
    threads = []
    for i in range(20):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
```

## Frontend Performance Testing

### Page Load Performance

```python
# tests/performance/frontend_performance.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

class FrontendPerformanceTest:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def measure_page_load(self, url):
        """Measure page load performance."""
        start_time = time.time()
        self.driver.get(url)
        
        # Wait for page to be fully loaded
        self.driver.execute_script("return document.readyState") == "complete"
        
        end_time = time.time()
        
        # Get performance metrics
        performance_data = self.driver.execute_script("""
            return {
                loadEventEnd: performance.timing.loadEventEnd,
                navigationStart: performance.timing.navigationStart,
                domContentLoadedEventEnd: performance.timing.domContentLoadedEventEnd,
                responseEnd: performance.timing.responseEnd
            };
        """)
        
        navigation_start = performance_data["navigationStart"]
        
        metrics = {
            "total_load_time": end_time - start_time,
            "dom_content_loaded": (performance_data["domContentLoadedEventEnd"] - navigation_start) / 1000,
            "page_load_complete": (performance_data["loadEventEnd"] - navigation_start) / 1000,
            "response_time": (performance_data["responseEnd"] - navigation_start) / 1000
        }
        
        return metrics
    
    def test_page_performance(self):
        """Test performance of key pages."""
        pages = {
            "home": "http://localhost:8080/",
            "units": "http://localhost:8080/units",
            "login": "http://localhost:8080/login"
        }
        
        results = {}
        for page_name, url in pages.items():
            try:
                metrics = self.measure_page_load(url)
                results[page_name] = metrics
                
                print(f"{page_name}:")
                print(f"  Total Load Time: {metrics['total_load_time']:.2f}s")
                print(f"  DOM Content Loaded: {metrics['dom_content_loaded']:.2f}s")
                print(f"  Page Load Complete: {metrics['page_load_complete']:.2f}s")
                print()
                
                # Check performance thresholds
                if metrics['total_load_time'] > 3.0:
                    print(f"⚠️  {page_name} load time exceeds 3 seconds")
                
            except Exception as e:
                print(f"Error testing {page_name}: {e}")
        
        return results
    
    def test_javascript_performance(self):
        """Test JavaScript execution performance."""
        self.driver.get("http://localhost:8080/units")
        
        # Test search functionality performance
        search_script = """
            var start = performance.now();
            
            // Simulate search
            var searchInput = document.getElementById('search-query');
            if (searchInput) {
                searchInput.value = 'ICT';
                searchInput.dispatchEvent(new Event('input'));
            }
            
            var end = performance.now();
            return end - start;
        """
        
        search_time = self.driver.execute_script(search_script)
        print(f"Search execution time: {search_time:.2f}ms")
        
        return search_time
    
    def cleanup(self):
        """Clean up resources."""
        self.driver.quit()

# Run frontend performance tests
if __name__ == "__main__":
    test = FrontendPerformanceTest()
    try:
        test.test_page_performance()
        test.test_javascript_performance()
    finally:
        test.cleanup()
```

### Lighthouse Performance Testing

```bash
# Install Lighthouse CLI
npm install -g lighthouse

# Run Lighthouse performance audit
lighthouse http://localhost:8080 \
  --output json \
  --output-path ./results/lighthouse-report.json \
  --chrome-flags="--headless"

# Run Lighthouse for specific pages
lighthouse http://localhost:8080/units \
  --output html \
  --output-path ./results/units-performance.html
```

## API Performance Testing

### Benchmark API Endpoints

```python
# tests/performance/api_benchmark.py
import pytest
import time
import statistics
from fastapi.testclient import TestClient
from main import app

class APIBenchmark:
    def __init__(self):
        self.client = TestClient(app)
        self.auth_headers = self.get_auth_headers()
    
    def get_auth_headers(self):
        """Get authentication headers."""
        response = self.client.post("/api/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        return {}
    
    def benchmark_endpoint(self, method, endpoint, iterations=100, **kwargs):
        """Benchmark an API endpoint."""
        response_times = []
        
        for _ in range(iterations):
            start_time = time.time()
            
            if method.upper() == "GET":
                response = self.client.get(endpoint, **kwargs)
            elif method.upper() == "POST":
                response = self.client.post(endpoint, **kwargs)
            
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        if not response_times:
            return None
        
        return {
            "endpoint": endpoint,
            "iterations": len(response_times),
            "avg_time": statistics.mean(response_times),
            "median_time": statistics.median(response_times),
            "min_time": min(response_times),
            "max_time": max(response_times),
            "p95_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
        }
    
    def run_benchmarks(self):
        """Run benchmarks for key endpoints."""
        endpoints = [
            ("GET", "/api/units/"),
            ("GET", "/api/units/search", {"params": {"query": "ICT"}}),
            ("GET", "/api/achievements/"),
            ("GET", "/api/auth/me", {"headers": self.auth_headers}),
        ]
        
        results = []
        for method, endpoint, kwargs in endpoints:
            print(f"Benchmarking {method} {endpoint}...")
            result = self.benchmark_endpoint(method, endpoint, **kwargs)
            
            if result:
                results.append(result)
                print(f"  Average: {result['avg_time']:.3f}s")
                print(f"  95th percentile: {result['p95_time']:.3f}s")
                print(f"  Min/Max: {result['min_time']:.3f}s / {result['max_time']:.3f}s")
                print()
        
        return results

# Pytest benchmark integration
@pytest.mark.benchmark
def test_units_list_performance(benchmark):
    """Benchmark units list endpoint."""
    client = TestClient(app)
    
    def get_units():
        response = client.get("/api/units/")
        assert response.status_code == 200
        return response
    
    result = benchmark(get_units)
    
    # Assert performance requirements
    assert result.stats.mean < 2.0  # Average response time under 2 seconds

@pytest.mark.benchmark
def test_search_performance(benchmark):
    """Benchmark search endpoint."""
    client = TestClient(app)
    
    def search_units():
        response = client.get("/api/units/search?query=ICT")
        assert response.status_code == 200
        return response
    
    result = benchmark(search_units)
    assert result.stats.mean < 3.0  # Search should complete within 3 seconds
```

## TGA Integration Performance

### TGA API Performance Testing

```python
# tests/performance/tga_performance.py
import time
import asyncio
from backend.services.tga.client import TrainingGovClient
import os

class TGAPerformanceTest:
    def __init__(self):
        self.client = TrainingGovClient(
            username=os.getenv('TGA_USERNAME'),
            password=os.getenv('TGA_PASSWORD')
        )
    
    def test_search_performance(self):
        """Test TGA search performance."""
        search_terms = ["ICT", "BSB", "CHC", "SIT", "AUR"]
        results = []
        
        for term in search_terms:
            start_time = time.time()
            try:
                result = self.client.search_components(
                    filter_text=term,
                    page_size=20
                )
                end_time = time.time()
                
                results.append({
                    "term": term,
                    "response_time": end_time - start_time,
                    "component_count": len(result.get("components", [])),
                    "success": True
                })
                
            except Exception as e:
                end_time = time.time()
                results.append({
                    "term": term,
                    "response_time": end_time - start_time,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    def test_xml_retrieval_performance(self):
        """Test XML retrieval performance."""
        unit_codes = ["ICTICT214", "BSBWHS211", "CHCCOM005"]
        results = []
        
        for code in unit_codes:
            start_time = time.time()
            try:
                xml_data = self.client.get_component_xml(code)
                end_time = time.time()
                
                results.append({
                    "code": code,
                    "response_time": end_time - start_time,
                    "xml_size": len(xml_data.get("xml", "")),
                    "success": True
                })
                
            except Exception as e:
                end_time = time.time()
                results.append({
                    "code": code,
                    "response_time": end_time - start_time,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def test_concurrent_tga_requests(self):
        """Test concurrent TGA requests."""
        async def make_search_request(term):
            start_time = time.time()
            try:
                result = self.client.search_components(filter_text=term, page_size=5)
                end_time = time.time()
                return {
                    "term": term,
                    "response_time": end_time - start_time,
                    "success": True
                }
            except Exception as e:
                end_time = time.time()
                return {
                    "term": term,
                    "response_time": end_time - start_time,
                    "error": str(e),
                    "success": False
                }
        
        search_terms = ["ICT", "BSB", "CHC", "SIT", "AUR"] * 3  # 15 concurrent requests
        
        start_time = time.time()
        results = await asyncio.gather(*[
            make_search_request(term) for term in search_terms
        ])
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_requests = sum(1 for r in results if r["success"])
        
        return {
            "total_time": total_time,
            "total_requests": len(results),
            "successful_requests": successful_requests,
            "success_rate": successful_requests / len(results) * 100,
            "avg_response_time": sum(r["response_time"] for r in results) / len(results),
            "results": results
        }
```

## Performance Monitoring

### Application Performance Monitoring

```python
# backend/monitoring/performance_monitor.py
import time
import psutil
import logging
from functools import wraps
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)
    
    def monitor_endpoint(self, endpoint_name: str):
        """Decorator to monitor endpoint performance."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    
                    metrics = {
                        "endpoint": endpoint_name,
                        "response_time": end_time - start_time,
                        "memory_used": end_memory - start_memory,
                        "success": success,
                        "timestamp": time.time()
                    }
                    
                    if error:
                        metrics["error"] = error
                    
                    self.record_metrics(metrics)
                
                return result
            return wrapper
        return decorator
    
    def record_metrics(self, metrics: Dict[str, Any]):
        """Record performance metrics."""
        endpoint = metrics["endpoint"]
        
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        
        self.metrics[endpoint].append(metrics)
        
        # Log slow
