from flask import Flask
from datetime import timedelta

def init_app(app: Flask):
    """Initialize configuration for the Flask application"""
    app.config.update(
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=1),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
        JWT_ALGORITHM='HS256'
    )

    # Load environment variables
    if app.config['JWT_SECRET_KEY'] is None:
        app.config['JWT_SECRET_KEY'] = app.config.get('SECRET_KEY')

    return app