"""
Contact form API endpoints.

This module provides contact form functionality for
landing page integration.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.models.contact import ContactForm, ContactResponse
from app.services.mailgun import mailgun_service

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post("/", response_model=ContactResponse)
async def submit_contact_form(contact_data: ContactForm) -> ContactResponse:
    """
    Submit contact form from landing page.

    Args:
        contact_data: Contact form data

    Returns:
        Contact form response
    """
    try:
        # Verificar configuración de Mailgun
        if not settings.mailgun_api_key or not settings.mailgun_domain:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email service not configured",
            )

        # Verificar que el email del admin esté configurado
        if not settings.admin_email:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Admin email not configured",
            )

        # Enviar email de contacto
        success = mailgun_service.send_contact_form_email(
            full_name=contact_data.full_name,
            email=contact_data.email,
            phone=contact_data.phone,
            message=contact_data.message,
            admin_email=settings.admin_email,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send contact email",
            )

        return ContactResponse(
            success=True,
            message="Mensaje enviado exitosamente. Te responderemos pronto.",
            data={
                "full_name": contact_data.full_name,
                "email": contact_data.email,
                "timestamp": datetime.now().isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing contact form: {str(e)}",
        )
