from datetime import datetime, timedelta
import jwt
from flask import current_app

class JWTManager:
    @staticmethod
    def create_token(user_data: dict, expires_delta: timedelta = None) -> str:
        """Create a new JWT token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=1)
            
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'exp': datetime.utcnow() + expires_delta,
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}