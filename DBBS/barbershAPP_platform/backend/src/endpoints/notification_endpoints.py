from flask import Blueprint, request, jsonify
import firebase_admin #type: ignore
from firebase_admin import credentials, firestore, messaging #type: ignore
from src.middleware.firebase_auth import require_firebase_auth
from typing import Dict
import logging
logger = logging.getLogger(__name__)
notifications_bp = Blueprint('notifications', __name__)

# Initialize Firebase Admin if not already initialized
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)
admin = firebase_admin
admin.db = firestore.client()
notifications_bp = Blueprint('notifications', __name__)

NOTIFICATION_TEMPLATES: Dict[str, Dict[str, Dict[str, str]]] = {
    'QUEUE_UPDATE': {
        'en': {
            'title': 'Queue Update',
            'body': 'Your turn is coming up! Estimated wait time: {wait_time} minutes'
        },
        'es': {
            'title': 'Actualización de Cola',
            'body': '¡Tu turno se acerca! Tiempo estimado de espera: {wait_time} minutos'
        }
    },
    'APPOINTMENT_REMINDER': {
        'en': {
            'title': 'Appointment Reminder',
            'body': 'Your appointment with {barber_name} is in {time_until} minutes'
        },
        'es': {
            'title': 'Recordatorio de Cita',
            'body': 'Tu cita con {barber_name} es en {time_until} minutos'
        }
    }
}

@notifications_bp.route('/notifications/subscribe', methods=['POST'])
@require_firebase_auth
async def subscribe_to_notifications():
    """Subscribe user to push notifications"""
    try:
        user_id = request.user['uid']
        token = request.json.get('token')
        topics = request.json.get('topics', [])
        
        # Store token in user's profile
        admin.db.collection('users').document(user_id).update({
            'fcm_token': token,
            'notification_topics': topics
        })
        
        # Subscribe to topics
        for topic in topics:
            messaging.subscribe_to_topic(token, topic)
            
        return jsonify({'status': 'subscribed'}), 200
    except Exception as e:
        logger.error(f"Error subscribing to notifications: {e}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/notifications/send', methods=['POST'])
@require_firebase_auth
async def send_notification():
    """Send notification to specific user"""
    try:
        recipient_id = request.json.get('user_id')
        notification_type = request.json.get('type')
        language = request.json.get('language', 'en')
        variables = request.json.get('variables', {})
        
        # Get user's FCM token
        user_doc = admin.db.collection('users').document(recipient_id).get()
        if not user_doc.exists:
            return jsonify({'error': 'User not found'}), 404
            
        user_data = user_doc.to_dict()
        token = user_data.get('fcm_token')
        
        if not token:
            return jsonify({'error': 'User has no FCM token'}), 400
            
        # Get notification template
        template = NOTIFICATION_TEMPLATES.get(notification_type, {}).get(language, {})
        if not template:
            return jsonify({'error': 'Invalid notification type or language'}), 400
            
        # Format notification
        message = messaging.Message(
            notification=messaging.Notification(
                title=template['title'],
                body=template['body'].format(**variables)
            ),
            token=token
        )
        
        # Send notification
        response = messaging.send(message)
        return jsonify({'message_id': response}), 200
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return jsonify({'error': str(e)}), 500