#!/usr/bin/env python3
"""
Script to check if a user exists in Cognito.
"""

import os

import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_user_exists(username):
    """Check if user exists in Cognito."""
    print(f"🔍 Checking if user exists: {username}")

    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    region = os.getenv("COGNITO_REGION", "us-east-2")

    try:
        cognito = boto3.client("cognito-idp", region_name=region)

        # List users with filter
        response = cognito.list_users(
            UserPoolId=user_pool_id, Filter=f'email = "{username}"'
        )

        users = response.get("Users", [])

        if users:
            user = users[0]
            print(f"✅ User found:")
            print(f"   Username: {user.get('Username')}")
            print(f"   Status: {user.get('UserStatus')}")
            print(f"   Enabled: {user.get('Enabled')}")

            # Get user attributes
            attributes = user.get("Attributes", [])
            for attr in attributes:
                if attr["Name"] == "email":
                    print(f"   Email: {attr['Value']}")
                elif attr["Name"] == "given_name":
                    print(f"   First Name: {attr['Value']}")
                elif attr["Name"] == "family_name":
                    print(f"   Last Name: {attr['Value']}")

            return user
        else:
            print(f"❌ User not found: {username}")
            return None

    except Exception as e:
        print(f"❌ Error checking user: {e}")
        return None


def list_all_users():
    """List all users in the user pool."""
    print("\n📋 Listing all users in the pool:")

    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    region = os.getenv("COGNITO_REGION", "us-east-2")

    try:
        cognito = boto3.client("cognito-idp", region_name=region)

        response = cognito.list_users(UserPoolId=user_pool_id)
        users = response.get("Users", [])

        if users:
            for i, user in enumerate(users, 1):
                print(f"\n{i}. Username: {user.get('Username')}")
                print(f"   Status: {user.get('UserStatus')}")
                print(f"   Enabled: {user.get('Enabled')}")

                # Get email
                attributes = user.get("Attributes", [])
                for attr in attributes:
                    if attr["Name"] == "email":
                        print(f"   Email: {attr['Value']}")
                        break
        else:
            print("No users found in the pool")

    except Exception as e:
        print(f"❌ Error listing users: {e}")


if __name__ == "__main__":
    print("🔍 Cognito User Check Tool")
    print("=" * 30)

    username = input("Enter username/email to check: ").strip()

    # Check specific user
    user = check_user_exists(username)

    # List all users
    list_all_users()

    if user:
        print(f"\n✅ User '{username}' exists and is ready for login")
    else:
        print(f"\n❌ User '{username}' does not exist. You need to register first.")
