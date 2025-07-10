#!/usr/bin/env python3
"""
Test script to verify that su and sub are handled correctly as different fields.
"""

import os
import sys
from typing import Any, Dict

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.config import settings
from app.services.cognito import cognito_service


def test_su_sub_difference():
    """Test that su and sub are handled as different fields."""
    print("🔍 Testing su and sub field difference...")
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

        # Extract and display all attributes
        user_attributes = user_info.get("UserAttributes", [])
        print(f"\n📋 All user attributes:")
        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")
            print(f"  {name}: {value}")

        # Check for specific attributes
        print(f"\n🎯 Specific attributes check:")
        custom_su = None
        sub_value = None
        custom_plan = None

        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")

            if name == "custom:su":
                custom_su = value
                print(f"  ✅ Found custom:su = {value}")
            elif name == "sub":
                sub_value = value
                print(f"  ✅ Found sub = {value}")
            elif name == "custom:plan":
                custom_plan = value
                print(f"  ✅ Found custom:plan = {value}")

        if not custom_su:
            print("  ❌ custom:su not found")
        if not sub_value:
            print("  ❌ sub not found")
        if not custom_plan:
            print("  ❌ custom:plan not found")

        # Test the processing logic
        print(f"\n🔄 Testing processing logic:")
        processed_attributes = {}

        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")

            if name == "custom:su":
                processed_attributes["su"] = value
            elif name == "sub":
                processed_attributes["sub"] = value
            elif name == "email":
                processed_attributes["email"] = value
            elif name == "given_name":
                processed_attributes["first_name"] = value
            elif name == "family_name":
                processed_attributes["last_name"] = value
            elif name == "phone_number":
                processed_attributes["phone_number"] = value
            elif name == "custom:plan":
                processed_attributes["plan"] = value

        print(f"  Processed attributes: {processed_attributes}")

        # Check final values
        final_su = processed_attributes.get("su", "1")
        final_sub = processed_attributes.get("sub")
        final_plan = processed_attributes.get("plan", "Mensual")

        print(f"\n📊 Final values:")
        print(f"  su: {final_su}")
        print(f"  sub: {final_sub}")
        print(f"  plan: {final_plan}")

        # Verify they are different
        if final_su == custom_su:
            print(f"  ✅ SU value is correct (from custom:su)")
        else:
            print(f"  ❌ SU value mismatch: expected {custom_su}, got {final_su}")

        if final_sub == sub_value:
            print(f"  ✅ SUB value is correct (from sub)")
        else:
            print(f"  ❌ SUB value mismatch: expected {sub_value}, got {final_sub}")

        if final_plan == custom_plan:
            print(f"  ✅ Plan value is correct (from custom:plan)")
        else:
            print(f"  ❌ Plan value mismatch: expected {custom_plan}, got {final_plan}")

        # Verify su and sub are different
        if final_su != final_sub:
            print(f"  ✅ SU and SUB are correctly different values")
        else:
            print(f"  ❌ SU and SUB should be different but are the same")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_su_sub_difference()
