from .booking import booking_bp
from .shop import shop_bp
from .appointments import appointments_bp
from src.app import create_app
from models import *
from services import *

__version__ = '0.1'
__author__ = 'Your Name'


def register_routes(app):
    """Register all blueprints with unique names"""
    routes = [
        (booking_bp, '/api/booking', 'booking_api'),
        (shop_bp, '/api/shops', 'shop_api'),
        (appointments_bp, '/api/appointments', 'appointments_api')
    ]
    
    for blueprint, url_prefix, name in routes:
        app.register_blueprint(blueprint, url_prefix=url_prefix, name=name)

__all__ = ['register_routes','create_app']