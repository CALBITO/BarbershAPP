from datetime import timedelta

JWT_CONFIG = {
    'ACCESS_TOKEN_EXPIRES': timedelta(hours=1),
    'REFRESH_TOKEN_EXPIRES': timedelta(days=30),
    'ALGORITHM': 'HS256',
    'SECRET_KEY': None  # Will be loaded from environment
}