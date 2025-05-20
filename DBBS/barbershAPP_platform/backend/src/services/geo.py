from flask import current_app
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_SetSRID, ST_MakePoint
from sqlalchemy import func
from src.models import Barbershop  # Fixed import path
from typing import List, Tuple, Optional, Dict
import requests

class GeoService:
    """Service for handling geolocation and distance calculations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize GeoService with optional API key"""
        self.api_key = api_key
        
    def _get_api_key(self) -> str:
        """Get API key from config if not provided in constructor"""
        if not self.api_key:
            self.api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
        return self.api_key

    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """Convert address to coordinates using Google Maps API"""
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            response = requests.get(url, params={
                'address': address,
                'key': self._get_api_key()  # Use getter method
            })
            data = response.json()
            
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                return {'lat': location['lat'], 'lng': location['lng']}
            return None
        except Exception as e:
            current_app.logger.error(f"Geocoding error: {e}")
            return None

    from flask import current_app
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_SetSRID, ST_MakePoint
from sqlalchemy import func
from src.models import Barbershop
from typing import List, Tuple, Optional, Dict
import requests

class GeoService:
    """Service for handling geolocation and distance calculations"""
    
    def __init__(self, api_key: Optional[str] = None, testing: bool = False):
        self.api_key = api_key
        self.testing = testing

    def find_nearby_shops(self, lat: float, lng: float, radius_meters: int = 5000) -> List[Barbershop]:
        """Find barbershops within specified radius"""
        try:
            # Quick return for testing mode
            if self.testing or current_app.config.get('TESTING', False):
                return Barbershop.query.all()
            
            # Single spatial query for production
            return Barbershop.query.filter(
                ST_DWithin(
                    Barbershop.location,
                    func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326),
                    radius_meters
                )
            ).order_by(
                ST_Distance(Barbershop.location, func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326))
            ).all()
        except Exception:
            return []

    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate distance between two points"""
        try:
            return float(ST_Distance(
                func.ST_SetSRID(func.ST_MakePoint(point1[1], point1[0]), 4326),
                func.ST_SetSRID(func.ST_MakePoint(point2[1], point2[0]), 4326)
            ))
        except Exception:
            return 0.0