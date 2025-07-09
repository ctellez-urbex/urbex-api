#!/usr/bin/env python3
"""
Debug script to check Cognito user attributes.
"""

import os
import sys

import boto3
from botocore.exceptions import ClientError

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.core.config import settings


def get_user_attributes():
    """Get user attributes from Cognito."""
    try:
        # Create Cognito client
        client = boto3.client(
            "cognito-idp",
            region_name=settings.cognito_region or settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
        )

        print(f"🔍 Cognito config - User Pool ID: {settings.cognito_user_pool_id}")
        print(f"🔍 Cognito config - Client ID: {settings.cognito_client_id}")
        print(
            f"🔍 Cognito config - Region: {settings.cognito_region or settings.aws_region}"
        )

        # First, let's authenticate to get a token
        auth_params = {
            "USERNAME": "carloss.tellezz@gmail.com",
            "PASSWORD": "4p0C4l1ps1s",
        }

        print("🔍 Authenticating...")
        auth_response = client.initiate_auth(
            ClientId=settings.cognito_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters=auth_params,
        )

        access_token = auth_response["AuthenticationResult"]["AccessToken"]
        print(f"✅ Authentication successful")
        print(f"🔍 Access token: {access_token[:50]}...")

        # Now get user info
        print("🔍 Getting user info...")
        user_response = client.get_user(AccessToken=access_token)

        print(f"🔍 Raw Cognito response: {user_response}")
        print(f"🔍 Username: {user_response.get('Username')}")
        print(f"🔍 User attributes:")

        for attr in user_response.get("UserAttributes", []):
            name = attr.get("Name")
            value = attr.get("Value")
            print(f"  - {name}: {value}")

        # Also check if there are any custom attributes
        print(f"🔍 Looking for custom attributes...")
        custom_attrs = [
            attr
            for attr in user_response.get("UserAttributes", [])
            if attr.get("Name", "").startswith("custom:")
        ]

        if custom_attrs:
            print(f"🔍 Custom attributes found:")
            for attr in custom_attrs:
                print(f"  - {attr.get('Name')}: {attr.get('Value')}")
        else:
            print(f"🔍 No custom attributes found")

    except ClientError as e:
        print(f"❌ Error: {e}")
        print(f"❌ Error code: {e.response['Error']['Code']}")
        print(f"❌ Error message: {e.response['Error']['Message']}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    get_user_attributes()
