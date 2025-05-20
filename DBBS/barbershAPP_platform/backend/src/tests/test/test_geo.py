import pytest
from src.services.geo import GeoService
from src.models import Barbershop
from flask import Flask

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['GOOGLE_MAPS_API_KEY'] = 'test-key'
    return app

@pytest.fixture
def geo_service():
    """Create GeoService instance for testing"""
    return GeoService(testing=True)

def test_find_nearby_shops(app, geo_service):
    """Test nearby shops functionality"""
    with app.app_context():
        # Test coordinates (Boston, MA)
        shops = geo_service.find_nearby_shops(42.3601, -71.0589)
        
        # Basic assertions
        assert isinstance(shops, list)
        assert all(isinstance(shop, Barbershop) for shop in shops)