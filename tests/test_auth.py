"""
Tests for authentication endpoints.

This module contains tests for all authentication-related endpoints
including registration, login, and token management.
"""

from unittest.mock import patch

import pytest
from fastapi import status


class TestAuthEndpoints:
    """Test class for authentication endpoints."""

    def test_register_user_success(
        self, client: pytest.FixtureRequest, sample_user_data: dict
    ) -> None:
        """Test successful user registration."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito, patch(
            "app.api.v1.auth.mailgun_service"
        ) as mock_mailgun:
            # Mock successful registration
            mock_cognito.register_user.return_value = {"UserSub": "test-user-id"}
            mock_mailgun.send_welcome_email.return_value = True

            response = client.post("/api/v1/auth/register", json=sample_user_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "User registered successfully" in data["message"]
            assert data["data"]["username"] == sample_user_data["username"]

    def test_register_user_failure(
        self, client: pytest.FixtureRequest, sample_user_data: dict
    ) -> None:
        """Test user registration failure."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock failed registration
            mock_cognito.register_user.return_value = None

            response = client.post("/api/v1/auth/register", json=sample_user_data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Failed to register user" in data["detail"]

    def test_confirm_registration_success(self, client: pytest.FixtureRequest) -> None:
        """Test successful registration confirmation."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock successful confirmation
            mock_cognito.confirm_registration.return_value = True

            confirm_data = {"username": "testuser", "confirmation_code": "123456"}

            response = client.post("/api/v1/auth/confirm", json=confirm_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "User confirmed successfully" in data["message"]

    def test_confirm_registration_failure(self, client: pytest.FixtureRequest) -> None:
        """Test registration confirmation failure."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock failed confirmation
            mock_cognito.confirm_registration.return_value = False

            confirm_data = {"username": "testuser", "confirmation_code": "123456"}

            response = client.post("/api/v1/auth/confirm", json=confirm_data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Invalid confirmation code" in data["detail"]

    def test_login_success(
        self, client: pytest.FixtureRequest, sample_login_data: dict
    ) -> None:
        """Test successful user login."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock successful authentication
            mock_cognito.authenticate_user.return_value = {
                "AuthenticationResult": {
                    "AccessToken": "test_access_token",
                    "RefreshToken": "test_refresh_token",
                    "ExpiresIn": 3600,
                }
            }

            response = client.post("/api/v1/auth/login", json=sample_login_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "test_access_token"
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 3600
            assert data["refresh_token"] == "test_refresh_token"

    def test_login_failure(
        self, client: pytest.FixtureRequest, sample_login_data: dict
    ) -> None:
        """Test user login failure."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock failed authentication
            mock_cognito.authenticate_user.return_value = None

            response = client.post("/api/v1/auth/login", json=sample_login_data)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "Invalid credentials" in data["detail"]

    def test_refresh_token_success(self, client: pytest.FixtureRequest) -> None:
        """Test successful token refresh."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock successful token refresh
            mock_cognito.refresh_token.return_value = {
                "AuthenticationResult": {
                    "AccessToken": "new_access_token",
                    "ExpiresIn": 3600,
                }
            }

            refresh_data = {"refresh_token": "test_refresh_token"}

            response = client.post("/api/v1/auth/refresh", json=refresh_data)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["access_token"] == "new_access_token"
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 3600

    def test_refresh_token_failure(self, client: pytest.FixtureRequest) -> None:
        """Test token refresh failure."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock failed token refresh
            mock_cognito.refresh_token.return_value = None

            refresh_data = {"refresh_token": "invalid_refresh_token"}

            response = client.post("/api/v1/auth/refresh", json=refresh_data)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "Invalid refresh token" in data["detail"]

    def test_get_current_user_success(self, client: pytest.FixtureRequest) -> None:
        """Test successful current user retrieval."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock successful user info retrieval
            mock_cognito.get_user_info.return_value = {
                "UserAttributes": [
                    {"Name": "sub", "Value": "testuser"},
                    {"Name": "email", "Value": "test@example.com"},
                    {"Name": "given_name", "Value": "Test"},
                    {"Name": "family_name", "Value": "User"},
                ]
            }

            headers = {"Authorization": "Bearer test_token"}
            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == "testuser"
            assert data["email"] == "test@example.com"
            assert data["first_name"] == "Test"
            assert data["last_name"] == "User"

    def test_get_current_user_failure(self, client: pytest.FixtureRequest) -> None:
        """Test current user retrieval failure."""
        with patch("app.api.v1.auth.cognito_service") as mock_cognito:
            # Mock failed user info retrieval
            mock_cognito.get_user_info.return_value = None

            headers = {"Authorization": "Bearer invalid_token"}
            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "Invalid token" in data["detail"]

    def test_logout_success(self, client: pytest.FixtureRequest) -> None:
        """Test successful user logout."""
        headers = {"Authorization": "Bearer test_token"}
        response = client.post("/api/v1/auth/logout", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "User logged out successfully" in data["message"]


class TestHealthEndpoints:
    """Test class for health check endpoints."""

    def test_health_check(self, client: pytest.FixtureRequest) -> None:
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "Urbex API" in data["service"]

    def test_root_endpoint(self, client: pytest.FixtureRequest) -> None:
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Welcome to Urbex API" in data["message"]
        assert "version" in data
