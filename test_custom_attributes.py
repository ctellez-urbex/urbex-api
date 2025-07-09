#!/usr/bin/env python3
"""
Test script to verify custom attributes retrieval from Cognito.
"""

import os
import sys
from typing import Any, Dict

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.config import settings
from app.services.cognito import cognito_service


def test_custom_attributes():
    """Test custom attributes retrieval."""
    print("🔍 Testing custom attributes retrieval...")
    print(f"🔍 User Pool ID: {settings.cognito_user_pool_id}")
    print(f"🔍 Client ID: {settings.cognito_client_id}")

    # Test with a known user email
    test_email = "carloss.tellezz@gmail.com"

    try:
        # Get user info with admin privileges
        print(f"🔍 Getting user info for: {test_email}")
        user_info = cognito_service.get_user_info_admin(test_email)

        if not user_info:
            print("❌ No user info returned")
            return

        print(f"✅ User info retrieved successfully")
        print(f"🔍 Raw response: {user_info}")

        # Extract and display all attributes
        user_attributes = user_info.get("UserAttributes", [])
        print(f"\n📋 All user attributes:")
        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")
            print(f"  {name}: {value}")

        # Check for custom attributes specifically
        print(f"\n🎯 Custom attributes check:")
        custom_su = None
        custom_plan = None

        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")

            if name == "custom:su":
                custom_su = value
                print(f"  ✅ Found custom:su = {value}")
            elif name == "custom:plan":
                custom_plan = value
                print(f"  ✅ Found custom:plan = {value}")

        if not custom_su:
            print("  ❌ custom:su not found")
        if not custom_plan:
            print("  ❌ custom:plan not found")

        # Test the processing logic
        print(f"\n🔄 Testing processing logic:")
        processed_attributes = {}

        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")

            if name == "email":
                processed_attributes["email"] = value
            elif name == "given_name":
                processed_attributes["first_name"] = value
            elif name == "family_name":
                processed_attributes["last_name"] = value
            elif name == "phone_number":
                processed_attributes["phone_number"] = value
            elif name == "custom:su":
                processed_attributes["su"] = value
            elif name == "custom:plan":
                processed_attributes["plan"] = value
            elif name == "sub":
                # Only use sub if custom:su is not present
                if "su" not in processed_attributes:
                    processed_attributes["su"] = value

        print(f"  Processed attributes: {processed_attributes}")

        # Check final values
        final_su = processed_attributes.get("su")
        final_plan = processed_attributes.get("plan", "Mensual")

        print(f"\n📊 Final values:")
        print(f"  su: {final_su}")
        print(f"  plan: {final_plan}")

        if final_su == custom_su:
            print(f"  ✅ SU value is correct (from custom:su)")
        else:
            print(f"  ❌ SU value mismatch: expected {custom_su}, got {final_su}")

        if final_plan == custom_plan:
            print(f"  ✅ Plan value is correct (from custom:plan)")
        else:
            print(f"  ❌ Plan value mismatch: expected {custom_plan}, got {final_plan}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_custom_attributes()
