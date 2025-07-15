#!/usr/bin/env python3
"""
Debug script to test Cognito list_users functionality.
"""

import os

import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def debug_cognito_users():
    """Debug Cognito users listing."""

    # Get configuration
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    region = "us-east-2"  # Based on the user pool ID

    print(f"🔍 User Pool ID: {user_pool_id}")
    print(f"🔍 Region: {region}")

    # Create Cognito client
    client = boto3.client("cognito-idp", region_name=region)

    try:
        # List users
        response = client.list_users(UserPoolId=user_pool_id, Limit=5)

        if "Users" in response:
            print(f"🔍 Found {len(response['Users'])} users")

            for i, user in enumerate(response["Users"]):
                print(f"\n🔍 User {i+1}:")
                print(f"  Username: {user.get('Username', 'N/A')}")
                print(f"  Status: {user.get('UserStatus', 'N/A')}")
                print(f"  Created: {user.get('UserCreateDate', 'N/A')}")
                print(f"  Attributes:")

                # Debug: Print raw attributes
                raw_attrs = user.get("Attributes", [])
                print(f"    Raw attributes count: {len(raw_attrs)}")

                for attr in raw_attrs:
                    name = attr.get("Name", "")
                    value = attr.get("Value", "")
                    print(f"    {name}: {value}")

                # Test our parsing function
                print(f"  Parsed attributes:")
                parsed = parse_user_attributes(raw_attrs)
                for key, value in parsed.items():
                    print(f"    {key}: {value}")
        else:
            print("❌ No users found in response")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def parse_user_attributes(user_attributes: list) -> dict:
    """Parse Cognito user attributes into a dictionary."""
    print(f"🔍 Debug: Parsing {len(user_attributes)} user attributes")
    for attr in user_attributes:
        print(
            f"🔍 Debug: Attribute - Name: '{attr.get('Name', '')}', Value: '{attr.get('Value', '')}'"
        )

    attributes = {}
    for attr in user_attributes:
        name = attr.get("Name", "")
        value = attr.get("Value", "")

        if name == "email":
            attributes["email"] = value
        elif name == "given_name":
            attributes["first_name"] = value
        elif name == "family_name":
            attributes["last_name"] = value
        elif name == "phone_number":
            attributes["phone_number"] = value
        elif name == "custom:plan":
            attributes["plan"] = value
        elif name == "custom:su":
            attributes["su"] = value
        elif name == "email_verified":
            attributes["email_verified"] = value == "true"
        elif name == "sub":
            attributes["user_id"] = value

    print(f"🔍 Debug: Parsed attributes: {attributes}")
    return attributes


if __name__ == "__main__":
    debug_cognito_users()
