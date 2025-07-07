#!/usr/bin/env python3
"""
Script to test authentication directly with Cognito.
"""

import os

import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_authentication(username, password):
    """Test authentication with Cognito."""
    print(f"🔍 Testing authentication for: {username}")

    client_id = os.getenv("COGNITO_CLIENT_ID")
    region = os.getenv("COGNITO_REGION", "us-east-2")

    try:
        cognito = boto3.client("cognito-idp", region_name=region)

        # Prepare auth parameters
        auth_params = {
            "USERNAME": username,
            "PASSWORD": password,
        }

        print(f"🔍 Auth parameters: {auth_params}")

        # Attempt authentication
        response = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters=auth_params,
        )

        print(f"✅ Authentication successful!")
        print(
            f"🔑 Access Token: {response['AuthenticationResult']['AccessToken'][:50]}..."
        )
        print(
            f"🔄 Refresh Token: {response['AuthenticationResult']['RefreshToken'][:50]}..."
        )
        print(f"⏰ Expires In: {response['AuthenticationResult']['ExpiresIn']} seconds")

        return response

    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        if hasattr(e, "response"):
            print(f"❌ Error code: {e.response['Error']['Code']}")
            print(f"❌ Error message: {e.response['Error']['Message']}")
        return None


def reset_user_password(username):
    """Reset user password (admin action)."""
    print(f"🔧 Resetting password for: {username}")

    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    region = os.getenv("COGNITO_REGION", "us-east-2")

    try:
        cognito = boto3.client("cognito-idp", region_name=region)

        # Set temporary password
        response = cognito.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=username,
            Password="TempPassword123!",
            Permanent=False,
        )

        print(f"✅ Password reset successful!")
        print(f"📧 User will receive a temporary password via email")
        return True

    except Exception as e:
        print(f"❌ Password reset failed: {e}")
        return False


if __name__ == "__main__":
    print("🔐 Cognito Authentication Test Tool")
    print("=" * 40)

    username = input("Enter username/email: ").strip()
    password = input("Enter password: ").strip()

    # Test authentication
    result = test_authentication(username, password)

    if not result:
        print(f"\n❌ Authentication failed. Possible solutions:")
        print(f"1. Check if the password is correct")
        print(f"2. Reset the user password")

        reset_option = (
            input("\nDo you want to reset the user password? (y/n): ").strip().lower()
        )
        if reset_option == "y":
            reset_user_password(username)
            print(f"\n📧 Check the email for the temporary password")
            print(f"🔐 Then try to login with the temporary password")
