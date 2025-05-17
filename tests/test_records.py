"""Tests for record-related endpoints."""
import pytest
from fastapi import status

from app.models import RecordType
from tests.test_utils import (
    assert_error_response,
    create_test_host,
    create_test_record,
)


def test_create_record_success(client):
    """Test creating a record with valid data."""
    # Arrange
    host = create_test_host(client, "example.com")
    record_data = {
        "type": "A",
        "value": "192.168.1.1",
        "ttl": 300,
        "host_id": host["id"]
    }
    
    # Act
    response = client.post("/api/records/", json=record_data)
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["type"] == "A"
    assert data["value"] == "192.168.1.1"
    assert data["ttl"] == 300
    assert data["host_id"] == host["id"]
    assert "id" in data
    assert "created_at" in data


def test_create_mx_record_with_priority(client):
    """Test creating an MX record with priority."""
    # Arrange
    host = create_test_host(client, "example.com")
    
    # Act
    response = client.post("/api/records/", json={
        "type": "MX",
        "value": "mail.example.com",
        "ttl": 300,
        "priority": 10,
        "host_id": host["id"]
    })
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["type"] == "MX"
    assert data["value"] == "mail.example.com"
    assert data["priority"] == 10


def test_create_mx_record_without_priority(client):
    """Test creating an MX record without priority fails."""
    # Arrange
    host = create_test_host(client, "example.com")
    
    # Act
    response = client.post("/api/records/", json={
        "type": "MX",
        "value": "mail.example.com",
        "ttl": 300,
        "host_id": host["id"]
    })
    
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    error = response.json()
    assert any("field required" in str(e) for e in error.get("detail", []))


def test_create_record_invalid_ipv4(client):
    """Test creating an A record with invalid IPv4."""
    # Arrange
    host = create_test_host(client, "example.com")
    
    # Act
    response = client.post("/api/records/", json={
        "type": "A",
        "value": "not.an.ip",
        "ttl": 300,
        "host_id": host["id"]
    })
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error = response.json()["detail"]
    assert "invalid ipv4 address" in error["message"].lower()


def test_create_cname_record(client):
    """Test creating a CNAME record."""
    # Arrange
    host = create_test_host(client, "www.example.com")
    
    # Act
    response = client.post("/api/records/", json={
        "type": "CNAME",
        "value": "example.com",
        "ttl": 300,
        "host_id": host["id"]
    })
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["type"] == "CNAME"


def test_create_duplicate_record(client):
    """Test creating a duplicate record fails."""
    # Arrange
    host = create_test_host(client, "example.com")
    create_test_record(client, host["id"], "A", "192.168.1.1")
    
    # Act
    response = client.post("/api/records/", json={
        "type": "A",
        "value": "192.168.1.1",
        "ttl": 300,
        "host_id": host["id"]
    })
    
    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT
    error = response.json()["error"]
    assert error["code"] == "RECORD_CONFLICT"
    assert "already exists for this host" in error["message"]


def test_list_records_empty(client):
    """Test listing records when none exist."""
    # Act
    response = client.get("/api/records/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_records_with_data(client):
    """Test listing records with data."""
    # Arrange
    host1 = create_test_host(client, "example1.com")
    host2 = create_test_host(client, "example2.com")
    
    record1 = create_test_record(client, host1["id"], "A", "192.168.1.1")
    record2 = create_test_record(client, host2["id"], "A", "192.168.1.2")
    
    # Act
    response = client.get("/api/records/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    records = response.json()
    assert len(records) == 2
    assert {r["id"] for r in records} == {record1["id"], record2["id"]}


def test_get_record_not_found(client):
    """Test getting a non-existent record."""
    # Act
    response = client.get("/api/records/999")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    error = response.json()
    assert "error" in error
    assert "not found" in error["error"]["message"].lower()


def test_get_record_success(client):
    """Test getting an existing record."""
    # Arrange
    host = create_test_host(client, "example.com")
    created_record = create_test_record(client, host["id"], "A", "192.168.1.1")
    
    # Act
    response = client.get(f"/api/records/{created_record['id']}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    record = response.json()
    assert record["id"] == created_record["id"]
    assert record["type"] == "A"
    assert record["value"] == "192.168.1.1"
    assert record["host_id"] == host["id"]
    assert "created_at" in record
