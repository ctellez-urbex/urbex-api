"""
Mailgun email service integration.

This module provides email functionality using Mailgun API
for sending transactional emails.
"""

from datetime import datetime
import requests
from typing import Any, Dict, List, Optional

from app.core.config import settings


class MailgunService:
    """Service class for Mailgun email operations."""

    def __init__(self) -> None:
        """Initialize the Mailgun service."""
        self.api_key = settings.mailgun_api_key
        self.domain = settings.mailgun_domain
        self.base_url = settings.mailgun_base_url
        self.auth = ("api", self.api_key) if self.api_key else None

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an email using Mailgun.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            text: Plain text content
            html: HTML content
            from_email: Sender email (defaults to domain)
            cc: CC recipients
            bcc: BCC recipients
            reply_to: Reply-to email address
            custom_data: Custom variables for templates
            
        Returns:
            API response or None if failed
        """
        if not self.api_key or not self.domain:
            print("Mailgun API key or domain not configured")
            return None

        try:
            data = {
                "from": from_email or f"Urbex <noreply@{self.domain}>",
                "to": to_emails,
                "subject": subject,
            }

            if text:
                data["text"] = text
            if html:
                data["html"] = html
            if cc:
                data["cc"] = cc
            if bcc:
                data["bcc"] = bcc
            if reply_to:
                data["h:Reply-To"] = reply_to
            if custom_data:
                for key, value in custom_data.items():
                    data[f"v:{key}"] = str(value)

            url = f"{self.base_url}/{self.domain}/messages"
            response = requests.post(url, auth=self.auth, data=data)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"Email sending error: {e}")
            return None

    def send_template_email(
        self,
        to_emails: List[str],
        template_name: str,
        template_variables: Optional[Dict[str, Any]] = None,
        subject: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Send an email using a Mailgun template.
        
        Args:
            to_emails: List of recipient email addresses
            template_name: Name of the template
            template_variables: Variables for template
            subject: Email subject (can be in template)
            from_email: Sender email
            
        Returns:
            API response or None if failed
        """
        if not self.api_key or not self.domain:
            print("Mailgun API key or domain not configured")
            return None

        try:
            data = {
                "from": from_email or f"Urbex <noreply@{self.domain}>",
                "to": to_emails,
                "template": template_name,
            }

            if subject:
                data["subject"] = subject
            if template_variables:
                for key, value in template_variables.items():
                    data[f"v:{key}"] = str(value)

            url = f"{self.base_url}/{self.domain}/messages"
            response = requests.post(url, auth=self.auth, data=data)
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            print(f"Template email sending error: {e}")
            return None

    def send_welcome_email(self, email: str, username: str) -> bool:
        """
        Send a welcome email to new users.
        
        Args:
            email: User's email address
            username: User's username
            
        Returns:
            True if successful, False otherwise
        """
        subject = "Welcome to Urbex!"
        html_content = f"""
        <html>
        <body>
            <h1>Welcome to Urbex, {username}!</h1>
            <p>Thank you for joining our community. We're excited to have you on board!</p>
            <p>Best regards,<br>The Urbex Team</p>
        </body>
        </html>
        """
        
        result = self.send_email(
            to_emails=[email],
            subject=subject,
            html=html_content,
        )
        
        return result is not None

    def send_password_reset_email(self, email: str, reset_token: str) -> bool:
        """
        Send a password reset email.
        
        Args:
            email: User's email address
            reset_token: Password reset token
            
        Returns:
            True if successful, False otherwise
        """
        subject = "Password Reset Request"
        reset_url = f"https://your-app.com/reset-password?token={reset_token}"
        
        html_content = f"""
        <html>
        <body>
            <h1>Password Reset Request</h1>
            <p>You requested a password reset for your Urbex account.</p>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_url}">Reset Password</a>
            <p>If you didn't request this, please ignore this email.</p>
            <p>Best regards,<br>The Urbex Team</p>
        </body>
        </html>
        """
        
        result = self.send_email(
            to_emails=[email],
            subject=subject,
            html=html_content,
        )
        
        return result is not None

    def send_verification_email(self, email: str, verification_code: str) -> bool:
        """
        Send an email verification code.
        
        Args:
            email: User's email address
            verification_code: Verification code
            
        Returns:
            True if successful, False otherwise
        """
        subject = "Email Verification"
        
        html_content = f"""
        <html>
        <body>
            <h1>Email Verification</h1>
            <p>Please verify your email address by entering this code:</p>
            <h2>{verification_code}</h2>
            <p>This code will expire in 24 hours.</p>
            <p>Best regards,<br>The Urbex Team</p>
        </body>
        </html>
        """
        
        result = self.send_email(
            to_emails=[email],
            subject=subject,
            html=html_content,
        )
        
        return result is not None

    def send_contact_form_email(
        self, 
        full_name: str, 
        email: str, 
        phone: str, 
        message: str,
        admin_email: str
    ) -> bool:
        """
        Send contact form notification to admin.
        
        Args:
            full_name: Contact person's full name
            email: Contact person's email
            phone: Contact person's phone
            message: Contact message
            admin_email: Admin email to receive notification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            subject = f"Nuevo mensaje de contacto de {full_name}"
            
            html_content = f"""
            <html>
            <body>
                <h1>Nuevo Mensaje de Contacto</h1>
                <p>Has recibido un nuevo mensaje de contacto desde la landing page:</p>
                
                <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <h2>Información del Contacto:</h2>
                    <p><strong>Nombre completo:</strong> {full_name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Teléfono:</strong> {phone}</p>
                    <p><strong>Mensaje:</strong></p>
                    <div style="background-color: white; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0;">
                        {message.replace(chr(10), '<br>')}
                    </div>
                </div>
                
                <p><strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                
                <hr>
                <p><em>Este mensaje fue enviado automáticamente desde el formulario de contacto de Urbex.</em></p>
            </body>
            </html>
            """
            
            # Enviar email al admin
            admin_result = self.send_email(
                to_emails=[admin_email],
                subject=subject,
                html=html_content,
                reply_to=email,  # Para que el admin pueda responder directamente
            )
            
            if not admin_result:
                print(f"Failed to send admin notification to {admin_email}")
                return False
            
            # Enviar confirmación al usuario
            user_subject = "Gracias por contactarnos - Urbex"
            user_html_content = f"""
            <html>
            <body>
                <h1>¡Gracias por contactarnos!</h1>
                <p>Hola {full_name},</p>
                <p>Hemos recibido tu mensaje y nos pondremos en contacto contigo pronto.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Resumen de tu mensaje:</h3>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Teléfono:</strong> {phone}</p>
                    <p><strong>Mensaje:</strong></p>
                    <div style="background-color: white; padding: 10px; border-left: 3px solid #28a745;">
                        {message[:200]}{'...' if len(message) > 200 else ''}
                    </div>
                </div>
                
                <p>Te responderemos en las próximas 24 horas.</p>
                <p>Saludos,<br>El equipo de Urbex</p>
            </body>
            </html>
            """
            
            user_result = self.send_email(
                to_emails=[email],
                subject=user_subject,
                html=user_html_content,
            )
            
            if not user_result:
                print(f"Failed to send confirmation email to {email}")
                # No fallamos completamente si solo falla la confirmación
                return True
            
            return True
            
        except Exception as e:
            print(f"Error in send_contact_form_email: {str(e)}")
            return False


# Global Mailgun service instance
mailgun_service = MailgunService() 