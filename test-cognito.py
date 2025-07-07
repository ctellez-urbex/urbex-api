#!/usr/bin/env python3
"""
Test script to diagnose Cognito connection issues.
"""

import os

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_aws_credentials():
    """Test AWS credentials."""
    print("🔍 Testing AWS credentials...")
    try:
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials valid: {identity}")
        return True
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        return False


def test_cognito_connection():
    """Test Cognito connection."""
    print("\n🔍 Testing Cognito connection...")

    # Get configuration
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    region = os.getenv("COGNITO_REGION", "us-east-2")

    print(f"📋 Configuration:")
    print(f"   User Pool ID: {user_pool_id}")
    print(f"   Client ID: {client_id}")
    print(f"   Region: {region}")

    try:
        # Create Cognito client
        cognito = boto3.client("cognito-idp", region_name=region)

        # Test describe user pool
        response = cognito.describe_user_pool(UserPoolId=user_pool_id)
        print(f"✅ User Pool exists: {response['UserPool']['Name']}")

        # Test describe user pool client
        response = cognito.describe_user_pool_client(
            UserPoolId=user_pool_id, ClientId=client_id
        )
        print(f"✅ User Pool Client exists: {response['UserPoolClient']['ClientName']}")

        return True
    except ClientError as e:
        print(f"❌ Cognito error: {e}")
        print(f"❌ Error code: {e.response['Error']['Code']}")
        print(f"❌ Error message: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_user_registration():
    """Test user registration."""
    print("\n🔍 Testing user registration...")

    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    region = os.getenv("COGNITO_REGION", "us-east-2")

    try:
        cognito = boto3.client("cognito-idp", region_name=region)

        # Try to register a test user
        response = cognito.sign_up(
            ClientId=client_id,
            Username="test@example.com",
            Password="TestPassword123!",
            UserAttributes=[
                {"Name": "email", "Value": "test@example.com"},
                {"Name": "given_name", "Value": "Test"},
                {"Name": "family_name", "Value": "User"},
            ],
        )

        print(f"✅ User registration successful: {response}")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "UsernameExistsException":
            print(f"ℹ️  User already exists: {e.response['Error']['Message']}")
            return True
        else:
            print(f"❌ Registration error: {e}")
            print(f"❌ Error code: {e.response['Error']['Code']}")
            print(f"❌ Error message: {e.response['Error']['Message']}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Cognito Diagnostic Tool")
    print("=" * 40)

    # Test AWS credentials
    if not test_aws_credentials():
        print("\n❌ Cannot proceed without valid AWS credentials")
        exit(1)

    # Test Cognito connection
    if not test_cognito_connection():
        print("\n❌ Cannot connect to Cognito")
        exit(1)

    # Test user registration
    test_user_registration()

    print("\n✅ Diagnostic complete!")
