"""Tests for host-related endpoints."""
import pytest
from fastapi import status

from tests.test_utils import assert_error_response, create_test_host


def test_create_host_success(client):
    """Test creating a host with valid data."""
    # Arrange
    host_data = {"hostname": "example.com", "description": "Test host"}
    
    # Act
    response = client.post("/api/hosts/", json=host_data)
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["hostname"] == "example.com"
    assert data["description"] == "Test host"
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_host(client):
    """Test creating a duplicate host fails."""
    # Arrange
    create_test_host(client, "example.com")
    
    # Act
    response = client.post("/api/hosts/", json={"hostname": "example.com"})
    
    # Assert
    assert_error_response(
        response,
        status_code=status.HTTP_409_CONFLICT,
        error_code="HOST_EXISTS",
        message="Hostname 'example.com' already exists"
    )


def test_create_host_invalid_hostname(client):
    """Test creating a host with an invalid hostname."""
    # Arrange & Act
    response = client.post("/api/hosts/", json={"hostname": "invalid hostname!"})
    
    # Assert
    assert_error_response(
        response,
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="INVALID_HOSTNAME",
        message="Invalid hostname format"
    )


def test_list_hosts_empty(client):
    """Test listing hosts when none exist."""
    # Act
    response = client.get("/api/hosts/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_hosts_with_data(client):
    """Test listing hosts with data."""
    # Arrange
    host1 = create_test_host(client, "example1.com", "First host")
    host2 = create_test_host(client, "example2.com", "Second host")
    
    # Act
    response = client.get("/api/hosts/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    hosts = response.json()
    assert len(hosts) == 2
    assert hosts[0]["hostname"] in ["example1.com", "example2.com"]
    assert hosts[1]["hostname"] in ["example1.com", "example2.com"]
    assert hosts[0]["hostname"] != hosts[1]["hostname"]


def test_get_host_not_found(client):
    """Test getting a non-existent host."""
    # Act
    response = client.get("/api/hosts/999")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    error = response.json()["error"]
    assert "not found" in error["message"].lower()


def test_get_host_success(client):
    """Test getting an existing host."""
    # Arrange
    created_host = create_test_host(client, "example.com", "Test host")
    
    # Act
    response = client.get(f"/api/hosts/{created_host['id']}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    host = response.json()
    assert host["id"] == created_host["id"]
    assert host["hostname"] == "example.com"
    assert host["description"] == "Test host"
    assert "created_at" in host
