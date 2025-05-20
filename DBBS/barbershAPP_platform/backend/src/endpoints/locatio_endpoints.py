from flask import Blueprint, request, jsonify
from src.services.GISService import GeoService
from src.services.firebase.updates import FirebaseUpdates

location_bp = Blueprint('location', __name__)

@location_bp.route('/nearby', methods=['GET'])
async def get_nearby_shops():
    """Get shops within specified drive time"""
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    drive_time = int(request.args.get('minutes', 30))
    
    # Get PostGIS results
    shops = await GeoService.get_shops_by_drive_time(lat, lon, drive_time)
    
    # Enhance with real-time data
    enhanced_shops = await FirebaseUpdates.enhance_shop_data(shops)
    
    return jsonify({
        'shops': enhanced_shops,
        'drive_time': drive_time,
        'total': len(enhanced_shops)
    })