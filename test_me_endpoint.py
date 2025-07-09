#!/usr/bin/env python3
"""
Test script to verify the /me endpoint returns custom attributes correctly.
"""

import json
from typing import Any, Dict

import requests


def test_me_endpoint():
    """Test the /me endpoint with a valid token."""
    base_url = "http://localhost:8000"

    # First, let's try to login to get a valid token
    print("🔍 Attempting login...")
    login_data = {"username": "carloss.tellezz@gmail.com", "password": "Test123!"}

    try:
        login_response = requests.post(
            f"{base_url}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
        )

        print(f"🔍 Login response status: {login_response.status_code}")
        print(f"🔍 Login response: {login_response.text}")

        if login_response.status_code == 200:
            login_result = login_response.json()
            if login_result.get("success"):
                token = login_result["data"]["token"]
                print(f"✅ Login successful, got token: {token[:20]}...")

                # Now test the /me endpoint
                print("\n🔍 Testing /me endpoint...")
                me_response = requests.get(
                    f"{base_url}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {token}"},
                )

                print(f"🔍 /me response status: {me_response.status_code}")
                print(f"🔍 /me response: {me_response.text}")

                if me_response.status_code == 200:
                    me_result = me_response.json()
                    if me_result.get("success"):
                        user_data = me_result["data"]
                        print(f"\n📊 User data from /me endpoint:")
                        print(f"  Email: {user_data.get('email')}")
                        print(f"  First Name: {user_data.get('first_name')}")
                        print(f"  Last Name: {user_data.get('last_name')}")
                        print(f"  SU: {user_data.get('su')}")
                        print(f"  Plan: {user_data.get('plan')}")
                        print(f"  Phone: {user_data.get('phone_number')}")

                        # Check if custom attributes are present
                        if user_data.get("su") == "2":
                            print("  ✅ SU value is correct (from custom:su)")
                        else:
                            print(
                                f"  ❌ SU value incorrect: expected '2', got '{user_data.get('su')}'"
                            )

                        if user_data.get("plan") == "Mensual":
                            print("  ✅ Plan value is correct (from custom:plan)")
                        else:
                            print(
                                f"  ❌ Plan value incorrect: expected 'Mensual', got '{user_data.get('plan')}'"
                            )
                    else:
                        print(
                            f"❌ /me endpoint returned error: {me_result.get('error')}"
                        )
                else:
                    print(
                        f"❌ /me endpoint failed with status: {me_response.status_code}"
                    )
            else:
                print(f"❌ Login failed: {login_result.get('error')}")
        else:
            print(f"❌ Login request failed with status: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to server. Make sure the server is running on http://localhost:8000"
        )
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_me_endpoint()
