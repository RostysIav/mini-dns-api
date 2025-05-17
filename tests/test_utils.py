"""Test utilities for the Mini DNS API."""
from typing import Any, Dict, Optional, Union, List

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import Record, RecordType, Host

def assert_error_response(
    response: Any,
    status_code: int,
    error_code: Optional[str] = None,
    message: Optional[Union[str, List[str]]] = None,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """Assert that a response contains the expected error.
    
    Args:
        response: The test client response
        status_code: Expected HTTP status code
        error_code: Expected error code (optional)
        message: Expected error message or list of possible messages (optional)
        details: Optional expected error details
    """
    assert response.status_code == status_code
    
    # Handle different response formats
    content = response.json()
    if "detail" in content:
        error = content["detail"]
    elif "error" in content:
        error = content["error"]
    else:
        error = content
    
    # Check error code if provided
    if error_code is not None:
        if isinstance(error, dict) and "code" in error:
            assert error["code"] == error_code, f"Expected error code '{error_code}', got '{error.get('code')}'"
    
    # Check message if provided
    if message is not None:
        error_message = error.get("message", str(error)) if isinstance(error, dict) else str(error)
        if isinstance(message, list):
            assert any(m in error_message for m in message), \
                f"None of {message} found in error message: {error_message}"
        else:
            assert message in error_message, f"'{message}' not found in error message: {error_message}"
    
    # Check details if provided
    if details and isinstance(error, dict):
        for key, value in details.items():
            assert key in error, f"Key '{key}' not found in error"
            assert error[key] == value, f"Expected {key}={value}, got {key}={error[key]}"

def create_test_host(
    client: TestClient, 
    hostname: str = "example.com", 
    description: str = "Test host"
) -> Dict[str, Any]:
    """Create a test host via the API.
    
    Args:
        client: Test client
        hostname: Hostname for the test host
        description: Description for the test host
        
    Returns:
        The created host data
    """
    response = client.post(
        "/api/hosts/",
        json={"hostname": hostname, "description": description}
    )
    assert response.status_code == 201
    return response.json()

def create_test_record(
    client: TestClient,
    host_id: int,
    record_type: str = "A",
    value: str = "192.168.1.1",
    ttl: int = 300,
    priority: Optional[int] = None
) -> Dict[str, Any]:
    """Create a test record via the API.
    
    Args:
        client: Test client
        host_id: ID of the host to add the record to
        record_type: Type of DNS record
        value: Record value
        ttl: TTL in seconds
        priority: Priority for MX records
        
    Returns:
        The created record data
    """
    record_data = {
        "type": record_type,
        "value": value,
        "ttl": ttl,
        "host_id": host_id,
    }
    
    if priority is not None:
        record_data["priority"] = priority
    
    response = client.post("/api/records/", json=record_data)
    assert response.status_code == 201
    return response.json()
