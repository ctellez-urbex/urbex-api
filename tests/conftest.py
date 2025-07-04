"""
Pytest configuration and fixtures.

This module provides common fixtures and configuration for all tests.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_cognito_service() -> Mock:
    """Mock Cognito service for testing."""
    return Mock()


@pytest.fixture
def mock_mailgun_service() -> Mock:
    """Mock Mailgun service for testing."""
    return Mock()


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def sample_login_data() -> dict:
    """Sample login data for testing."""
    return {
        "username": "testuser",
        "password": "testpassword123",
    }


@pytest.fixture
def sample_token_response() -> dict:
    """Sample token response for testing."""
    return {
        "access_token": "test_access_token",
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": "test_refresh_token",
    } 