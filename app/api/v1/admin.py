"""
Admin API endpoints for user management.

This module provides administrative endpoints for managing users
in the Cognito User Pool.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.security import verify_admin_token
from app.models.admin import (
    AdminResponse,
    UserInfo,
    UserListRequest,
    UserListResponse,
    UserStatus,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)
from app.services.cognito import cognito_service

router = APIRouter(prefix="/admin", tags=["admin"])


def _parse_user_attributes(user_attributes: list) -> Dict[str, Any]:
    """Parse Cognito user attributes into a dictionary."""
    attributes = {}
    for attr in user_attributes:
        name = attr.get("Name", "")
        value = attr.get("Value", "")
        print(f"🔍 Debug: Attribute - Name: '{name}', Value: '{value}'")
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
        elif name == "UserStatus":
            attributes["UserStatus"] = value
        elif name == "UserCreateDate":
            attributes["UserCreateDate"] = value.isoformat() if value else None
        elif name == "UserLastModifiedDate":
            attributes["UserLastModifiedDate"] = value

    return attributes


def _filter_users_by_search(users: list, search: str) -> list:
    """Filter users by search term (contains search)."""
    if not search:
        return users

    search_lower = search.lower()
    filtered_users = []
    seen_usernames = set()  # To avoid duplicates

    for user in users:
        username = user.get("Username", "")

        # Skip if we've already seen this user
        if username in seen_usernames:
            continue

        # Get raw attributes directly from Cognito response
        raw_attributes = user.get("Attributes", [])
        print(f"🔍 Debug: Raw attributes: {raw_attributes}")

        # Extract values from raw attributes
        email = ""
        given_name = ""
        family_name = ""
        phone_number = ""
        user_status = ""
        user_create_date = ""
        user_last_modified_date = ""

        for attr in raw_attributes:
            name = attr.get("Name", "")
            value = attr.get("Value", "")

            if name == "email":
                email = value.lower()
            elif name == "given_name":
                given_name = value.lower()
            elif name == "family_name":
                family_name = value.lower()
            elif name == "phone_number":
                phone_number = value.lower()
            elif name == "UserStatus":
                user_status = value
            elif name == "UserCreateDate":
                user_create_date = value
            elif name == "UserLastModifiedDate":
                user_last_modified_date = value

        # Check if search term is contained in any of these fields (OR condition)
        if (
            search_lower in email
            or search_lower in given_name
            or search_lower in family_name
            or search_lower in phone_number
            or search_lower in user_status
            or search_lower in user_create_date
            or search_lower in user_last_modified_date
        ):
            filtered_users.append(user)
            seen_usernames.add(username)  # Mark as seen

    return filtered_users


@router.post("/users")
async def list_users(
    request: UserListRequest, current_user: Dict[str, Any] = Depends(verify_admin_token)
):
    """
    List users with filtering.

    This endpoint allows administrators to list users with search functionality.
    Returns all users that match the filter criteria.
    """
    try:
        # Extract filter parameters
        search = request.filter

        # Get ALL users from Cognito (handles pagination automatically)
        response = cognito_service.list_all_users()

        if not response:
            raise HTTPException(status_code=500, detail="Failed to retrieve users")

        # Filter users by search term
        filtered_users = _filter_users_by_search(response.get("Users", []), search)

        users = []
        for user in filtered_users:
            attributes = _parse_user_attributes(user.get("Attributes", []))

            # Create user object with exact fields requested
            user_data = {
                "user_id": attributes.get("user_id", ""),
                "email": attributes.get("email", ""),
                "emailVerified": attributes.get("email_verified", False),
                "first_name": attributes.get("first_name"),
                "last_name": attributes.get("last_name"),
                "phone_number": attributes.get("phone_number"),
                "plan": attributes.get("plan"),
                "su": attributes.get("su"),
                "status": UserStatus(attributes.get("UserStatus", "CONFIRMED")),
                "email_verified": attributes.get("email_verified", False),
                "createdAt": user.get("UserCreateDate", "").isoformat()
                if user.get("UserCreateDate")
                else None,
                "lastLogin": user.get("UserLastModifiedDate", "").isoformat()
                if user.get("UserLastModifiedDate")
                else None,
            }
            users.append(user_data)

        return {
            "success": True,
            "message": "Users retrieved successfully",
            "data": {"users": users, "total": len(users)},
        }

    except Exception as e:
        print(f"❌ Error in list_users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/email/{email}", response_model=AdminResponse)
async def get_user(
    email: str, current_user: Dict[str, Any] = Depends(verify_admin_token)
):
    """
    Get detailed information about a specific user.

    This endpoint retrieves complete user information including
    custom attributes and status.
    """
    try:
        # Get user from Cognito
        response = cognito_service.get_user_by_email(email)

        if not response:
            raise HTTPException(status_code=404, detail="User not found")

        # Parse user attributes
        attributes = _parse_user_attributes(response.get("UserAttributes", []))

        user_data = {
            "user_id": attributes.get("user_id", ""),
            "email": attributes.get("email", ""),
            "first_name": attributes.get("first_name"),
            "last_name": attributes.get("last_name"),
            "phone_number": attributes.get("phone_number"),
            "plan": attributes.get("plan"),
            "su": attributes.get("su"),
            "status": UserStatus(response.get("UserStatus", "CONFIRMED")),
            "email_verified": attributes.get("email_verified", False),
            "createdAt": response.get("UserCreateDate", "").isoformat()
            if response.get("UserCreateDate")
            else None,
            "lastLogin": response.get("UserLastModifiedDate", "").isoformat()
            if response.get("UserLastModifiedDate")
            else None,
        }

        return {
            "success": True,
            "message": "User retrieved successfully",
            "data": user_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/user/{user_id}", response_model=AdminResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(verify_admin_token),
):
    """
    Update user information.

    This endpoint allows administrators to update user attributes
    including name, phone number, plan, and super user status.
    """
    try:
        # Prepare attributes to update
        attributes = {}

        if user_data.first_name is not None:
            attributes["given_name"] = user_data.first_name
        if user_data.last_name is not None:
            attributes["family_name"] = user_data.last_name
        if user_data.phone_number is not None:
            attributes["phone_number"] = user_data.phone_number
        if user_data.plan is not None:
            attributes["custom:plan"] = user_data.plan
        if user_data.su is not None:
            attributes["custom:su"] = user_data.su

        if not attributes:
            raise HTTPException(status_code=400, detail="No attributes to update")

        # Update user attributes
        success = cognito_service.update_user_attributes(user_id, attributes)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user")

        return AdminResponse(
            success=True,
            message="User updated successfully",
            data={"user_id": user_id, "updated_attributes": list(attributes.keys())},
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in update_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/user/{user_id}/status", response_model=AdminResponse)
async def update_user_status(
    user_id: str,
    status_data: UserStatusUpdateRequest,
    current_user: Dict[str, Any] = Depends(verify_admin_token),
):
    """
    Update user status (enable/disable).

    This endpoint allows administrators to enable or disable user accounts.
    """
    try:
        success = False

        if status_data.status == UserStatus.ENABLED:
            success = cognito_service.enable_user(user_id)
        elif status_data.status == UserStatus.DISABLED:
            success = cognito_service.disable_user(user_id)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Only ENABLED and DISABLED are supported",
            )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user status")

        return AdminResponse(
            success=True,
            message=f"User status updated to {status_data.status.value}",
            data={"user_id": user_id, "status": status_data.status.value},
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in update_user_status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
