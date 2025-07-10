#!/usr/bin/env python3
"""
Script to compare Cognito configurations between local and production environments.
"""

import os
import sys
from typing import Any, Dict

import requests

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.config import settings


def compare_cognito_config():
    """Compare Cognito configuration between environments."""
    print("🔍 Comparing Cognito configurations...")
    print("=" * 50)

    # Local configuration
    print("📋 LOCAL Configuration:")
    print(f"  User Pool ID: {settings.cognito_user_pool_id}")
    print(f"  Client ID: {settings.cognito_client_id}")
    print(f"  Region: {settings.cognito_region or settings.aws_region}")
    print()

    # Production configuration (from environment variables)
    print("📋 PRODUCTION Configuration:")
    print(f"  User Pool ID: {os.getenv('COGNITO_USER_POOL_ID')}")
    print(f"  Client ID: {os.getenv('COGNITO_CLIENT_ID')}")
    print(f"  Region: {os.getenv('COGNITO_REGION')}")
    print()

    # Check if they match
    local_pool = settings.cognito_user_pool_id
    prod_pool = os.getenv("COGNITO_USER_POOL_ID")

    local_client = settings.cognito_client_id
    prod_client = os.getenv("COGNITO_CLIENT_ID")

    if local_pool == prod_pool:
        print("✅ User Pool IDs match")
    else:
        print("❌ User Pool IDs are different!")
        print(f"   Local: {local_pool}")
        print(f"   Prod:  {prod_pool}")

    if local_client == prod_client:
        print("✅ Client IDs match")
    else:
        print("❌ Client IDs are different!")
        print(f"   Local: {local_client}")
        print(f"   Prod:  {prod_client}")


def test_local_vs_production():
    """Test the same user in both environments."""
    print("\n🧪 Testing same user in both environments...")
    print("=" * 50)

    # Test data
    test_user = "carloss.tellezz@gmail.com"
    test_password = "Test123!"  # Replace with actual password

    # Local test
    print("🔍 Testing LOCAL environment...")
    try:
        local_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": test_user, "password": test_password},
            headers={"Content-Type": "application/json"},
        )

        if local_response.status_code == 200:
            local_data = local_response.json()
            if local_data.get("success"):
                local_su = local_data["data"]["user"].get("su")
                local_sub = local_data["data"]["user"].get("sub")
                print(f"  ✅ Local login successful")
                print(f"  Local SU: {local_su}")
                print(f"  Local SUB: {local_sub}")
            else:
                print(f"  ❌ Local login failed: {local_data.get('error')}")
        else:
            print(f"  ❌ Local request failed: {local_response.status_code}")
    except Exception as e:
        print(f"  ❌ Local test error: {e}")

    print()

    # Production test
    print("🔍 Testing PRODUCTION environment...")
    try:
        prod_response = requests.post(
            "https://eo6cj32bch.execute-api.us-east-2.amazonaws.com/prod/api/v1/auth/login",
            json={"username": test_user, "password": test_password},
            headers={
                "Content-Type": "application/json",
                "x-api-key": "09mLQ6KO1k6vadXSBQWVR8JvLMH40oPw2HIRTZyW",
            },
        )

        if prod_response.status_code == 200:
            prod_data = prod_response.json()
            if prod_data.get("success"):
                prod_su = prod_data["data"]["user"].get("su")
                prod_sub = prod_data["data"]["user"].get("sub")
                print(f"  ✅ Production login successful")
                print(f"  Production SU: {prod_su}")
                print(f"  Production SUB: {prod_sub}")

                # Compare values
                if local_su == prod_su:
                    print(f"  ✅ SU values match: {local_su}")
                else:
                    print(f"  ❌ SU values differ!")
                    print(f"     Local: {local_su}")
                    print(f"     Prod:  {prod_su}")

                if local_sub == prod_sub:
                    print(f"  ✅ SUB values match: {local_sub}")
                else:
                    print(f"  ❌ SUB values differ!")
                    print(f"     Local: {local_sub}")
                    print(f"     Prod:  {prod_sub}")
            else:
                print(f"  ❌ Production login failed: {prod_data.get('error')}")
        else:
            print(f"  ❌ Production request failed: {prod_response.status_code}")
    except Exception as e:
        print(f"  ❌ Production test error: {e}")


if __name__ == "__main__":
    compare_cognito_config()
    test_local_vs_production()
