#!/usr/bin/env python3
"""
Simple test script to isolate registration issue.
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()


def test_registration_endpoint():
    """Test the registration endpoint directly."""
    print("🔍 Testing Registration Endpoint")
    print("=" * 50)

    url = "http://localhost:8000/api/v1/auth/register"
    data = {
        "username": "testuser6@example.com",
        "email": "testuser6@example.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
    }

    headers = {"Content-Type": "application/json"}

    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print()

    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")

    except Exception as e:
        print(f"❌ Request error: {e}")


if __name__ == "__main__":
    test_registration_endpoint()
