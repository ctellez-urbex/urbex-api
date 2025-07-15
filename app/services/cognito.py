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
        try:
            # In Lambda, don't specify credentials explicitly - use the execution role
            self.client = boto3.client(
                "cognito-idp",
                region_name=settings.cognito_region or settings.aws_region,
            )
            self.user_pool_id = settings.cognito_user_pool_id
            self.client_id = settings.cognito_client_id
            self.client_secret = settings.cognito_client_secret

            print(f"✅ Cognito client initialized successfully")
            print(f"🔍 User Pool ID: {self.user_pool_id}")
            print(f"🔍 Client ID: {self.client_id}")
            print(f"🔍 Region: {settings.cognito_region or settings.aws_region}")

        except Exception as e:
            print(f"❌ Error initializing Cognito client: {e}")
            raise

    def check_user_exists(self, username: str) -> bool:
        """
        Check if a user already exists in Cognito.

        Args:
            username: The username or email to check

        Returns:
            True if user exists, False otherwise
        """
        try:
            self.client.admin_get_user(UserPoolId=self.user_pool_id, Username=username)
            print(f"✅ User already exists: {username}")
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "UserNotFoundException":
                print(f"✅ User does not exist: {username}")
                return False
            else:
                print(f"❌ Error checking user existence: {e}")
                # If there's an error, assume user doesn't exist to allow registration
                return False

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
            print(f"🔍 Raw Cognito response: {response}")
            print(f"🔍 User attributes: {response.get('UserAttributes', [])}")
            return response
        except ClientError as e:
            print(f"Get user info error: {e}")
            return None

    def get_user_info_admin(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information using admin privileges (includes custom attributes).

        Args:
            username: The username or email

        Returns:
            User information or None if failed
        """
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id, Username=username
            )
            print(f"🔍 Admin get user response: {response}")
            print(f"🔍 User attributes: {response.get('UserAttributes', [])}")
            return response
        except ClientError as e:
            print(f"Admin get user info error: {e}")
            return None

    def get_user_info_by_token_admin(
        self, access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user information using access token and then fetch full details with admin privileges.

        Args:
            access_token: The user's access token

        Returns:
            User information with custom attributes or None if failed
        """
        try:
            # First get basic user info to extract email
            basic_info = self.client.get_user(AccessToken=access_token)
            print(f"🔍 Basic user info: {basic_info}")
            # Extract email from the response
            email = None
            for attr in basic_info.get("UserAttributes", []):
                if attr.get("Name") == "email":
                    email = attr.get("Value")
                    break
            if not email:
                print("❌ Could not extract email from token")
                return basic_info
            print(
                f"🔍 About to call admin_get_user with UserPoolId={self.user_pool_id}, Username={email}"
            )
            # Now get full user info with admin privileges using email as username
            admin_info = self.client.admin_get_user(
                UserPoolId=self.user_pool_id, Username=email
            )
            print(f"🔍 Admin user info: {admin_info}")
            return admin_info
        except Exception as e:
            import traceback

            print(
                f"❌ Exception in get_user_info_by_token_admin: {type(e).__name__}: {e}"
            )
            print(traceback.format_exc())
            # Fallback to basic get_user
            return self.get_user_info(access_token)

    def forgot_password(self, username: str) -> bool:
        """
        Initiate forgot password process.

        Args:
            username: The username or email

        Returns:
            True if successful, False otherwise
        """
        try:
            forgot_params = {
                "ClientId": self.client_id,
                "Username": username,
            }

            if self.client_secret:
                forgot_params["SecretHash"] = self._get_secret_hash(username)

            self.client.forgot_password(**forgot_params)
            print(f"✅ Forgot password initiated for user: {username}")
            return True
        except ClientError as e:
            print(f"❌ Forgot password error: {e}")
            print(f"❌ Error code: {e.response['Error']['Code']}")
            print(f"❌ Error message: {e.response['Error']['Message']}")
            return False

    def disable_user(self, username: str) -> bool:
        """
        Disable a user account in Cognito.

        Args:
            username: The username or email

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.admin_disable_user(
                UserPoolId=self.user_pool_id, Username=username
            )
            print(f"✅ User disabled: {username}")
            return True
        except ClientError as e:
            print(f"❌ Disable user error: {e}")
            print(f"❌ Error code: {e.response['Error']['Code']}")
            print(f"❌ Error message: {e.response['Error']['Message']}")
            return False

    def confirm_forgot_password(
        self, username: str, confirmation_code: str, new_password: str
    ) -> bool:
        """
        Confirm forgot password with confirmation code and new password.

        Args:
            username: The username or email
            confirmation_code: The confirmation code sent to user
            new_password: The new password

        Returns:
            True if successful, False otherwise
        """
        try:
            confirm_params = {
                "ClientId": self.client_id,
                "Username": username,
                "ConfirmationCode": confirmation_code,
                "Password": new_password,
            }

            if self.client_secret:
                confirm_params["SecretHash"] = self._get_secret_hash(username)

            self.client.confirm_forgot_password(**confirm_params)
            print(f"✅ Password reset confirmed for user: {username}")
            return True
        except ClientError as e:
            print(f"❌ Confirm forgot password error: {e}")
            print(f"❌ Error code: {e.response['Error']['Code']}")
            print(f"❌ Error message: {e.response['Error']['Message']}")
            return False

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

    def list_users(
        self,
        limit: int = 10,
        pagination_token: Optional[str] = None,
        filter_expression: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        List users in the Cognito User Pool with pagination and filtering.

        Args:
            limit: Maximum number of users to return
            pagination_token: Token for pagination
            filter_expression: Filter expression for users

        Returns:
            List of users or None if failed
        """
        try:
            params = {"UserPoolId": self.user_pool_id, "Limit": limit}

            if pagination_token:
                params["PaginationToken"] = pagination_token

            if filter_expression:
                params["Filter"] = filter_expression

            response = self.client.list_users(**params)

            return response
        except ClientError as e:
            print(f"❌ Error listing users: {e}")
            return None

    def list_all_users(self) -> Optional[Dict[str, Any]]:
        """
        List ALL users in the Cognito User Pool by handling pagination automatically.

        Returns:
            All users combined or None if failed
        """
        try:
            print(f"🔍 Starting list_all_users with UserPoolId: {self.user_pool_id}")

            all_users = []
            pagination_token = None

            while True:
                params = {
                    "UserPoolId": self.user_pool_id,
                    "Limit": 60,  # Maximum allowed by Cognito
                }

                if pagination_token:
                    params["PaginationToken"] = pagination_token

                print(f"🔍 Calling list_users with params: {params}")
                response = self.client.list_users(**params)

                if not response or "Users" not in response:
                    print(f"🔍 No response or no Users in response")
                    break

                users = response.get("Users", [])
                all_users.extend(users)
                print(f"🔍 Retrieved {len(users)} users, total so far: {len(all_users)}")

                # Check if there are more pages
                pagination_token = response.get("PaginationToken")
                if not pagination_token:
                    print(f"🔍 No more pages, finished pagination")
                    break

            print(f"✅ Total users retrieved: {len(all_users)}")
            return {"Users": all_users}

        except ClientError as e:
            print(f"❌ Error listing all users: {e}")
            print(f"❌ Error code: {e.response['Error']['Code']}")
            print(f"❌ Error message: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error in list_all_users: {type(e).__name__}: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by user ID using admin privileges.

        Args:
            user_id: The Cognito User ID

        Returns:
            User information or None if failed
        """
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id, Username=user_id
            )
            return response
        except ClientError as e:
            print(f"❌ Error getting user by ID: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by email using admin privileges.

        Args:
            email: The user's email address

        Returns:
            User information or None if failed
        """
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id, Username=email
            )
            print(f"🔍 Get user by email response: {response}")
            return response
        except ClientError as e:
            print(f"❌ Error getting user by email: {e}")
            return None

    def update_user_attributes(self, user_id: str, attributes: Dict[str, str]) -> bool:
        """
        Update user attributes using admin privileges.

        Args:
            user_id: The Cognito User ID
            attributes: Dictionary of attributes to update

        Returns:
            True if successful, False otherwise
        """
        try:
            user_attributes = []
            for key, value in attributes.items():
                user_attributes.append({"Name": key, "Value": value})

            self.client.admin_update_user_attributes(
                UserPoolId=self.user_pool_id,
                Username=user_id,
                UserAttributes=user_attributes,
            )
            print(f"✅ User attributes updated successfully for: {user_id}")
            return True
        except ClientError as e:
            print(f"❌ Error updating user attributes: {e}")
            return False

    def enable_user(self, user_id: str) -> bool:
        """
        Enable a user account.

        Args:
            user_id: The Cognito User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.admin_enable_user(
                UserPoolId=self.user_pool_id, Username=user_id
            )
            print(f"✅ User enabled successfully: {user_id}")
            return True
        except ClientError as e:
            print(f"❌ Error enabling user: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user account.

        Args:
            user_id: The Cognito User ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.admin_delete_user(
                UserPoolId=self.user_pool_id, Username=user_id
            )
            print(f"✅ User deleted successfully: {user_id}")
            return True
        except ClientError as e:
            print(f"❌ Error deleting user: {e}")
            return False


# Global Cognito service instance
cognito_service = CognitoService()
