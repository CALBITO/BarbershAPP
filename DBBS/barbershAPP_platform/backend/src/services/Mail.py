"""Email service module"""
from flask import current_app, render_template
from src.config.Mail import Mail
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class MailService:
    @staticmethod
    def send_email(
        subject: str,
        recipients: List[str],
        body: str,
        html: Optional[str] = None,
        sender: Optional[str] = None
    ) -> bool:
        """Send email to recipients"""
        try:
            Mail.send_message(
                subject=subject,
                recipients=recipients,
                body=body,
                html=html,
                sender=sender or current_app.config['MAIL_DEFAULT_SENDER']
            )
            logger.info(f"Email sent successfully to {recipients}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_appointment_confirmation(
        email: str,
        appointment_details: dict
    ) -> bool:
        """Send appointment confirmation email"""
        subject = "Appointment Confirmation"
        body = render_template(
            'emails/appointment_confirmation.txt',
            **appointment_details
        )
        html = render_template(
            'emails/appointment_confirmation.html',
            **appointment_details
        )
        return MailService.send_email(subject, [email], body, html)