#!/usr/bin/env python3
"""
Script to confirm a test user in Cognito.
"""

import os

import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def confirm_user(username, confirmation_code):
    """Confirm user registration."""
    print(f"🔍 Confirming user: {username}")

    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    region = os.getenv("COGNITO_REGION", "us-east-2")

    try:
        cognito = boto3.client("cognito-idp", region_name=region)

        response = cognito.confirm_sign_up(
            ClientId=client_id, Username=username, ConfirmationCode=confirmation_code
        )

        print(f"✅ User confirmed successfully!")
        return True
    except Exception as e:
        print(f"❌ Confirmation error: {e}")
        return False


if __name__ == "__main__":
    print("🔐 User Confirmation Tool")
    print("=" * 30)

    username = input("Enter username (email): ").strip()
    confirmation_code = input("Enter confirmation code: ").strip()

    if confirm_user(username, confirmation_code):
        print("\n🎉 User is now confirmed and ready for login!")
    else:
        print("\n❌ Failed to confirm user")
