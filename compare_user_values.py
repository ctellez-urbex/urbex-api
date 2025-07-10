#!/usr/bin/env python3
"""
Script to compare su and plan values for the same user between local and production.
"""

import json
import os
import sys
from typing import Any, Dict

import requests

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.config import settings
from app.services.cognito import cognito_service


def get_user_from_cognito_directly(email: str):
    """Get user directly from Cognito to verify attributes."""
    print(f"🔍 Getting user directly from Cognito: {email}")

    try:
        user_info = cognito_service.get_user_info_admin(email)
        if not user_info:
            print("❌ No user found in Cognito")
            return None

        user_attributes = user_info.get("UserAttributes", [])
        print(f"📋 User attributes from Cognito:")

        su_value = None
        plan_value = None
        sub_value = None

        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")
            print(f"  {name}: {value}")

            if name == "custom:su":
                su_value = value
            elif name == "custom:plan":
                plan_value = value
            elif name == "sub":
                sub_value = value

        return {
            "su": su_value,
            "plan": plan_value,
            "sub": sub_value,
            "username": user_info.get("Username"),
        }
    except Exception as e:
        print(f"❌ Error getting user from Cognito: {e}")
        return None


def test_api_endpoint(base_url: str, api_key: str = None, environment: str = "LOCAL"):
    """Test API endpoint and return user data."""
    print(f"\n🔍 Testing {environment} API endpoint...")

    # Test credentials (replace with actual credentials)
    test_user = "carloss.tellezz@gmail.com"
    test_password = "4p0C4l1ps1s"  # Replace with actual password

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["x-api-key"] = api_key

    try:
        # Login
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json={"username": test_user, "password": test_password},
            headers=headers,
        )

        print(f"  Login status: {login_response.status_code}")

        if login_response.status_code == 200:
            login_data = login_response.json()
            print(f"  Login response: {json.dumps(login_data, indent=2)}")

            if login_data.get("success"):
                token = login_data["data"]["token"]
                user_data = login_data["data"]["user"]

                print(f"  ✅ Login successful")
                print(f"  User data from login:")
                print(f"    Email: {user_data.get('email')}")
                print(f"    SU: {user_data.get('su')}")
                print(f"    Plan: {user_data.get('plan')}")
                print(f"    SUB: {user_data.get('sub')}")

                # Test /me endpoint
                print(f"\n  🔍 Testing /me endpoint...")
                me_response = requests.get(
                    f"{base_url}/api/v1/auth/me",
                    headers={**headers, "Authorization": f"Bearer {token}"},
                )

                print(f"  /me status: {me_response.status_code}")

                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print(f"  /me response: {json.dumps(me_data, indent=2)}")

                    if me_data.get("success"):
                        me_user_data = me_data["data"]
                        print(f"  ✅ /me successful")
                        print(f"  User data from /me:")
                        print(f"    Email: {me_user_data.get('email')}")
                        print(f"    SU: {me_user_data.get('su')}")
                        print(f"    Plan: {me_user_data.get('plan')}")
                        print(f"    SUB: {me_user_data.get('sub')}")

                        return {
                            "login_su": user_data.get("su"),
                            "login_plan": user_data.get("plan"),
                            "login_sub": user_data.get("sub"),
                            "me_su": me_user_data.get("su"),
                            "me_plan": me_user_data.get("plan"),
                            "me_sub": me_user_data.get("sub"),
                            "email": user_data.get("email"),
                        }
                    else:
                        print(f"  ❌ /me failed: {me_data.get('error')}")
                else:
                    print(f"  ❌ /me request failed: {me_response.status_code}")
                    print(f"  Response: {me_response.text}")
            else:
                print(f"  ❌ Login failed: {login_data.get('error')}")
        else:
            print(f"  ❌ Login request failed: {login_response.status_code}")
            print(f"  Response: {login_response.text}")

    except Exception as e:
        print(f"  ❌ Error testing {environment}: {e}")

    return None


def main():
    """Main comparison function."""
    print("🔍 Comparing user values between local and production")
    print("=" * 60)

    # Get user directly from Cognito
    cognito_user = get_user_from_cognito_directly("carloss.tellezz@gmail.com")

    if cognito_user:
        print(f"\n📊 Direct Cognito values:")
        print(f"  SU: {cognito_user['su']}")
        print(f"  Plan: {cognito_user['plan']}")
        print(f"  SUB: {cognito_user['sub']}")
        print(f"  Username: {cognito_user['username']}")

    # Test local environment
    local_data = test_api_endpoint("http://localhost:8000", environment="LOCAL")

    # Test production environment
    prod_data = test_api_endpoint(
        "https://eo6cj32bch.execute-api.us-east-2.amazonaws.com/prod",
        api_key="09mLQ6KO1k6vadXSBQWVR8JvLMH40oPw2HIRTZyW",
        environment="PRODUCTION",
    )

    # Compare results
    print(f"\n📊 COMPARISON RESULTS")
    print("=" * 60)

    if cognito_user and local_data and prod_data:
        print(f"🔍 Cognito Direct vs Local vs Production:")
        print(f"  SU:")
        print(f"    Cognito: {cognito_user['su']}")
        print(f"    Local Login: {local_data['login_su']}")
        print(f"    Local /me: {local_data['me_su']}")
        print(f"    Prod Login: {prod_data['login_su']}")
        print(f"    Prod /me: {prod_data['me_su']}")
        print()

        print(f"  Plan:")
        print(f"    Cognito: {cognito_user['plan']}")
        print(f"    Local Login: {local_data['login_plan']}")
        print(f"    Local /me: {local_data['me_plan']}")
        print(f"    Prod Login: {prod_data['login_plan']}")
        print(f"    Prod /me: {prod_data['me_plan']}")
        print()

        print(f"  SUB:")
        print(f"    Cognito: {cognito_user['sub']}")
        print(f"    Local Login: {local_data['login_sub']}")
        print(f"    Local /me: {local_data['me_sub']}")
        print(f"    Prod Login: {prod_data['login_sub']}")
        print(f"    Prod /me: {prod_data['me_sub']}")
        print()

        # Check if same user
        if local_data["login_sub"] == prod_data["login_sub"]:
            print("✅ Same user in both environments (SUB matches)")
        else:
            print("❌ Different users in environments (SUB differs)")

        # Check SU consistency
        if local_data["login_su"] == prod_data["login_su"]:
            print("✅ SU values match between environments")
        else:
            print("❌ SU values differ between environments")

        # Check Plan consistency
        if local_data["login_plan"] == prod_data["login_plan"]:
            print("✅ Plan values match between environments")
        else:
            print("❌ Plan values differ between environments")


if __name__ == "__main__":
    main()
