"""Tests for health check endpoint"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "slfn-nexus-platform"
    assert "version" in data


def test_health_check_response_format(client: TestClient):
    """Test health check response format"""
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    assert "status" in response.json()
    assert "service" in response.json()
    assert "version" in response.json()