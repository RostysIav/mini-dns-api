"""Tests for DNS resolution and CNAME chain endpoints."""
import pytest
from fastapi import status

from app.models import RecordType
from tests.test_utils import (
    assert_error_response,
    create_test_host,
    create_test_record,
)


def test_resolve_hostname_a_record(client):
    """Test resolving a hostname with an A record."""
    # Arrange
    host = create_test_host(client, "example.com")
    create_test_record(client, host["id"], "A", "192.168.1.1")
    
    # Act
    response = client.get("/api/resolve/example.com")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["hostname"] == "example.com"
    assert len(data["records"]) == 1
    assert data["records"][0]["type"] == "A"
    assert data["records"][0]["value"] == "192.168.1.1"


def test_resolve_hostname_cname_chain(client):
    """Test resolving a hostname with a CNAME chain."""
    # Arrange
    # Create hosts
    host1 = create_test_host(client, "www.example.com")
    host2 = create_test_host(client, "example.com")
    
    # Create records
    create_test_record(client, host1["id"], "CNAME", "example.com")
    create_test_record(client, host2["id"], "A", "192.168.1.1")
    
    # Act
    response = client.get("/api/resolve/www.example.com")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["hostname"] == "www.example.com"
    assert len(data["records"]) == 1
    assert data["records"][0]["type"] == "A"
    assert data["records"][0]["value"] == "192.168.1.1"
    assert data["canonical_name"] == "example.com"


def test_resolve_nonexistent_hostname(client):
    """Test resolving a non-existent hostname."""
    # Act
    response = client.get("/api/resolve/nonexistent.example.com")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    error = response.json()["detail"]
    assert "not found" in error["message"].lower()


def test_resolve_with_record_type_filter(client):
    """Test resolving with a record type filter."""
    # Arrange
    host = create_test_host(client, "example.com")
    create_test_record(client, host["id"], "A", "192.168.1.1")
    create_test_record(client, host["id"], "AAAA", "2001:db8::1")
    
    # Act - Request only AAAA records
    response = client.get("/api/resolve/example.com?type=AAAA")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["records"]) == 1
    assert data["records"][0]["type"] == "AAAA"
    assert data["records"][0]["value"] == "2001:db8::1"


def test_get_cname_chain_simple(client):
    """Test getting a simple CNAME chain."""
    # Arrange
    host1 = create_test_host(client, "www.example.com")
    host2 = create_test_host(client, "example.com")
    
    create_test_record(client, host1["id"], "CNAME", "example.com")
    create_test_record(client, host2["id"], "A", "192.168.1.1")
    
    # Act
    response = client.get("/api/cname-chain/www.example.com")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["hostname"] == "www.example.com"
    assert len(data["chain"]) == 1
    assert data["chain"][0]["hostname"] == "www.example.com"
    assert data["chain"][0]["cname"] == "example.com"
    assert data["resolved"] is True


def test_get_cname_chain_with_loop(client):
    """Test getting a CNAME chain with a loop."""
    # Arrange
    host1 = create_test_host(client, "a.example.com")
    host2 = create_test_host(client, "b.example.com")
    
    create_test_record(client, host1["id"], "CNAME", "b.example.com")
    create_test_record(client, host2["id"], "CNAME", "a.example.com")
    
    # Act
    response = client.get("/api/cname-chain/a.example.com")
    
    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error = response.json()["detail"]
    assert "cname loop" in error["message"].lower()


def test_get_cname_chain_max_depth(client):
    """Test CNAME chain with maximum depth."""
    # Create a chain of CNAME records
    domains = [f"d{i}.example.com" for i in range(10)]
    
    # Create hosts and records
    for i in range(len(domains) - 1):
        host = create_test_host(client, domains[i])
        create_test_record(client, host["id"], "CNAME", domains[i+1])
    
    # Add final A record
    final_host = create_test_host(client, domains[-1])
    create_test_record(client, final_host["id"], "A", "192.168.1.1")
    
    # Test with default max depth (should work)
    response = client.get(f"/api/cname-chain/{domains[0]}")
    assert response.status_code == status.HTTP_200_OK
    
    # Test with lower max depth (should fail)
    response = client.get(f"/api/cname-chain/{domains[0]}?max_depth=5")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["chain"]) <= 5
