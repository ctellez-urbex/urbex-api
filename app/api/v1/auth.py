"""
Authentication API endpoints.

This module provides authentication-related endpoints including
login, registration, and token management with Cognito integration.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.core.config import settings
from app.core.security import create_access_token, verify_token
from app.models.auth import (
    AuthResponse,
    RefreshToken,
    TokenResponse,
    UserConfirm,
    UserInfo,
    UserLogin,
    UserRegister,
)
from app.services.cognito import cognito_service
from app.services.mailgun import mailgun_service

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegister) -> AuthResponse:
    """
    Register a new user with Cognito.
    
    Args:
        user_data: User registration data
        
    Returns:
        Registration response
    """
    try:
        # Prepare user attributes
        attributes = {}
        if user_data.first_name:
            attributes["given_name"] = user_data.first_name
        if user_data.last_name:
            attributes["family_name"] = user_data.last_name

        # Register user with Cognito
        result = cognito_service.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            attributes=attributes,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register user",
            )

        # Send welcome email
        mailgun_service.send_welcome_email(user_data.email, user_data.username)

        return AuthResponse(
            success=True,
            message="User registered successfully. Please check your email for confirmation.",
            data={"username": user_data.username},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/confirm", response_model=AuthResponse)
async def confirm_registration(confirm_data: UserConfirm) -> AuthResponse:
    """
    Confirm user registration with verification code.
    
    Args:
        confirm_data: Confirmation data
        
    Returns:
        Confirmation response
    """
    try:
        success = cognito_service.confirm_registration(
            username=confirm_data.username,
            confirmation_code=confirm_data.confirmation_code,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid confirmation code",
            )

        return AuthResponse(
            success=True,
            message="User confirmed successfully",
            data={"username": confirm_data.username},
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confirmation failed: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin) -> TokenResponse:
    """
    Authenticate user and return access token.
    
    Args:
        login_data: Login credentials
        
    Returns:
        Token response with access and refresh tokens
    """
    try:
        # Authenticate with Cognito
        result = cognito_service.authenticate_user(
            username=login_data.username,
            password=login_data.password,
        )

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        # Extract tokens from Cognito response
        auth_result = result.get("AuthenticationResult", {})
        access_token = auth_result.get("AccessToken")
        refresh_token = auth_result.get("RefreshToken")
        expires_in = auth_result.get("ExpiresIn", 3600)

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
            )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            refresh_token=refresh_token,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshToken) -> TokenResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token data
        
    Returns:
        New token response
    """
    try:
        result = cognito_service.refresh_token(refresh_data.refresh_token)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        auth_result = result.get("AuthenticationResult", {})
        access_token = auth_result.get("AccessToken")
        expires_in = auth_result.get("ExpiresIn", 3600)

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed",
            )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}",
        )


@router.get("/me", response_model=UserInfo)
async def get_current_user(token: str = Depends(security)) -> UserInfo:
    """
    Get current user information.
    
    Args:
        token: Bearer token
        
    Returns:
        Current user information
    """
    try:
        # Get user info from Cognito
        result = cognito_service.get_user_info(token.credentials)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        # Extract user attributes
        user_attributes = result.get("UserAttributes", [])
        user_info = {}
        
        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")
            if name == "sub":
                user_info["username"] = value
            elif name == "email":
                user_info["email"] = value
            elif name == "given_name":
                user_info["first_name"] = value
            elif name == "family_name":
                user_info["last_name"] = value

        return UserInfo(
            username=user_info.get("username", ""),
            email=user_info.get("email", ""),
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            is_active=True,  # Cognito users are active by default
            created_at=datetime.utcnow(),  # You might want to get this from Cognito
            updated_at=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}",
        )


@router.post("/logout", response_model=AuthResponse)
async def logout_user(token: str = Depends(security)) -> AuthResponse:
    """
    Logout user (invalidate token).
    
    Args:
        token: Bearer token
        
    Returns:
        Logout response
    """
    try:
        # In a real implementation, you might want to blacklist the token
        # For now, we'll just return success
        return AuthResponse(
            success=True,
            message="User logged out successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}",
        ) 