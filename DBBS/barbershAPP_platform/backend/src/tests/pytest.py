import pytest
from flask import current_app
from src.app import create_app
from src.database.db import db
from src.services.geo import GeoService
from src.services.tasks import QueueService
from flask_cors import CORS
import redis
import logging

logger = logging.getLogger(__name__)

@pytest.mark.usefixtures('app')
class TestServices:
    def test_redis_connection(self, app):
        """Test Redis connection"""
        try:
            r = redis.from_url(app.config['REDIS_URL'])
            assert r.ping() is True
            logger.info("Redis connection successful")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            pytest.fail(f"Redis connection failed: {e}")

    def test_postgis(self, app):
        """Test PostGIS functionality"""
        try:
            with app.app_context():
                result = db.session.execute('SELECT PostGIS_Version()').scalar()
                assert result is not None
                logger.info(f"PostGIS version: {result}")
        except Exception as e:
            logger.error(f"PostGIS test failed: {e}")
            pytest.fail(f"PostGIS test failed: {e}")

    def test_google_maps(self, app):
        """Test Google Maps API"""
        try:
            with app.app_context():
                geo_service = GeoService()
                result = geo_service.geocode_address("1 Main St, Boston, MA")
                assert result is not None
                assert 'lat' in result and 'lng' in result
                logger.info(f"Geocoding successful: {result}")
        except Exception as e:
            logger.error(f"Google Maps API test failed: {e}")
            pytest.fail(f"Google Maps API test failed: {e}")

    def test_queue_service(self, app):
        """Test Queue Service"""
        try:
            with app.app_context():
                result = QueueService.test_connection()
                assert result is True
                logger.info("Queue service connection successful")
        except Exception as e:
            logger.error(f"Queue service test failed: {e}")
            pytest.fail(f"Queue service test failed: {e}")

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://postgres:postgres@localhost:5432/barbershop_test'
    })
    
    with app.app_context():
        db.create_all()
    
    yield app
    
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
