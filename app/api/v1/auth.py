"""
Authentication API endpoints.

This module provides authentication-related endpoints including
login, registration, and token management with Cognito integration.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.auth import (
    AuthResponse,
    LoginData,
    LoginResponse,
    LoginUserData,
    MeResponse,
    PasswordReset,
    PasswordResetConfirm,
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


async def get_current_user_token(request: Request) -> str:
    """
    Extract and validate the Bearer token from the Authorization header.

    Args:
        request: FastAPI request object

    Returns:
        The access token string

    Raises:
        HTTPException: If token is missing or invalid
    """
    try:
        # Try to get the authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )

        # Check if it's a Bearer token
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected 'Bearer <token>'",
            )

        # Extract the token
        token = auth_header.replace("Bearer ", "").strip()

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is empty",
            )

        return token

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error extracting token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )


@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegister) -> AuthResponse:
    """
    Register a new user with Cognito.

    Args:
        user_data: User registration data

    Returns:
        Registration response
    """
    print(f"🔍 Register endpoint called with email: {user_data.email}")

    # 1. Validate that email doesn't already exist in Cognito
    try:
        print(f"🔍 Checking if user already exists: {user_data.email}")
        user_exists = cognito_service.check_user_exists(user_data.email)
        if user_exists:
            return AuthResponse(
                success=False,
                message="User with this email already exists. Please use a different email or try logging in.",
            )
    except Exception as e:
        print(f"⚠️ Warning: Could not verify user existence: {e}")
        # Continue with registration if we can't verify

    # 2. Prepare user attributes including custom fields
    attributes = {}
    if user_data.first_name:
        attributes["given_name"] = user_data.first_name
    if user_data.last_name:
        attributes["family_name"] = user_data.last_name
    if user_data.email:
        attributes["email"] = user_data.email
    if user_data.phone_number:
        attributes["phone_number"] = user_data.phone_number
    if user_data.plan:
        attributes["custom:plan"] = user_data.plan

    # Always set custom:su to "1" for new registrations
    attributes["custom:su"] = "1"

    print(f"🔍 Prepared attributes: {attributes}")

    # 3. Register user with Cognito
    result = None
    try:
        print("🔍 Calling cognito_service.register_user...")
        result = cognito_service.register_user(
            username=user_data.email,  # Use email as username for consistency
            email=user_data.email,
            password=user_data.password,
            attributes=attributes,
        )
        print(f"🔍 Cognito registration result: {result}")
    except Exception as e:
        print(f"❌ Registration exception: {e}")
        print(f"❌ Exception type: {type(e).__name__}")

        # Handle specific Cognito errors
        if "UsernameExistsException" in str(e):
            return AuthResponse(
                success=False,
                message="User with this email already exists. Please use a different email or try logging in.",
            )
        elif "InvalidPasswordException" in str(e):
            return AuthResponse(
                success=False,
                message="Password does not meet requirements. Please use a stronger password.",
            )

        # Only unexpected errors are 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to register user",
        )

    # 4. Send welcome email (don't fail if email fails)
    try:
        print("🔍 Sending welcome email...")
        email_sent = mailgun_service.send_welcome_email(
            user_data.email, user_data.email
        )
        print(f"🔍 Welcome email sent: {email_sent}")
    except Exception as e:
        print(f"⚠️ Warning: Failed to send welcome email: {e}")
        # Don't fail the registration if email fails

    return AuthResponse(
        success=True,
        message="User registered successfully. Please check your email for confirmation.",
        data={"email": user_data.email, "plan": user_data.plan, "su": "1"},
    )


@router.post("/confirm", response_model=AuthResponse)
async def confirm_registration(confirm_data: UserConfirm) -> AuthResponse:
    """
    Confirm user registration with verification code and disable account.

    Args:
        confirm_data: Confirmation data

    Returns:
        Confirmation response
    """
    success = None
    try:
        # 1. Confirm the registration
        success = cognito_service.confirm_registration(
            username=confirm_data.username,
            confirmation_code=confirm_data.confirmation_code,
        )

        if success:
            # 2. Disable the user account after successful confirmation
            print(
                f"🔍 Disabling user account after confirmation: {confirm_data.username}"
            )
            disable_success = cognito_service.disable_user(confirm_data.username)

            if not disable_success:
                print(
                    f"⚠️ Warning: Could not disable user account: {confirm_data.username}"
                )
                # Don't fail the confirmation if disable fails

    except Exception as e:
        # Only unexpected errors are 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Confirmation failed: {str(e)}",
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid confirmation code",
        )

    return AuthResponse(
        success=True,
        message="User confirmed successfully. Account is now disabled and requires admin approval.",
        data={"username": confirm_data.username},
    )


@router.post("/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin) -> LoginResponse:
    """
    Authenticate user and return user information with access token.

    Args:
        login_data: Login credentials

    Returns:
        Login response with user data and access token
    """
    try:
        print(f"🔍 Attempting login for user: {login_data.username}")

        # Authenticate with Cognito
        result = cognito_service.authenticate_user(
            username=login_data.username,
            password=login_data.password,
        )
        print(f"🔍 Cognito response: {result}")

        if not result:
            print(f"❌ Authentication failed for user: {login_data.username}")
            return LoginResponse(
                success=False,
                error="Invalid credentials",
            )

        # Extract tokens from Cognito response
        auth_result = result.get("AuthenticationResult", {})
        access_token = auth_result.get("AccessToken")
        refresh_token = auth_result.get("RefreshToken")
        expires_in = auth_result.get("ExpiresIn", 3600)

        if not access_token:
            return LoginResponse(
                success=False,
                error="Authentication failed",
            )

        # Get user information from Cognito with admin privileges to include custom attributes
        user_info = None
        try:
            user_info = cognito_service.get_user_info_by_token_admin(access_token)
        except Exception as e:
            print(f"⚠️ Admin user info failed, falling back to basic: {e}")
            # Fallback to basic get_user
            try:
                user_info = cognito_service.get_user_info(access_token)
            except Exception as e2:
                print(f"⚠️ Basic user info also failed: {e2}")
                # Continue with login even if user info fails

        # Extract user attributes
        user_attributes = {}
        if user_info:
            for attr in user_info.get("UserAttributes", []):
                name = attr.get("Name")
                value = attr.get("Value")
                print(f"🔍 Processing attribute: {name} = {value}")

                if name == "custom:su":
                    user_attributes["su"] = value
                elif name == "sub":
                    user_attributes["sub"] = value
                elif name == "email":
                    user_attributes["email"] = value
                elif name == "given_name":
                    user_attributes["first_name"] = value
                elif name == "family_name":
                    user_attributes["last_name"] = value
                elif name == "phone_number":
                    user_attributes["phone_number"] = value
                elif name == "custom:plan":
                    user_attributes["plan"] = value

        # Create user data
        user_data = LoginUserData(
            email=user_attributes.get("email", ""),
            first_name=user_attributes.get("first_name"),
            last_name=user_attributes.get("last_name"),
            phone_number=user_attributes.get("phone_number"),
            su=user_attributes.get("su", "1"),
            sub=user_attributes.get("sub"),
            plan=user_attributes.get("plan", "Mensual"),
            name=f"{user_attributes.get('first_name', '')} {user_attributes.get('last_name', '')}".strip()
            or None,
        )

        # Create login data
        login_data_response = LoginData(
            user=user_data,
            token=access_token,
        )

        return LoginResponse(
            success=True,
            message="Login successful",
            data=login_data_response,
        )

    except Exception as e:
        print(f"❌ Login exception: {e}")
        return LoginResponse(
            success=False,
            error=f"Login failed: {str(e)}",
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


@router.get("/me", response_model=MeResponse)
async def get_current_user(
    token: str = Depends(get_current_user_token), _cache_bust: str = None
) -> MeResponse:
    """
    Get current user information.

    Args:
        token: Bearer token

    Returns:
        Current user information with consistent response format
    """
    try:
        print(f"🔍 Getting user info for token: {token[:20]}...")

        # Get user info from Cognito with admin privileges to include custom attributes
        print(
            f"🔍 About to call admin_get_user with UserPoolId={cognito_service.user_pool_id}, Username={token}"
        )
        result = cognito_service.get_user_info_by_token_admin(token)
        print(f"🔍 Admin user info result: {result is not None}")
        print(f"🔍 User info: {result}")

        if not result:
            print("❌ No user info returned from Cognito")
            return MeResponse(
                success=False,
                error="Invalid token",
            )

        # Extract user attributes
        user_attributes = result.get("UserAttributes", [])
        user_info = {}

        for attr in user_attributes:
            name = attr.get("Name")
            value = attr.get("Value")
            print(f"🔍 Processing attribute: {name} = {value}")

            if name == "custom:su":
                user_info["su"] = value
            elif name == "sub":
                user_info["sub"] = value
            elif name == "email":
                user_info["email"] = value
            elif name == "given_name":
                user_info["first_name"] = value
            elif name == "family_name":
                user_info["last_name"] = value
            elif name == "phone_number":
                user_info["phone_number"] = value
            elif name == "custom:plan":
                user_info["plan"] = value

        # Create user data
        user_data = LoginUserData(
            email=user_info.get("email", ""),
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            phone_number=user_info.get("phone_number"),
            su=user_info.get("su", "1"),
            sub=user_info.get("sub"),
            plan=user_info.get("plan", "Mensual"),
            name=f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
            or None,
        )
        print(f"🔍 User data: {user_data}")
        return MeResponse(
            success=True,
            message="User information retrieved successfully",
            data=user_data,
        )

    except Exception as e:
        print(f"❌ Error getting user info: {e}")
        return MeResponse(
            success=False,
            error=f"Failed to get user info: {str(e)}",
        )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(password_reset: PasswordReset) -> AuthResponse:
    """
    Initiate forgot password process.

    Args:
        password_reset: Password reset request data

    Returns:
        Password reset initiation response
    """
    try:
        print(f"🔍 Forgot password request for email: {password_reset.email}")

        # Initiate forgot password process
        success = cognito_service.forgot_password(password_reset.email)

        if not success:
            return AuthResponse(
                success=False,
                message="Fallo al iniciar el restablecimiento de contraseña. Por favor, verifique su dirección de correo electrónico.",
            )

        return AuthResponse(
            success=True,
            message="Código de restablecimiento de contraseña enviado a su dirección de correo electrónico.",
            data={"email": password_reset.email},
        )

    except Exception as e:
        print(f"❌ Forgot password exception: {e}")
        return AuthResponse(
            success=False,
            message=f"Password reset failed: {str(e)}",
        )


@router.post("/reset-password", response_model=AuthResponse)
async def reset_password(password_reset_confirm: PasswordResetConfirm) -> AuthResponse:
    """
    Confirm password reset with code and new password.

    Args:
        password_reset_confirm: Password reset confirmation data

    Returns:
        Password reset confirmation response
    """
    try:
        print(
            f"🔍 Password reset confirmation request for user: {password_reset_confirm.username}"
        )

        # Confirm password reset
        success = cognito_service.confirm_forgot_password(
            username=password_reset_confirm.username,
            confirmation_code=password_reset_confirm.confirmation_code,
            new_password=password_reset_confirm.new_password,
        )

        if not success:
            return AuthResponse(
                success=False,
                message="Fallo al restablecer la contraseña. Por favor, verifique su código de confirmación.",
            )

        return AuthResponse(
            success=True,
            message="Contraseña restablecida correctamente. Ahora puede iniciar sesión con su nueva contraseña.",
        )

    except Exception as e:
        print(f"❌ Reset password exception: {e}")
        return AuthResponse(
            success=False,
            message=f"Password reset failed: {str(e)}",
        )


@router.post("/logout", response_model=AuthResponse)
async def logout_user(token: str = Depends(get_current_user_token)) -> AuthResponse:
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
