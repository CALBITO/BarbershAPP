from functools import wraps
from flask import request, abort, current_app
import hmac
import hashlib

def require_api_key(f):
    """Decorator to check for valid API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config['API_KEY']:
            abort(401)
        return f(*args, **kwargs)
    return decorated

def verify_webhook_signature(secret_key):
    """Verify webhook signatures"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            signature = request.headers.get('X-Hub-Signature')
            if not signature:
                abort(403)

            expected = hmac.new(
                secret_key.encode('utf-8'),
                request.data,
                hashlib.sha1
            ).hexdigest()

            if not hmac.compare_digest(f"sha1={expected}", signature):
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator