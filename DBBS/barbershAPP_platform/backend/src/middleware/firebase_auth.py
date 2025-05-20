from functools import wraps
from flask import request, jsonify
from barbershop_platform.backend.src.services.firebase.firebase_service import FirebaseService

def require_firebase_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authentication token'}), 401

        token = auth_header.replace('Bearer ', '')
        decoded_token = FirebaseService.verify_token(token)
        
        if not decoded_token:
            return jsonify({'error': 'Invalid authentication token'}), 401

        request.user = decoded_token
        return f(*args, **kwargs)
    return decorated_function

def verify_phone_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        decoded_token = require_firebase_auth(f)
        if not decoded_token.get('phone_number'):
            return jsonify({'error': 'Phone verification required'}), 403
        return f(*args, **kwargs)
    return decorated_function