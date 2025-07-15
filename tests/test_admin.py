"""
Tests for admin endpoints.

This module contains tests for user management functionality
including listing, viewing, updating, and deleting users.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.admin import UserStatus

client = TestClient(app)


# Mock the verify_admin_token function globally
@pytest.fixture(autouse=True)
def mock_admin_auth():
    """Mock admin authentication for all tests."""
    with patch("app.core.security.verify_admin_token") as mock:
        mock.return_value = {"is_admin": True}
        yield mock


@pytest.fixture
def mock_admin_user():
    """Mock admin user for testing."""
    return {"sub": "admin-user-id", "email": "admin@urbex.com.co", "is_admin": True}


@pytest.fixture
def mock_cognito_user():
    """Mock Cognito user response."""
    return {
        "Username": "test-user-id",
        "UserAttributes": [
            {"Name": "sub", "Value": "test-user-id"},
            {"Name": "email", "Value": "test@urbex.com.co"},
            {"Name": "given_name", "Value": "Test"},
            {"Name": "family_name", "Value": "User"},
            {"Name": "phone_number", "Value": "+573052464748"},
            {"Name": "custom:plan", "Value": "mensual"},
            {"Name": "custom:su", "Value": "0"},
            {"Name": "email_verified", "Value": "true"},
        ],
        "UserStatus": "CONFIRMED",
        "UserCreateDate": "2024-01-01T00:00:00Z",
        "UserLastModifiedDate": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_cognito_users_list():
    """Mock Cognito users list response."""
    return {
        "Users": [
            {
                "Username": "user1",
                "Attributes": [
                    {"Name": "sub", "Value": "user1"},
                    {"Name": "email", "Value": "user1@urbex.com.co"},
                    {"Name": "given_name", "Value": "User"},
                    {"Name": "family_name", "Value": "One"},
                    {"Name": "custom:plan", "Value": "mensual"},
                    {"Name": "custom:su", "Value": "0"},
                    {"Name": "email_verified", "Value": "true"},
                ],
                "UserStatus": "CONFIRMED",
                "UserCreateDate": "2024-01-01T00:00:00Z",
            },
            {
                "Username": "user2",
                "Attributes": [
                    {"Name": "sub", "Value": "user2"},
                    {"Name": "email", "Value": "user2@urbex.com.co"},
                    {"Name": "given_name", "Value": "User"},
                    {"Name": "family_name", "Value": "Two"},
                    {"Name": "custom:plan", "Value": "anual"},
                    {"Name": "custom:su", "Value": "1"},
                    {"Name": "email_verified", "Value": "false"},
                ],
                "UserStatus": "DISABLED",
                "UserCreateDate": "2024-01-01T00:00:00Z",
            },
        ]
    }


class TestListUsers:
    """Test cases for listing users endpoint."""

    @patch("app.api.v1.admin.cognito_service")
    def test_list_users_success(self, mock_cognito_service, mock_cognito_users_list):
        """Test successful user listing."""
        mock_cognito_service.list_all_users.return_value = mock_cognito_users_list

        request_data = {"filter": "test"}

        response = client.post("/api/v1/admin/users", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert "users" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["users"]) == 2

    @patch("app.api.v1.admin.cognito_service")
    def test_list_users_with_search(
        self, mock_cognito_service, mock_cognito_users_list
    ):
        """Test user listing with search filter."""
        mock_cognito_service.list_all_users.return_value = mock_cognito_users_list

        request_data = {"filter": "user1"}

        response = client.post("/api/v1/admin/users", json=request_data)

        assert response.status_code == 200
        mock_cognito_service.list_all_users.assert_called_once()

    def test_list_users_unauthorized(self, mock_admin_auth):
        """Test user listing without admin privileges."""
        mock_admin_auth.side_effect = Exception("Unauthorized")

        request_data = {"filter": "test"}

        response = client.post("/api/v1/admin/users", json=request_data)

        assert response.status_code == 500


class TestGetUser:
    """Test cases for getting user details endpoint."""

    @patch("app.api.v1.admin.cognito_service")
    def test_get_user_success(self, mock_cognito_service, mock_cognito_user):
        """Test successful user retrieval."""
        mock_cognito_service.get_user_by_id.return_value = mock_cognito_user

        response = client.get("/api/v1/admin/users/test-user-id")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user-id"
        assert data["email"] == "test@urbex.com.co"
        assert data["first_name"] == "Test"
        assert data["last_name"] == "User"

    @patch("app.api.v1.admin.cognito_service")
    def test_get_user_not_found(self, mock_cognito_service):
        """Test user retrieval when user doesn't exist."""
        mock_cognito_service.get_user_by_id.return_value = None

        response = client.get("/api/v1/admin/users/nonexistent-user")

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestUpdateUser:
    """Test cases for updating user endpoint."""

    @patch("app.api.v1.admin.cognito_service")
    def test_update_user_success(self, mock_cognito_service):
        """Test successful user update."""
        mock_cognito_service.update_user_attributes.return_value = True

        update_data = {"first_name": "Updated", "last_name": "Name", "plan": "anual"}

        response = client.put("/api/v1/admin/users/test-user-id", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "User updated successfully" in data["message"]

    @patch("app.api.v1.admin.cognito_service")
    def test_update_user_no_attributes(self, mock_cognito_service):
        """Test user update with no attributes to update."""

        response = client.put("/api/v1/admin/users/test-user-id", json={})

        assert response.status_code == 400
        assert "No attributes to update" in response.json()["detail"]

    @patch("app.api.v1.admin.cognito_service")
    def test_update_user_failure(self, mock_cognito_service):
        """Test user update when Cognito operation fails."""
        mock_cognito_service.update_user_attributes.return_value = False

        update_data = {"first_name": "Updated"}

        response = client.put("/api/v1/admin/users/test-user-id", json=update_data)

        assert response.status_code == 500
        assert "Failed to update user" in response.json()["detail"]


class TestUpdateUserStatus:
    """Test cases for updating user status endpoint."""

    @patch("app.api.v1.admin.cognito_service")
    def test_enable_user_success(self, mock_cognito_service):
        """Test successful user enable."""
        mock_cognito_service.enable_user.return_value = True

        status_data = {"status": "ENABLED"}

        response = client.patch(
            "/api/v1/admin/users/test-user-id/status", json=status_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ENABLED" in data["message"]

    @patch("app.api.v1.admin.cognito_service")
    def test_disable_user_success(self, mock_cognito_service):
        """Test successful user disable."""
        mock_cognito_service.disable_user.return_value = True

        status_data = {"status": "DISABLED"}

        response = client.patch(
            "/api/v1/admin/users/test-user-id/status", json=status_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "DISABLED" in data["message"]

    def test_update_user_status_invalid(self):
        """Test user status update with invalid status."""

        status_data = {"status": "INVALID_STATUS"}

        response = client.patch(
            "/api/v1/admin/users/test-user-id/status", json=status_data
        )

        assert response.status_code == 422  # Validation error


class TestDeleteUser:
    """Test cases for deleting user endpoint."""

    @patch("app.api.v1.admin.cognito_service")
    def test_delete_user_success(self, mock_cognito_service):
        """Test successful user deletion."""
        mock_cognito_service.delete_user.return_value = True

        response = client.delete("/api/v1/admin/users/test-user-id")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "User deleted successfully" in data["message"]

    @patch("app.api.v1.admin.cognito_service")
    def test_delete_user_failure(self, mock_cognito_service):
        """Test user deletion when Cognito operation fails."""
        mock_cognito_service.delete_user.return_value = False

        response = client.delete("/api/v1/admin/users/test-user-id")

        assert response.status_code == 500
        assert "Failed to delete user" in response.json()["detail"]
