from datetime import datetime
import jwt
from flask import current_app
from backend.src.config.jwt_config import JWT_CONFIG

class JWTManager:
    @staticmethod
    def create_token(user_data):
        """Create a new JWT token"""
        payload = {
            'user_id': user_data.get('id'),
            'email': user_data.get('email'),
            'exp': datetime.utcnow() + JWT_CONFIG['ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.utcnow()
        }
        return jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm=JWT_CONFIG['ALGORITHM']
        )

    @staticmethod
    def verify_token(token):
        """Verify and decode a JWT token"""
        try:
            return jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=[JWT_CONFIG['ALGORITHM']]
            )
        except jwt.ExpiredSignatureError:
            return {'error': 'Token has expired'}
        except jwt.InvalidTokenError:
            return {'error': 'Invalid token'}