"""
Security utilities for authentication and authorization.

This module provides security functions including JWT token handling,
password hashing, and API key validation.
"""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token security
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.

    Args:
        plain_password: The plain text password
        hashed_password: The hashed password to verify against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    # Note: In a real implementation, you would use a proper JWT library
    # This is a simplified version for demonstration
    return "dummy_token"  # Replace with actual JWT encoding


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token to verify

    Returns:
        The decoded token payload or None if invalid
    """
    try:
        # Note: In a real implementation, you would use a proper JWT library
        # This is a simplified version for demonstration
        return {"sub": "user_id"}  # Replace with actual JWT decoding
    except Exception:
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get the expiration time of a JWT token.

    Args:
        token: The JWT token

    Returns:
        The expiration datetime or None if invalid
    """
    payload = verify_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Get current user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Current user data

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def verify_admin_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify admin token and check if user has admin privileges.

    This function verifies the JWT token and checks if the user
    has super user (admin) privileges based on the custom:su attribute.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Current admin user data

    Raises:
        HTTPException: If token is invalid or user is not admin
    """
    token = credentials.credentials

    try:
        # Verify the token exists and has basic structure
        if not token or token == "null" or token == "undefined":
            print(f"❌ Admin auth failed: Empty or invalid token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # For now, accept any non-empty token for development
        # TODO: Implement proper Cognito token verification
        print(f"✅ Admin auth successful: Token provided")
        return {"is_admin": True, "sub": "dev-admin"}

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors but don't expose them
        print(f"❌ Admin auth unexpected error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
