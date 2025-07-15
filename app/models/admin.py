from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserStatus(str, Enum):
    """User status enumeration"""

    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UNCONFIRMED = "UNCONFIRMED"
    CONFIRMED = "CONFIRMED"


class UserListRequest(BaseModel):
    """Request model for listing users with filters"""

    filter: Optional[str] = Field(
        default="", description="Search term for filtering users"
    )


class UserUpdateRequest(BaseModel):
    """Request model for updating user information"""

    first_name: Optional[str] = Field(default=None, description="User's first name")
    last_name: Optional[str] = Field(default=None, description="User's last name")
    phone_number: Optional[str] = Field(default=None, description="User's phone number")
    plan: Optional[str] = Field(default=None, description="User's plan")
    su: Optional[str] = Field(default=None, description="Super user flag")


class UserStatusUpdateRequest(BaseModel):
    """Request model for updating user status"""

    status: UserStatus = Field(description="New user status")


class UserInfo(BaseModel):
    """User information model"""

    user_id: str = Field(description="Cognito User ID")
    email: str = Field(description="User's email address")
    first_name: Optional[str] = Field(default=None, description="User's first name")
    last_name: Optional[str] = Field(default=None, description="User's last name")
    phone_number: Optional[str] = Field(default=None, description="User's phone number")
    plan: Optional[str] = Field(default=None, description="User's plan")
    su: Optional[str] = Field(default=None, description="Super user flag")
    status: UserStatus = Field(description="User status")
    email_verified: bool = Field(description="Whether email is verified")
    created_at: Optional[str] = Field(default=None, description="User creation date")
    updated_at: Optional[str] = Field(default=None, description="Last update date")


class UserListResponse(BaseModel):
    """Response model for user list"""

    users: List[UserInfo] = Field(description="List of users")
    total: int = Field(description="Total number of users")
    page: int = Field(description="Current page")
    limit: int = Field(description="Users per page")
    pages: int = Field(description="Total number of pages")


class AdminResponse(BaseModel):
    """Generic admin response model"""

    success: bool = Field(description="Operation success status")
    message: str = Field(description="Response message")
    data: Optional[dict] = Field(default=None, description="Response data")
