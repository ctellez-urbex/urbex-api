"""
Contact form models and schemas.

This module contains Pydantic models for contact form
requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field


class ContactForm(BaseModel):
    """Contact form request model."""

    full_name: str = Field(
        ..., description="Nombre completo", min_length=2, max_length=100
    )
    email: EmailStr = Field(..., description="Correo electrónico")
    phone: str = Field(
        ..., description="Número de teléfono", min_length=10, max_length=20
    )
    message: str = Field(
        ..., description="Contenido del mensaje", min_length=10, max_length=2000
    )


class ContactResponse(BaseModel):
    """Contact form response model."""

    success: bool = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje de respuesta")
    data: dict = Field(default_factory=dict, description="Datos de respuesta")
