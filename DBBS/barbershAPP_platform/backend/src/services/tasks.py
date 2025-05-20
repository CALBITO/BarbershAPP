from flask import current_app
from celery import Celery
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask_mail import Message
from twilio.rest import Client
from src.models import Appointment, Barbershop, Queue 
import os

celery = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL'))

from flask import current_app
import redis
from datetime import datetime
from typing import Optional, Dict, Any

class QueueService:
    """Service for managing barbershop queues"""
    
    def __init__(self):
        self.redis_client = None
        self.config = {}

    def init_app(self, app):
        """Initialize service with Flask app config"""
        self.config = {
            'REDIS_URL': app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
            'QUEUE_PREFIX': app.config.get('QUEUE_PREFIX', 'barbershop:'),
            'DEFAULT_TTL': app.config.get('QUEUE_TTL', 3600)
        }
        self.redis_client = redis.from_url(self.config['REDIS_URL'])

    def join_queue(self, shop_id: int, user_id: int) -> Optional[int]:
        """Add user to shop queue"""
        if not self.redis_client:
            raise RuntimeError("QueueService not initialized")
        
        queue_key = f"{self.config['QUEUE_PREFIX']}shop:{shop_id}:queue"
        position = self.redis_client.rpush(queue_key, user_id)
        return position

    def get_queue_status(self, shop_id: int) -> Dict[str, Any]:
        """Get queue status for a shop"""
        if not self.redis_client:
            raise RuntimeError("QueueService not initialized")
            
        queue_key = f"{self.config['QUEUE_PREFIX']}shop:{shop_id}:queue"
        queue_length = self.redis_client.llen(queue_key)
        return {
            'shop_id': shop_id,
            'queue_length': queue_length,
            'timestamp': datetime.utcnow().isoformat()
        }

# Create singleton instance
queue_service = QueueService()

@celery.task
def send_notification(appointment_id: int, notification_type: str = 'email') -> bool:
        """Send notification via email or SMS"""
        try:
            with current_app.app_context():
                appointment = Appointment.query.get(appointment_id)
                if not appointment:
                    return False
                
                message = f'Your appointment is confirmed for {appointment.appointment_datetime}'
                
                if notification_type == 'email' and appointment.client_email:
                    msg = Message(
                        'Appointment Confirmation',
                        recipients=[appointment.client_email],
                        body=message
                    )
                    current_app.mail.send(msg)
                    return True
                
                elif notification_type == 'sms' and appointment.client_phone:
                    client = Client(
                        os.getenv('TWILIO_ACCOUNT_SID'),
                        os.getenv('TWILIO_AUTH_TOKEN')
                    )
                    client.messages.create(
                        body=message,
                        from_=os.getenv('TWILIO_PHONE_NUMBER'),
                        to=appointment.client_phone
                    )
                    return True
                    
                return False
        except Exception as e:
            current_app.logger.error(f"Error sending {notification_type} notification: {e}")
            return False
@celery.task
def cleanup_old_queues():
        """Remove queue entries older than 24 hours"""
        try:
            with current_app.app_context():
                yesterday = datetime.utcnow() - timedelta(days=1)
                Queue.query.filter(Queue.last_updated < yesterday).delete()
                current_app.db.session.commit()
                return True
        except Exception as e:
            current_app.logger.error(f"Error cleaning up queues: {e}")
            return False