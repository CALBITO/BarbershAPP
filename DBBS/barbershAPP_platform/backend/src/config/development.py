from .default import Config

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/barbershop_db'
    REDIS_URL = 'redis://localhost:6379/0'
    JWT_SECRET_KEY = 'dev-jwt-key'