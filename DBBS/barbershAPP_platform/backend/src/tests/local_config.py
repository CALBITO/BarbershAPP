class TestConfig:
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret"
    GOOGLE_MAPS_API_KEY = "test-key"
    REDIS_URL = "memory://"
    DEBUG = True