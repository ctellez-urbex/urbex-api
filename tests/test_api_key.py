"""
Tests for API key authentication functionality.

This module tests the API key validation and authorization
for protected endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
def valid_api_key():
    """Valid API key for testing."""
    return "urbex-test-key-vjtyZHsCM2VpR_iGptzRxw"


@pytest.fixture
def invalid_api_key():
    """Invalid API key for testing."""
    return "invalid-api-key-123"


class TestAPIKeyAuthentication:
    """Test API key authentication functionality."""

    def test_contact_endpoint_with_valid_api_key(self, client, valid_api_key):
        """Test contact endpoint with valid API key."""
        headers = {"x-api-key": valid_api_key}
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/contact/", json=data, headers=headers)
        
        # Should return 200 or 500 (depending on email service), but not 401
        assert response.status_code != 401
        assert "x-api-key" in response.request.headers

    def test_contact_endpoint_without_api_key(self, client):
        """Test contact endpoint without API key."""
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/contact/", json=data)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert "API key required" in response.json()["detail"]

    def test_contact_endpoint_with_invalid_api_key(self, client, invalid_api_key):
        """Test contact endpoint with invalid API key."""
        headers = {"x-api-key": invalid_api_key}
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/contact/", json=data, headers=headers)
        
        # Should return 401 Unauthorized
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]

    def test_public_endpoints_without_api_key(self, client):
        """Test public endpoints work without API key."""
        # Health check should work without API key
        response = client.get("/health")
        assert response.status_code == 200
        
        # Docs should work without API key
        response = client.get("/docs")
        assert response.status_code == 200

    @patch('app.core.config.settings.require_api_key', False)
    def test_contact_endpoint_with_api_key_disabled(self, client):
        """Test contact endpoint when API key requirement is disabled."""
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/contact/", json=data)
        
        # Should work without API key when disabled
        assert response.status_code != 401

    def test_api_key_validation_function(self):
        """Test the API key validation function directly."""
        from app.core.security import validate_api_key
        
        # Test with valid API key
        assert validate_api_key("urbex-test-key-vjtyZHsCM2VpR_iGptzRxw") == True
        
        # Test with invalid API key
        assert validate_api_key("invalid-key") == False
        
        # Test with empty string
        assert validate_api_key("") == False


class TestAPIKeyHeaders:
    """Test API key header handling."""

    def test_x_api_key_header_case_insensitive(self, client, valid_api_key):
        """Test that x-api-key header is case insensitive."""
        headers = {"X-API-KEY": valid_api_key}
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/contact/", json=data, headers=headers)
        
        # Should work with uppercase header
        assert response.status_code != 401

    def test_multiple_api_keys_supported(self, client):
        """Test that multiple API keys are supported."""
        # Test with production key
        headers = {"x-api-key": "urbex-prod-key-pPK5CrbFX7Ue9u3gWvJc-A"}
        data = {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "Test message"
        }
        
        response = client.post("/api/v1/contact/", json=data, headers=headers)
        assert response.status_code != 401
        
        # Test with development key
        headers = {"x-api-key": "urbex-dev-key-pOV9-fe9HSKdI3tfogdUIw"}
        response = client.post("/api/v1/contact/", json=data, headers=headers)
        assert response.status_code != 401 