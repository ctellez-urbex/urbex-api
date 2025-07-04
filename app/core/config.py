"""
Application configuration using Pydantic settings.

This module provides centralized configuration management with environment
variable support and validation.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application settings
    app_name: str = Field(default="Urbex API", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # AWS settings
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS access key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS secret access key")
    
    # Cognito settings
    cognito_user_pool_id: Optional[str] = Field(default=None, description="Cognito user pool ID")
    cognito_client_id: Optional[str] = Field(default=None, description="Cognito client ID")
    cognito_client_secret: Optional[str] = Field(default=None, description="Cognito client secret")
    cognito_region: Optional[str] = Field(default=None, description="Cognito region")
    
    # Mailgun settings
    mailgun_api_key: Optional[str] = Field(default=None, description="Mailgun API key")
    mailgun_domain: Optional[str] = Field(default=None, description="Mailgun domain")
    mailgun_base_url: str = Field(default="https://api.mailgun.net/v3", description="Mailgun base URL")
    admin_email: Optional[str] = Field(default=None, description="Admin email for contact form notifications")
    
    # Database settings (if needed)
    database_url: Optional[str] = Field(default=None, description="Database connection URL")
    
    # Security settings
    secret_key: str = Field(default="your-secret-key-here", description="Secret key for JWT")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration in minutes")
    
    # CORS settings
    allowed_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")
    allowed_methods: list[str] = Field(default=["*"], description="Allowed CORS methods")
    allowed_headers: list[str] = Field(default=["*"], description="Allowed CORS headers")

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings() 