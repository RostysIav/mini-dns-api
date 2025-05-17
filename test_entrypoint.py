"""Test script to verify FastAPI entry point functionality."""
import sys
import json
import requests
from pathlib import Path

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_header(text):
    """Print a formatted header."""
    print(f"\n{'='*50}")
    print(f" {text}".upper())
    print(f"{'='*50}")

def test_health_check():
    """Test the health check endpoint."""
    print_header("Testing Health Check")
    url = f"{BASE_URL}/health"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print("Response:", json.dumps(response.json(), indent=2))
        
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print_header("Testing Root Endpoint")
    url = f"{BASE_URL}/"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print("Response:", json.dumps(data, indent=2))
        
        required_fields = ["name", "version", "docs", "environment"]
        if all(field in data for field in required_fields):
            print("✅ Root endpoint test passed")
            return True
        else:
            missing = [f for f in required_fields if f not in data]
            print(f"❌ Missing fields: {', '.join(missing)}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_docs_endpoints():
    """Test that API documentation is available."""
    print_header("Testing Documentation Endpoints")
    
    endpoints = [
        ("/docs", "Swagger UI"),
        ("/redoc", "ReDoc")
    ]
    
    all_passed = True
    
    for endpoint, name in endpoints:
        url = f"{BASE_URL}{endpoint}"
        print(f"GET {url} ({name})")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200 and "text/html" in response.headers.get("content-type", ""):
                print(f"✅ {name} is available")
            else:
                print(f"❌ {name} is not available")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error accessing {name}: {str(e)}")
            all_passed = False
    
    return all_passed

def test_database_connection():
    """Test that the database connection is working."""
    print_header("Testing Database Connection")
    url = f"{BASE_URL}/status"
    print(f"GET {url}")
    
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print("Response:", json.dumps(data, indent=2))
        
        if data.get("database") == "connected":
            print("✅ Database connection test passed")
            return True
        else:
            print(f"❌ Database connection failed: {data.get('database')}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_tests():
    """Run all tests and return the results."""
    print("="*50)
    print(" STARTING FASTAPI ENTRY POINT TESTS ".center(50, "="))
    print("="*50)
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Documentation Endpoints", test_docs_endpoints),
        ("Database Connection", test_database_connection)
    ]
    
    results = {}
    
    for name, test_func in tests:
        print(f"\n{' TESTING: ' + name + ' ':-^50}")
        results[name] = test_func()
    
    # Print summary
    print_header("TEST SUMMARY")
    
    all_passed = True
    for name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
    
    return all_passed

if __name__ == "__main__":
    run_tests()
