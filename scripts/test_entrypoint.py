"""Test script to verify FastAPI entry point functionality."""
import sys
import asyncio
import httpx
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add parent directory to path to allow importing app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.core.database import init_db, drop_all_tables

# Test client
client = TestClient(app)

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root_endpoint():
    """Test the root endpoint returns API information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert "environment" in data

def test_docs_endpoints():
    """Test that API documentation is available."""
    # Test Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    # Test ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_nonexistent_endpoint():
    """Test that a non-existent endpoint returns 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404

def test_database_connection():
    """Test that the database connection is working."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "connected"

if __name__ == "__main__":
    # Run tests
    import unittest
    unittest.main()
