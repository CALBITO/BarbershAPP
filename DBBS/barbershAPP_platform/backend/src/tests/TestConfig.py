class TestConfig:
    """Test configuration settings"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test-secret"
    SECRET_KEY = "test-app-secret"
    WTF_CSRF_ENABLED = False
    
    # Mail settings
    MAIL_SUPPRESS_SEND = True
    
    # Custom test settings
    TEST_USER_EMAIL = "test@example.com"
    TEST_USER_PASSWORD = "test123"
    
    # API settings
    API_PREFIX = "/api"
    
    # SQLite specific settings
    SQLITE_FOREIGN_KEYS = True