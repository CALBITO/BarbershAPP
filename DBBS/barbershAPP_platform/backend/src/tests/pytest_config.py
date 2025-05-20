import pytest
from flask import current_app
from src.services.geo import GeoService
from src.services.tasks import QueueService
import redis

def test_redis_connection():
    """Test Redis connection"""
    try:
        r = redis.from_url(current_app.config['REDIS_URL'])
        r.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False

def test_postgis():
    """Test PostGIS functionality"""
    try:
        result = current_app.db.session.execute('SELECT PostGIS_Version()')
        return bool(result.scalar())
    except Exception as e:
        print(f"PostGIS test failed: {e}")
        return False

def test_google_maps():
    """Test Google Maps API"""
    try:
        geo_service = GeoService()
        result = geo_service.geocode_address("1 Main St, Boston, MA")
        return bool(result and 'lat' in result)
    except Exception as e:
        print(f"Google Maps API test failed: {e}")
        return False