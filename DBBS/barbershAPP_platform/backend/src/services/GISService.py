from flask import current_app
import requests
import geojson
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy import text
from src.database.db import db
import logging

logger = logging.getLogger(__name__)

class GISService:
    """Service for handling GIS operations with public endpoints"""
    def __init__(self):
        self.session = requests.Session()
        self.query_url = None
        self.query_params = None
        self.maps_api_key = None

    def init_app(self, app):
        """Initialize the service with Flask app config"""
        self.query_url = app.config['GIS_QUERY_URL']
        self.query_params = app.config['GIS_QUERY_PARAMS']
        self.maps_api_key = app.config['GOOGLE_MAPS_API_KEY']

    def get_businesses_json(self) -> Optional[Dict]:
        """Get businesses in JSON format from public endpoint"""
        url = f"{self.query_url}?{self.query_params}&f=json"
        return self._make_request(url, {})

    def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Make HTTP request with error handling"""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"GIS API request failed: {str(e)}")
            return None

    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """Geocode an address using Google Maps Geocoding API"""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': self.maps_api_key
        }
        
        result = self._make_request(url, params)
        if not result or result.get('status') != 'OK':
            return None
            
        location = result['results'][0]['geometry']['location']
        return {
            'location': {
                'type': 'Point',
                'coordinates': [
                    location['lng'],
                    location['lat']
                ]
            },
            'address': result['results'][0]['formatted_address'],
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def find_nearby_barbershops(self, lat: float, lon: float, radius: int = 5000) -> Optional[Dict[str, Any]]:
        """Find barbershops within radius using public GIS endpoint"""
        params = {
            'where': '1=1',
            'outFields': '*',
            'geometryType': 'esriGeometryPoint',
            'geometry': f"{lon},{lat}",
            'distance': radius,
            'units': 'meters',
            'f': 'json'
        }
        
        result = self._make_request(self.query_url, params)
        if not result or 'features' not in result:
            return None

        return geojson.FeatureCollection([
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [
                        feature['geometry']['x'],
                        feature['geometry']['y']
                    ]
                },
                'properties': {
                    **feature['attributes'],
                    'distance_meters': round(
                        ((feature['geometry']['x'] - lon) ** 2 + 
                         (feature['geometry']['y'] - lat) ** 2) ** 0.5 * 111319.9,
                        2
                    )
                }
            }
            for feature in result['features']
        ])
    
class GeoService:
    # Drive time constants in meters
    DRIVE_TIMES = {
        15: 12500,  # ~15 min drive
        30: 25000,  # ~30 min drive
        45: 37500,  # ~45 min drive
        60: 50000   # ~60 min drive
    }

    @staticmethod
    async def get_shops_by_drive_time(lat: float, lon: float, minutes: int) -> List[Dict]:
        """Get shops within specified drive time radius"""
        try:
            radius = GeoService.DRIVE_TIMES.get(minutes, 25000)
            
            query = text("""
                WITH shops AS (
                    SELECT 
                        s.id,
                        s.name,
                        s.address,
                        s.phone,
                        ST_AsGeoJSON(s.location)::json AS location,
                        ST_Distance(
                            s.location::geography,
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                        ) AS distance
                    FROM barbershops s
                    WHERE ST_DWithin(
                        s.location::geography,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                        :radius
                    )
                )
                SELECT 
                    s.*,
                    EXISTS(
                        SELECT 1 
                        FROM firebase_shop_status fs 
                        WHERE fs.shop_id = s.id AND fs.is_open = true
                    ) as is_open
                FROM shops s
                ORDER BY distance
            """)

            result = await db.session.execute(
                query,
                {"lat": lat, "lon": lon, "radius": radius}
            )
            
            shops = result.mappings().all()
            
            # Fetch real-time data from Firebase
            from firebase_admin import firestore # type: ignore
            db = firestore.client()
            
            # Enhance with real-time data
            enhanced_shops = []
            for shop in shops:
                shop_dict = dict(shop)
                
                # Get real-time queue and availability
                shop_ref = db.collection('shops').document(str(shop['id']))
                shop_data = shop_ref.get().to_dict() or {}
                
                shop_dict.update({
                    'current_queue': shop_data.get('queue_size', 0),
                    'wait_time': shop_data.get('estimated_wait', 0),
                    'available_barbers': shop_data.get('available_barbers', [])
                })
                
                enhanced_shops.append(shop_dict)
            
            return enhanced_shops
            
        except Exception as e:
            logger.error(f"Error in get_shops_by_drive_time: {str(e)}")
            raise