from flask import Blueprint, request, jsonify
from barbershop_platform.backend.src.services.firebase.firebase_messaging import FirebaseMessaging
from src.middleware.firebase_auth import require_firebase_auth
from datetime import datetime
from src.services.subscribers import get_barber_subscribers
from hashlib import sha256
import re

availability_bp = Blueprint('availability', __name__)
messaging = FirebaseMessaging()

def format_phone_number(phone: str) -> str:
    """Format phone number to consistent format"""
    # Remove all non-digits
    cleaned = re.sub(r'\D', '', phone)
    # Ensure it's a valid US number
    if len(cleaned) == 10:
        return f"+1{cleaned}"
    elif len(cleaned) == 11 and cleaned.startswith('1'):
        return f"+{cleaned}"
    raise ValueError("Invalid phone number format")

def hash_phone(phone: str) -> str:
    """Create a secure hash of phone number for ID"""
    return sha256(format_phone_number(phone).encode()).hexdigest()[:16]

@availability_bp.route('/barber/availability', methods=['POST'])
@require_firebase_auth
async def update_availability():
    try:
        data = request.get_json()
        phone = data.get('phone')
        if not phone:
            return jsonify({'error': 'Phone number required'}), 400

        # Generate barber_id from phone
        barber_id = hash_phone(phone)
        
        # Format time slots
        time_slots = ", ".join(data['time_slots'])
        date = datetime.strptime(data['date'], '%Y-%m-%d').strftime('%B %d, %Y')
        
        # Get subscriber tokens from Firestore
        subscribers = await get_barber_subscribers(barber_id)
        
        # Send notifications to all subscribers
        for subscriber in subscribers:
            await messaging.send_bilingual_notification(
                token=subscriber['token'],
                message_type='AVAILABILITY_UPDATE',
                variables={
                    'barber_name': data['barber_name'],
                    'shop_name': data['shop_name'],
                    'date': date,
                    'time_slots': time_slots,
                    'booking_url': f"/book/{barber_id}?date={data['date']}"
                },
                preferred_language=subscriber.get('language', 'en')
            )
        
        return jsonify({
            'success': True,
            'notifications_sent': len(subscribers),
            'barber_id': barber_id  # Return the generated ID for reference
        }), 200
        
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500