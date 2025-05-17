"""Pytest configuration and fixtures."""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_db_session
from app.main import app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create a test database engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Override the database dependency
def override_get_db_session() -> Generator[Session, None, None]:
    """Override the get_db_session dependency for testing."""
    with Session(test_engine) as session:
        yield session

# Apply the override
app.dependency_overrides[get_db_session] = override_get_db_session

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a database session for testing."""
    # Create all tables
    SQLModel.metadata.create_all(test_engine)
    
    # Start a transaction
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    # Rollback the transaction and close the session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    # Override the database session dependency
    def override_get_db() -> Generator[Session, None, None]:
        yield db
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def sample_host_data():
    """Return sample host data for testing."""
    return {
        "hostname": "example.com",
        "description": "Test host"
    }

@pytest.fixture(scope="function")
def sample_record_data():
    """Return sample record data for testing."""
    return {
        "type": "A",
        "value": "192.168.1.1",
        "ttl": 300,
        "priority": None,
        "host_id": 1  # Will be set by the test
    }
