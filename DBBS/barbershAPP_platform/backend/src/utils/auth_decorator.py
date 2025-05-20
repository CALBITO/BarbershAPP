from functools import wraps
from flask import request, jsonify
from src.utils.jwt_mng import JWTManager  # Fixed import path

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
            
        user_data = JWTManager.verify_token(token)
        if 'error' in user_data:
            return jsonify({'error': user_data['error']}), 401
            
        request.user = user_data
        return f(*args, **kwargs)
    return decorated
