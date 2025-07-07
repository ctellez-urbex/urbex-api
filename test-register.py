#!/usr/bin/env python3
"""
Diagnostic script to test user registration and identify issues.
"""

import os
import sys

from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

load_dotenv()

from app.services.cognito import cognito_service


def test_registration():
    """Test user registration with detailed error handling."""
    print("🔍 Testing User Registration")
    print("=" * 50)

    # Test data
    username = "testuser@example.com"
    email = "testuser@example.com"
    password = "TestPassword123!"
    attributes = {"given_name": "Test", "family_name": "User"}

    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Attributes: {attributes}")
    print()

    try:
        print("🔍 Attempting to register user...")
        result = cognito_service.register_user(
            username=username, email=email, password=password, attributes=attributes
        )

        if result:
            print("✅ Registration successful!")
            print(f"Result: {result}")
        else:
            print("❌ Registration failed - no result returned")

    except Exception as e:
        print(f"❌ Registration error: {e}")
        print(f"Error type: {type(e).__name__}")

        # If it's a ClientError, get more details
        if hasattr(e, "response"):
            print(f"Error code: {e.response['Error']['Code']}")
            print(f"Error message: {e.response['Error']['Message']}")


def test_cognito_config():
    """Test Cognito configuration."""
    print("🔍 Testing Cognito Configuration")
    print("=" * 50)

    print(f"User Pool ID: {cognito_service.user_pool_id}")
    print(f"Client ID: {cognito_service.client_id}")
    print(f"Client Secret: {'Set' if cognito_service.client_secret else 'Not set'}")
    print(f"Region: {cognito_service.client.meta.region_name}")
    print()


def test_aws_credentials():
    """Test AWS credentials."""
    print("🔍 Testing AWS Credentials")
    print("=" * 50)

    try:
        # Try to list user pools to test credentials
        response = cognito_service.client.list_user_pools(MaxResults=1)
        print("✅ AWS credentials are valid")
        print(f"Found {len(response.get('UserPools', []))} user pools")
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
    print()


if __name__ == "__main__":
    test_cognito_config()
    test_aws_credentials()
    test_registration()
