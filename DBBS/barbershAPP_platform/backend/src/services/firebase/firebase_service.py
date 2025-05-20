from firebase_admin import credentials, auth, messaging, firestore, initialize_app #type: ignore
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from flask import current_app

logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self):
        """Initialize Firebase service with credentials"""
        try:
            cred = credentials.Certificate(current_app.config['FIREBASE_CREDENTIALS_PATH'])
            initialize_app(cred)
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Firebase initialization failed: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token"""
        try:
            return auth.verify_id_token(token)
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def create_user(self, email: str, password: str) -> Dict[str, Any]:
        """Create a new Firebase user"""
        try:
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=False
            )
            return {
                'uid': user.uid,
                'email': user.email,
                'created_at': user.user_metadata.creation_timestamp
            }
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            raise

    def send_notification(self, 
                         token: str, 
                         title: str, 
                         body: str, 
                         data: Optional[Dict[str, str]] = None) -> bool:
        """Send push notification to a device"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=token
            )
            response = messaging.send(message)
            logger.info(f"Notification sent: {response}")
            return True
        except Exception as e:
            logger.error(f"Notification failed: {e}")
            return False

    def store_appointment(self, appointment_data: Dict[str, Any]) -> str:
        """Store appointment in Firestore"""
        try:
            doc_ref = self.db.collection('appointments').document()
            appointment_data['created_at'] = firestore.SERVER_TIMESTAMP
            doc_ref.set(appointment_data)
            return doc_ref.id
        except Exception as e:
            logger.error(f"Appointment storage failed: {e}")
            raise

    def get_user_appointments(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all appointments for a user"""
        try:
            docs = self.db.collection('appointments')\
                .where('user_id', '==', user_id)\
                .order_by('date', direction=firestore.Query.DESCENDING)\
                .stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Fetching appointments failed: {e}")
            raise

    def update_appointment_status(self, 
                                appointment_id: str, 
                                status: str, 
                                notify_user: bool = True) -> bool:
        """Update appointment status and optionally notify user"""
        try:
            doc_ref = self.db.collection('appointments').document(appointment_id)
            appointment = doc_ref.get()
            
            if not appointment.exists:
                raise ValueError("Appointment not found")
                
            doc_ref.update({
                'status': status,
                'updated_at': firestore.SERVER_TIMESTAMP
            })

            if notify_user and appointment.get('user_token'):
                self.send_notification(
                    token=appointment.get('user_token'),
                    title="Appointment Update",
                    body=f"Your appointment status has been updated to: {status}",
                    data={'appointment_id': appointment_id}
                )
            
            return True
        except Exception as e:
            logger.error(f"Status update failed: {e}")
            return False

    def delete_user(self, uid: str) -> bool:
        """Delete a Firebase user"""
        try:
            auth.delete_user(uid)
            return True
        except Exception as e:
            logger.error(f"User deletion failed: {e}")
            return False