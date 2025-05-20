from flask import Blueprint, jsonify, request
from src.utils import require_auth, JWTManager
from flask import Blueprint, request, jsonify
from database.db import FirestoreService
from barbershop_platform.backend.src.services.firebase.firebase_messaging import FirebaseMessaging
from src.middleware.firebase_auth import require_firebase_auth

appointments_bp = Blueprint('appointments', __name__)
db_service = FirestoreService()
messaging_service = FirebaseMessaging()

@appointments_bp.route('/appointments', methods=['POST'])
@require_firebase_auth
def create_appointment():
    try:
        data = request.get_json()
        appointment_id = db_service.create_appointment(data)
        
        # Send notification
        messaging_service.send_appointment_notification(
            token=data['user_token'],
            appointment={'id': appointment_id, **data}
        )
        
        return jsonify({
            'success': True,
            'appointment_id': appointment_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/test-auth', methods=['GET'])
@require_auth
def test_auth():
    """Test endpoint for authentication"""
    return jsonify({
        'success': True,
        'message': 'Authentication successful',
        'user': request.user
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()
    # Add login logic here
    return jsonify({'message': 'Login endpoint'})