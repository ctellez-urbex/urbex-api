"""
AWS Cognito service integration.

This module provides authentication and user management functionality
using AWS Cognito User Pool.
"""

import base64
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class CognitoService:
    """Service class for AWS Cognito operations."""

    def __init__(self) -> None:
        """Initialize the Cognito service with AWS client."""
        self.client = boto3.client(
            "cognito-idp",
            region_name=settings.cognito_region or settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )
        self.user_pool_id = settings.cognito_user_pool_id
        self.client_id = settings.cognito_client_id
        self.client_secret = settings.cognito_client_secret

    def authenticate_user(
        self, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with Cognito.

        Args:
            username: The username or email
            password: The user's password

        Returns:
            Authentication result or None if failed
        """
        try:
            print(f"🔍 Cognito config - User Pool ID: {self.user_pool_id}")
            print(f"🔍 Cognito config - Client ID: {self.client_id}")
            print(
                f"🔍 Cognito config - Region: {settings.cognito_region or settings.aws_region}"
            )

            auth_params = {
                "USERNAME": username,
                "PASSWORD": password,
            }

            if self.client_secret:
                auth_params["SECRET_HASH"] = self._get_secret_hash(username)
                print("🔍 Using client secret for authentication")

            print(f"🔍 Auth parameters: {auth_params}")

            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters=auth_params,
            )

            print(f"✅ Authentication successful for user: {username}")
            return response
        except ClientError as e:
            print(f"❌ Authentication error: {e}")
            print(f"❌ Error code: {e.response['Error']['Code']}")
            print(f"❌ Error message: {e.response['Error']['Message']}")
            return None

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        attributes: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Register a new user in Cognito.

        Args:
            username: The username
            email: The user's email
            password: The user's password
            attributes: Additional user attributes

        Returns:
            Registration result or None if failed
        """
        try:
            user_attributes = [
                {"Name": "email", "Value": email},
            ]

            if attributes:
                for key, value in attributes.items():
                    user_attributes.append({"Name": key, "Value": value})

            signup_params = {
                "ClientId": self.client_id,
                "Username": username,
                "Password": password,
                "UserAttributes": user_attributes,
            }

            if self.client_secret:
                signup_params["SecretHash"] = self._get_secret_hash(username)

            response = self.client.sign_up(**signup_params)
            return response
        except ClientError as e:
            print(f"Registration error: {e}")
            return None

    def confirm_registration(self, username: str, confirmation_code: str) -> bool:
        """
        Confirm user registration with confirmation code.

        Args:
            username: The username
            confirmation_code: The confirmation code sent to user

        Returns:
            True if successful, False otherwise
        """
        try:
            confirm_params = {
                "ClientId": self.client_id,
                "Username": username,
                "ConfirmationCode": confirmation_code,
            }

            if self.client_secret:
                confirm_params["SecretHash"] = self._get_secret_hash(username)

            self.client.confirm_sign_up(**confirm_params)
            return True
        except ClientError as e:
            print(f"Confirmation error: {e}")
            return False

    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information using access token.

        Args:
            access_token: The user's access token

        Returns:
            User information or None if failed
        """
        try:
            response = self.client.get_user(AccessToken=access_token)
            return response
        except ClientError as e:
            print(f"Get user info error: {e}")
            return None

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            New tokens or None if failed
        """
        try:
            refresh_params = {
                "ClientId": self.client_id,
                "RefreshToken": refresh_token,
            }

            if self.client_secret:
                refresh_params["SecretHash"] = self._get_secret_hash("")

            response = self.client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters=refresh_params,
            )
            return response
        except ClientError as e:
            print(f"Token refresh error: {e}")
            return None

    def _get_secret_hash(self, username: str) -> str:
        """
        Generate secret hash for Cognito operations.

        Args:
            username: The username

        Returns:
            The secret hash
        """
        import hashlib
        import hmac

        if not self.client_secret:
            return ""

        message = username + self.client_id
        dig = hmac.new(
            str(self.client_secret).encode("utf-8"),
            msg=str(message).encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()

        return base64.b64encode(dig).decode()


# Global Cognito service instance
cognito_service = CognitoService()
