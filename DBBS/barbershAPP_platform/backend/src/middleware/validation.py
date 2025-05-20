from functools import wraps
from typing import Callable, Any, Dict, Optional
from flask import request, jsonify, current_app
from marshmallow import Schema, ValidationError # type: ignore
import re

def validate_request(schema: Schema) -> Callable:
    """Validate request data against schema"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            try:
                if request.is_json:
                    data = schema.load(request.get_json())
                elif request.form:
                    data = schema.load(request.form)
                else:
                    return jsonify({"error": "No data provided"}), 400
                
                return f(*args, data=data, **kwargs)
            except ValidationError as err:
                return jsonify({"error": "Validation error", "messages": err.messages}), 400
        return decorated_function
    return decorator

def validate_api_key(f: Callable) -> Callable:
    """Validate API key in request headers"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != current_app.config['API_KEY']:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

def validate_pagination(f: Callable) -> Callable:
    """Validate and normalize pagination parameters"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            if page < 1 or per_page < 1 or per_page > 100:
                return jsonify({
                    "error": "Invalid pagination parameters",
                    "message": "Page must be >= 1, per_page must be between 1 and 100"
                }), 400
                
            return f(*args, page=page, per_page=per_page, **kwargs)
        except ValueError:
            return jsonify({
                "error": "Invalid pagination parameters",
                "message": "Page and per_page must be integers"
            }), 400
    return decorated_function

def validate_coordinates(f: Callable) -> Callable:
    """Validate geographic coordinates"""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            lat = float(request.args.get('lat', 0))
            lng = float(request.args.get('lng', 0))
            
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return jsonify({
                    "error": "Invalid coordinates",
                    "message": "Latitude must be between -90 and 90, longitude between -180 and 180"
                }), 400
                
            return f(*args, lat=lat, lng=lng, **kwargs)
        except ValueError:
            return jsonify({
                "error": "Invalid coordinates",
                "message": "Latitude and longitude must be numbers"
            }), 400
    return decorated_function

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, phone))

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))