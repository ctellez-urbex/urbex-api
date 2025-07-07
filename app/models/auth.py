"""
Authentication models and schemas.

This module contains Pydantic models for authentication-related
requests and responses.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """User login request model."""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password", min_length=6)


class UserRegister(BaseModel):
    """User registration request model."""

    username: str = Field(..., description="Username", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=8)
    first_name: Optional[str] = Field(
        None, description="User's first name", max_length=50
    )
    last_name: Optional[str] = Field(
        None, description="User's last name", max_length=50
    )


class UserConfirm(BaseModel):
    """User confirmation request model."""

    username: str = Field(..., description="Username")
    confirmation_code: str = Field(..., description="Confirmation code")


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(None, description="Refresh token")


class UserInfo(BaseModel):
    """User information response model."""

    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="Account creation date")
    updated_at: Optional[datetime] = Field(None, description="Last update date")


class PasswordReset(BaseModel):
    """Password reset request model."""

    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""

    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., description="New password", min_length=8)


class RefreshToken(BaseModel):
    """Refresh token request model."""

    refresh_token: str = Field(..., description="Refresh token")


class AuthResponse(BaseModel):
    """Authentication response model."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
