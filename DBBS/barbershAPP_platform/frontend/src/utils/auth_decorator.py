from functools import wraps
from flask import request, jsonify, current_app
from .jwt_mng import JWTManager

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        # Check if token exists in header
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'No authorization token provided'
            }), 401
            
        token = auth_header.split(' ')[1]
        
        # Verify token
        user_data = JWTManager.verify_token(token)
        if 'error' in user_data:
            return jsonify({
                'success': False,
                'error': user_data['error']
            }), 401
            
        # Add user data to request context
        request.user = user_data
        return f(*args, **kwargs)
    
    return decorated