from firebase_admin import messaging # type: ignore
from src.config.messages import NotificationMessages
from typing import Dict, Optional
from logging import logger

class FirebaseMessaging:
    @staticmethod
    def send_bilingual_notification(
        token: str,
        message_type: str,
        variables: Dict[str, str],
        preferred_language: str = 'en'
    ) -> bool:
        """Send notification in user's preferred language"""
        try:
            messages = getattr(NotificationMessages, message_type)
            message_text = messages[preferred_language].format(**variables)
            
            message = messaging.Message(
                notification=messaging.Notification(
                    title="BarbershAPP",
                    body=message_text
                ),
                data={
                    'type': message_type,
                    **variables
                },
                token=token
            )
            
            response = messaging.send(message)
            return True
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return False