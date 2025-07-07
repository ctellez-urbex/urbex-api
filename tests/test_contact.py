"""
Tests for contact form endpoints.

This module contains tests for the contact form functionality
including form submission and email sending.
"""

import pytest
from unittest.mock import patch
from fastapi import status


class TestContactEndpoints:
    """Test class for contact form endpoints."""

    def test_submit_contact_form_success(self, client: pytest.FixtureRequest) -> None:
        """Test successful contact form submission."""
        with patch("app.api.v1.contact.mailgun_service") as mock_mailgun:
            # Mock successful email sending
            mock_mailgun.send_contact_form_email.return_value = True

            contact_data = {
                "full_name": "Juan Pérez",
                "email": "juan.perez@example.com",
                "phone": "+1234567890",
                "message": "Hola, me gustaría obtener más información sobre sus servicios."
            }

            response = client.post("/api/v1/contact/", json=contact_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert "Mensaje enviado exitosamente" in data["message"]
            assert data["data"]["full_name"] == contact_data["full_name"]
            assert data["data"]["email"] == contact_data["email"]

    def test_submit_contact_form_email_failure(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission when email sending fails."""
        with patch("app.api.v1.contact.mailgun_service") as mock_mailgun:
            # Mock failed email sending
            mock_mailgun.send_contact_form_email.return_value = False
            
            contact_data = {
                "full_name": "María García",
                "email": "maria.garcia@example.com",
                "phone": "+0987654321",
                "message": "Necesito ayuda con mi proyecto."
            }
            
            response = client.post("/api/v1/contact/", json=contact_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Failed to send contact email" in data["detail"]

    def test_submit_contact_form_admin_email_not_configured(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission when admin email is not configured."""
        with patch("app.api.v1.contact.settings") as mock_settings:
            # Mock admin email not configured
            mock_settings.admin_email = None
            
            contact_data = {
                "full_name": "Carlos López",
                "email": "carlos.lopez@example.com",
                "phone": "+1122334455",
                "message": "Consulta sobre precios."
            }
            
            response = client.post("/api/v1/contact/", json=contact_data)
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Admin email not configured" in data["detail"]

    def test_submit_contact_form_invalid_data(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission with invalid data."""
        # Test with missing required fields
        contact_data = {
            "full_name": "Ana",  # Missing email, phone, message
        }
        
        response = client.post("/api/v1/contact/", json=contact_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_contact_form_invalid_email(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission with invalid email."""
        contact_data = {
            "full_name": "Pedro Rodríguez",
            "email": "invalid-email",  # Invalid email format
            "phone": "+1234567890",
            "message": "Mensaje de prueba."
        }
        
        response = client.post("/api/v1/contact/", json=contact_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_contact_form_name_too_short(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission with name too short."""
        contact_data = {
            "full_name": "A",  # Too short (min 2 characters)
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "Mensaje de prueba."
        }
        
        response = client.post("/api/v1/contact/", json=contact_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_contact_form_message_too_short(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission with message too short."""
        contact_data = {
            "full_name": "Roberto Silva",
            "email": "roberto@example.com",
            "phone": "+1234567890",
            "message": "Hola",  # Too short (min 10 characters)
        }
        
        response = client.post("/api/v1/contact/", json=contact_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_contact_form_phone_too_short(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission with phone too short."""
        contact_data = {
            "full_name": "Laura Torres",
            "email": "laura@example.com",
            "phone": "123",  # Too short (min 10 characters)
            "message": "Mensaje de prueba con suficiente contenido."
        }
        
        response = client.post("/api/v1/contact/", json=contact_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_submit_contact_form_with_special_characters(self, client: pytest.FixtureRequest) -> None:
        """Test contact form submission with special characters in message."""
        with patch("app.api.v1.contact.mailgun_service") as mock_mailgun:
            # Mock successful email sending
            mock_mailgun.send_contact_form_email.return_value = True
            
            contact_data = {
                "full_name": "José María",
                "email": "jose.maria@example.com",
                "phone": "+1234567890",
                "message": "Hola! ¿Cómo están? Necesito información sobre:\n- Servicios\n- Precios\n- Disponibilidad\n\nGracias! 😊"
            }
            
            response = client.post("/api/v1/contact/", json=contact_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True 