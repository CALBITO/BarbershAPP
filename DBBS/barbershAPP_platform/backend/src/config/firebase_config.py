import firebase_admin # type: ignore
from firebase_admin import credentials, messaging # type: ignore
import os
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class FirebaseConfig:
    _instance: Optional[firebase_admin.App] = None
    _credentials_path: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'config',
        'serviceAccountKey.json'
    )

    @classmethod
    def init_app(cls):
        """Initialize Firebase Admin SDK as singleton"""
        if cls._instance is None:
            try:
                if not os.path.exists(cls._credentials_path):
                    raise ValueError(f"Firebase credentials not found at {cls._credentials_path}")
                
                cred = credentials.Certificate(cls._credentials_path)
                cls._instance = firebase_admin.initialize_app(cred, {
                    'projectId': os.getenv('FIREBASE_PROJECT_ID'),
                    'storageBucket': f"{os.getenv('FIREBASE_PROJECT_ID')}.appspot.com"
                })
                logger.info("Firebase Admin SDK initialized successfully")
            except Exception as e:
                logger.error(f"Firebase initialization failed: {str(e)}")
                raise
        return cls._instance

    @classmethod
    def get_app(cls):
        """Get Firebase Admin app instance"""
        if cls._instance is None:
            cls.init_app()
        return cls._instance

    @classmethod
    def send_notification(cls, token: str, title: str, body: str, data: Optional[Dict] = None):
        """Send Firebase Cloud Message"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            messaging.send(message)
            logger.info(f"Notification sent successfully to {token}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False