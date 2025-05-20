import os
from typing import Dict, Any

class Config:
    # Critical security key - should never use default in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set in environment variables")
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'RENDER_DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Google Maps API configuration
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("No GOOGLE_MAPS_API_KEY set in environment variables")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class RedisConfig:
    # Redis connection settings
    REDIS_CONFIG = {
        'host': os.environ.get('REDIS_HOST', 'localhost'),
        'port': int(os.environ.get('REDIS_PORT', 6379)),
        'db': int(os.environ.get('REDIS_DB', 0)),
        'socket_timeout': 2,
        'decode_responses': True,
        'retry_on_timeout': True
    }

class TestConfig(Config):
    """Test configuration - override parent for testing"""
    TESTING = True
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Test-specific keys
    SECRET_KEY = "test-secret-key"
    GOOGLE_MAPS_API_KEY = "test-maps-key"

class ProductionConfig(Config):
    """Production configuration with strict security"""
    DEBUG = False
    TESTING = False
    # Force HTTPS
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

__all__ = ['Config', 'TestConfig', 'ProductionConfig', 'RedisConfig']